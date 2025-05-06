# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
import calendar
import logging

_logger = logging.getLogger(__name__)

class AttendanceBonusRecord(models.Model):
    _name = 'attendance.bonus.record'
    _description = 'Attendance Bonus Record'
    _order = 'month desc, employee_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade',
        index=True
    )
    month = fields.Char(string='Month (YYYY-MM)', required=True, index=True)
    is_eligible = fields.Boolean(string='Eligible for Bonus', default=False)
    reason = fields.Text(string='Reason')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='employee_id.company_id',
        store=True,
        readonly=True
    )

    _sql_constraints = [
        ('employee_month_uniq', 'unique(employee_id, month, company_id)',
         'Bonus eligibility record already exists for this employee and month!')
    ]

    @api.model
    def _get_last_month_dates(self):
        today = fields.Date.context_today(self)
        last_day_prev_month = today.replace(day=1) - relativedelta(days=1)
        first_day_prev_month = last_day_prev_month.replace(day=1)
        return first_day_prev_month, last_day_prev_month

    @api.model
    def calculate_attendance_bonus(self, target_date_str=None):
        _logger.info("Starting Attendance Bonus Calculation cron job.")

        if target_date_str:
            try:
                target_date = fields.Date.from_string(target_date_str)
                end_date = target_date.replace(day=1) - relativedelta(days=1)
                start_date = end_date.replace(day=1)
            except:
                _logger.error("Invalid target_date_str format: %s. Use YYYY-MM-DD.", target_date_str)
                return
        else:
            start_date, end_date = self._get_last_month_dates()

        month_str = start_date.strftime('%Y-%m')
        _logger.info(f"Calculating bonus eligibility for month: {month_str} ({start_date} to {end_date})")

        employees = self.env['hr.employee'].search([('active', '=', True)])
        if not employees:
            _logger.info("No active employees found to process.")
            return

        processed_count = 0
        eligible_count = 0
        for employee in employees:
            existing_record = self.search([
                ('employee_id', '=', employee.id),
                ('month', '=', month_str),
            ], limit=1)

            eligible, reason = self._check_employee_eligibility(employee, start_date, end_date)

            vals = {
                'employee_id': employee.id,
                'month': month_str,
                'is_eligible': eligible,
                'reason': reason,
            }

            if not existing_record:
                self.create(vals)
                _logger.debug(f"Created bonus record for {employee.name} ({month_str}): Eligible={eligible}")
            elif existing_record.is_eligible != eligible or existing_record.reason != reason:
                existing_record.write(vals)
                _logger.debug(f"Updated bonus record for {employee.name} ({month_str}): Eligible={eligible}")

            processed_count += 1
            if eligible:
                eligible_count += 1

        _logger.info(f"Finished Attendance Bonus Calculation for {month_str}. Processed: {processed_count}, Eligible: {eligible_count}.")

    def _check_employee_eligibility(self, employee, start_date, end_date):
        """
        Checks a single employee's eligibility for the bonus during the given period.
        Uses configured allowed leave types.
        Returns: (Boolean: is_eligible, String: reason)
        """
        self.ensure_one()
        company_id = employee.company_id.id or self.env.company.id
        if not company_id:
            _logger.warning(
                f"Could not determine company for employee {employee.name} (ID: {employee.id}). Skipping eligibility check.")
            return False, _("Cannot determine employee company.")

        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', datetime.combine(start_date, time.min)),
            ('check_in', '<=', datetime.combine(end_date, time.max)),
        ])

        missed_checkout = attendances.filtered(lambda att: not att.check_out)
        if missed_checkout:
            return False, _("Missed check-out(s) recorded during the period.")

        if not attendances:
            return False, _("No attendance records found for the period.")

        allowed_leave_type_ids = self.env['attendance.bonus.config']._get_allowed_leave_types(company_id)

        if allowed_leave_type_ids is None:  # Explicit check if _get_allowed_leave_types was changed to return None
            _logger.warning(
                f"Attendance Bonus configuration not found for company ID {company_id}. Defaulting to NO leaves allowed.")
            allowed_leave_type_ids = []
        elif not allowed_leave_type_ids:
            _logger.info(f"No leave types configured as allowed for bonus in company ID {company_id}.")

        # Fetch validated leaves that overlap with the period.
        leaves = self.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),
            ('date_from', '<=', datetime.combine(end_date, time.max)),
            ('date_to', '>=', datetime.combine(start_date, time.min)),
        ])

        # Find any leaves whose type is NOT in the list of allowed types
        disqualifying_leaves = leaves.filtered(
            lambda l: l.holiday_status_id.id not in allowed_leave_type_ids
        )

        if disqualifying_leaves:
            leave_names = ", ".join(
                list(set(disqualifying_leaves.mapped('holiday_status_id.name'))))
            reason = _("Disqualifying time off taken: %s") % leave_names
            _logger.debug(f"Employee {employee.name} disqualified due to leaves: {leave_names}")
            return False, reason

        # If all checks passed
        return True, _("Perfect Attendance based on checks.")

    def action_recalculate_bonus(self):
        if not self.env.user.has_group('attendance_bonus_check.group_attendance_bonus_manager'):
            raise UserError(_("You do not have permission to recalculate bonus eligibility."))

        for record in self:
            try:
                month_date = fields.Date.from_string(record.month + '-01')
                start_date = month_date.replace(day=1)
                days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
                end_date = start_date.replace(day=days_in_month)

                eligible, reason = self._check_employee_eligibility(record.employee_id, start_date, end_date)
                record.write({
                    'is_eligible': eligible,
                    'reason': reason,
                })
                _logger.info(f"Manually recalculated bonus for {record.employee_id.name} for {record.month}. Eligible={eligible}")
            except Exception as e:
                _logger.error(f"Error recalculating bonus for record {record.id}: {e}")
