# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# No need for UserError, datetime, relativedelta unless used elsewhere
import logging

_logger = logging.getLogger(__name__)

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # This field determines if the bonus rule condition is met.
    # It is computed based on the existence of a valid attendance.bonus.record.
    has_perfect_attendance_bonus = fields.Boolean(
        string='Has Perfect Attendance Bonus Eligibility',
        compute='_compute_perfect_attendance_bonus_eligibility',
        store=True, # Store the result for performance and reliability
        help="Technically computed field. True if the employee is eligible for the Perfect Attendance Bonus for the relevant period."
    )

    # This field provides a direct link to the eligibility record for traceability.
    # It's not strictly required for the calculation but useful for debugging/auditing.
    attendance_bonus_record_id = fields.Many2one(
        'attendance.bonus.record', # Correct model name
        string='Attendance Bonus Record Reference',
        compute='_compute_perfect_attendance_bonus_eligibility',
        store=True, # Store the result
        help="Reference to the attendance bonus eligibility record checked for this payslip period."
    )

    @api.depends('employee_id', 'date_from', 'state') # Recompute if employee/date changes or slip resets
    def _compute_perfect_attendance_bonus_eligibility(self):
        """
        Check if the employee has a valid 'attendance.bonus.record' for the
        month corresponding to the payslip's date_from.
        """
        for payslip in self:
            # Reset values
            payslip.has_perfect_attendance_bonus = False
            payslip.attendance_bonus_record_id = False

            # Ensure we have the necessary data
            if not payslip.employee_id or not payslip.date_from or payslip.state == 'cancel':
                continue

            # Determine the month (YYYY-MM) the payslip primarily covers
            # Using date_from is usually sufficient for monthly payroll
            payslip_month_str = fields.Date.from_string(payslip.date_from).strftime('%Y-%m')

            # Search for the corresponding eligibility record from the first module
            # Ensure the record exists and indicates eligibility (is_eligible = True)
            bonus_record = self.env['attendance.bonus.record'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('month', '=', payslip_month_str),
                ('is_eligible', '=', True),
                # Optional: Add company check if needed, though employee_id usually implies company
                # ('company_id', '=', payslip.company_id.id)
            ], limit=1)

            if bonus_record:
                payslip.has_perfect_attendance_bonus = True
                payslip.attendance_bonus_record_id = bonus_record.id
                _logger.debug(f"Payslip {payslip.number or payslip.id}: Found eligible bonus record {bonus_record.id} for employee {payslip.employee_id.name} for month {payslip_month_str}.")
            else:
                 _logger.debug(f"Payslip {payslip.number or payslip.id}: No eligible bonus record found for employee {payslip.employee_id.name} for month {payslip_month_str}.")


    # Removed _compute_bonus_amount - The salary rule handles the amount calculation.
    # Removed _get_base_local_dict - The payslip object is available in the rule context.

    # Keep compute_sheet override to ensure eligibility is checked before rule computation
    def compute_sheet(self):
        # Ensure eligibility is computed *before* salary rules run
        self._compute_perfect_attendance_bonus_eligibility()
        return super(HrPayslip, self).compute_sheet()

    # Optional: Override create if you generate payslips programmatically
    # and need the eligibility computed immediately. Often compute_sheet is sufficient.
    # @api.model
    # def create(self, vals):
    #     res = super(HrPayslip, self).create(vals)
    #     res._compute_perfect_attendance_bonus_eligibility()
    #     return res