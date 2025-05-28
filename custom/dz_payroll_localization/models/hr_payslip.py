import datetime
import logging
from collections import defaultdict

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_attendance_worked_hours_per_day(self):
        """
        Calculates total worked hours per day based on hr.attendance records
        within the payslip period for the payslip's employee.
        Returns: dict {date_object: worked_hours_float}
        """
        self.ensure_one()
        worked_hours_by_day = defaultdict(float)

        if not self.employee_id or not self.date_from or not self.date_to:
            return worked_hours_by_day

        # Define the search domain for attendances
        domain = [
            ('employee_id', '=', self.employee_id.id),
            ('check_in', '>=', datetime.datetime.combine(self.date_from, datetime.time.min)),
            ('check_in', '<=', datetime.datetime.combine(self.date_to, datetime.time.max)),
            ('check_out', '!=', False)  # Only consider completed attendances
        ]
        attendances = self.env['hr.attendance'].search(domain)

        for att in attendances:
            # hr.attendance.worked_hours is a float representing hours
            day_date = att.check_in.date()  # Group by the date part of check_in
            worked_hours_by_day[day_date] += att.worked_hours

        return worked_hours_by_day

    def _calculate_and_create_missing_hours_input(self):
        """
        Calculates total missing hours for the payslip period and creates
        or updates an hr.payslip.input line with the deduction amount.
        """
        self.ensure_one()
        total_missing_hours = 0.0
        standard_hours_per_day = 8.0  # Standard daily hours
        penalty_per_hour = 100.0  # DZD per missing hour (hardcoded for Stage 1)

        worked_hours_per_day = self._get_attendance_worked_hours_per_day()

        # Iterate through days where attendance was recorded
        for day, hours_worked in worked_hours_per_day.items():
            if hours_worked < standard_hours_per_day:
                missing_on_day = standard_hours_per_day - hours_worked
                total_missing_hours += missing_on_day

        if total_missing_hours > 0:
            total_deduction_amount = total_missing_hours * penalty_per_hour

            input_type_code = 'MISSING_HOURS_DED_AMOUNT'
            input_type = self.env['hr.payslip.input.type'].search([('code', '=', input_type_code)], limit=1)

            if not input_type:
                _logger.error(
                    f"Payslip Input Type with code '{input_type_code}' not found. "
                    f"Cannot create missing hours deduction input for payslip {self.number}."
                )
                # Optional: Raise UserError if this input type is critical
                # raise UserError(_("Configuration Error: Payslip Input Type '%s' not found.") % input_type_code)
                return

            # Check if an input line for this type already exists
            existing_input = self.input_line_ids.filtered(
                lambda x: x.input_type_id.id == input_type.id
            )

            if existing_input:
                existing_input.write({'amount': total_deduction_amount})
                _logger.info(
                    f"Updated MISSING_HOURS_DED_AMOUNT input to {total_deduction_amount} for payslip {self.number}"
                )
            else:
                self.env['hr.payslip.input'].create({
                    'payslip_id': self.id,
                    'input_type_id': input_type.id,
                    'amount': total_deduction_amount,
                    'contract_id': self.contract_id.id,  # Required by om_hr_payroll
                })
                _logger.info(
                    f"Created MISSING_HOURS_DED_AMOUNT input with {total_deduction_amount} for payslip {self.number}"
                )
        else:
            # If no missing hours, ensure any pre-existing input for this is zeroed or removed
            input_type_code = 'MISSING_HOURS_DED_AMOUNT'
            input_type = self.env['hr.payslip.input.type'].search([('code', '=', input_type_code)], limit=1)
            if input_type:
                existing_input = self.input_line_ids.filtered(
                    lambda x: x.input_type_id.id == input_type.id
                )
                if existing_input:
                    existing_input.write({'amount': 0.0})  # Or existing_input.unlink() if preferred

    def compute_sheet(self):
        """
        Override to inject missing hours calculation before computing lines.
        """
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
            # Calculate and create/update the missing hours input line
            try:
                payslip._calculate_and_create_missing_hours_input()
            except Exception as e:
                _logger.error(f"Error calculating missing hours deduction for payslip {payslip.number}: {e}")
                # Depending on policy, you might want to raise the error or allow payslip computation to continue
                # raise UserError(_("Could not calculate missing hours deduction: %s") % e)

        # Call the original compute_sheet from om_hr_payroll (or its parent)
        return super(HrPayslip, self).compute_sheet()
