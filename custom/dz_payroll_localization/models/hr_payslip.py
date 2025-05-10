from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, time
import pytz  # For timezone handling


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_worked_hours_on_day(self, employee, date_day, employee_tz):
        """
        Calculates total worked hours for a given employee on a specific day.
        Considers attendances where check_in is on date_day.
        """
        # Convert date_day to datetime objects for start and end of day in UTC for querying
        # hr.attendance stores check_in/check_out in UTC
        day_start_naive = datetime.combine(date_day, time.min)
        day_end_naive = datetime.combine(date_day, time.max)

        day_start_aware_local = employee_tz.localize(day_start_naive, is_dst=None)
        day_end_aware_local = employee_tz.localize(day_end_naive, is_dst=None)

        day_start_utc = day_start_aware_local.astimezone(pytz.utc)
        day_end_utc = day_end_aware_local.astimezone(pytz.utc)

        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', day_start_utc),
            ('check_in', '<=', day_end_utc),  # Check-in must be on the given day
            ('check_out', '!=', False)  # Must have a check-out
        ])

        worked_hours = sum(att.worked_hours for att in attendances)
        return worked_hours

    def _calculate_missing_hours_deduction_value(self):
        """
        Calculates the total deduction amount for missing hours for the payslip.
        `self` is a single payslip record.
        """
        if not self.employee_id or not self.date_from or not self.date_to or not self.contract_id:
            return 0.0

        # Get penalty per hour from company settings or global config
        # Using company_id.missing_hour_penalty_amount as defined in res.config.settings
        penalty_per_hour = self.company_id.missing_hour_penalty_amount
        # If using config_parameter:
        # penalty_per_hour = float(self.env['ir.config_parameter'].sudo().get_param(
        #     'dz_payroll_localization.missing_hour_penalty_amount', default=100.0
        # ))

        if penalty_per_hour <= 0:
            return 0.0

        total_missing_hours = 0.0
        required_hours_per_day = 8.0  # As per requirement

        current_date = self.date_from
        employee = self.employee_id
        employee_calendar = employee.resource_calendar_id

        if not employee_calendar:
            # Potentially log a warning or raise error if calendar is essential
            # For now, skip if no calendar, or apply a default (e.g., Mon-Fri)
            # This example skips deduction if no calendar is set.
            return 0.0

        # Determine timezone for calendar operations
        employee_tz_str = employee.tz or employee_calendar.tz or self.env.user.tz or 'UTC'
        try:
            employee_pytz = pytz.timezone(employee_tz_str)
        except pytz.exceptions.UnknownTimeZoneError:
            employee_pytz = pytz.utc  # Fallback to UTC

        while current_date <= self.date_to:
            is_working_day = False

            # Convert current_date to datetime objects in employee's timezone for _work_intervals_batch
            day_dt_start_naive = datetime.combine(current_date, time.min)
            day_dt_end_naive = datetime.combine(current_date, time.max)

            # Localize naive datetimes
            day_dt_start_aware_local = employee_pytz.localize(day_dt_start_naive, is_dst=None)
            day_dt_end_aware_local = employee_pytz.localize(day_dt_end_naive, is_dst=None)

            # _work_intervals_batch expects aware datetimes.
            # It considers resource specific leaves as well.
            # The method returns intervals in UTC.
            # We pass the employee's resource, which is employee.resource_id
            work_intervals = employee_calendar._work_intervals_batch(
                day_dt_start_aware_local, day_dt_end_aware_local, resources=employee.resource_id, compute_leaves=True
            )[employee.resource_id.id]

            if work_intervals:  # If there are any work intervals, it's a working day
                is_working_day = True

            if is_working_day:
                worked_hours_today = self._get_worked_hours_on_day(employee, current_date, employee_pytz)

                if worked_hours_today < required_hours_per_day:
                    missing_hours_today = required_hours_per_day - worked_hours_today
                    if missing_hours_today > 0:  # Ensure no negative missing hours
                        total_missing_hours += missing_hours_today

            current_date += timedelta(days=1)

        total_deduction_amount = total_missing_hours * penalty_per_hour
        return total_deduction_amount

    def _get_localdict(self, rules_dict):
        """
        Override to calculate and write the MISSING_HOURS input amount
        before the rules are evaluated.
        """
        # `self` is the payslip record.
        # Calculate the deduction amount for missing hours.
        missing_hours_deduction_amount = self._calculate_missing_hours_deduction_value()

        # Find the 'MISSING_HOURS' input line for this payslip.
        # It should have been created by om_hr_payroll's compute_sheet if the input type
        # is linked to the payslip's structure.
        input_mh_line = self.input_line_ids.filtered(lambda r: r.code == 'MISSING_HOURS')

        if input_mh_line:
            # Update its amount. This write to DB ensures it's persisted and used by rules.
            if input_mh_line.amount != missing_hours_deduction_amount:  # Avoid unnecessary writes
                input_mh_line.write({'amount': missing_hours_deduction_amount})
        elif missing_hours_deduction_amount > 0:
            # If the input line doesn't exist but there's a deduction, it means MISSING_HOURS
            # input type might not be in the structure. The rule DED_MISSING_HOURS won't fire.
            # For robustness, one could create it here, but it's better to ensure structure setup.
            # For now, we assume if it's not there, the rule isn't meant to apply or setup is incomplete.
            pass

        # Call super to get the original localdict.
        # This will now use the updated amount for MISSING_HOURS when building `inputs`.
        localdict = super(HrPayslip, self)._get_localdict(rules_dict)

        return localdict
