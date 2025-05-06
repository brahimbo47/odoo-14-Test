from odoo import api, fields, models
from datetime import datetime

class EmployeeIDMigration(models.TransientModel):
    _name = 'employee.id.migration'
    _description = 'Generate Custom IDs for Existing Employees'

    def action_generate_ids(self):
        """Generate custom_employee_id for all employees missing one,
           using hire year from the earliest contract date."""
        self.ensure_one()
        config = self.env['employee.id.config'].search([], limit=1)
        if not config:
            raise models.ValidationError(
                "No Employee ID Config found. Please set up a format first."
            )

        employees = self.env['hr.employee'].search(
            [('custom_employee_id', '=', False)],
            order='create_date'
        )
        for emp in employees:
            dep_code = (emp.department_id.name or 'GEN')[:3].upper()

            # getting hire date from the new contract
            hire_year = None
            if emp.contract_ids:
                # find the most new contract
                earliest = min(emp.contract_ids, key=lambda c: c.date_start or datetime.max.date())
                hire_year = fields.Date.from_string(earliest.date_start).year

            # getting employee creation year if there is no contract
            if not hire_year:
                hire_year = fields.Datetime.from_string(emp.create_date).year

            # getting the next sequence
            seq = self.env['ir.sequence'].next_by_code('employee.custom.id')

            # create ID
            emp.custom_employee_id = (
                config.format_string
                      .replace('{DEP}', dep_code)
                      .replace('{YEAR}', str(hire_year))
                      .replace('{SEQ}', seq)
            )

        return {'type': 'ir.actions.act_window_close'}

    def action_clear_ids(self):
        """Clear custom_employee_id for all employees."""
        employees = self.env['hr.employee'].search([
            ('custom_employee_id', '!=', False)
        ])
        for emp in employees:
            emp.custom_employee_id = False
        return {'type': 'ir.actions.act_window_close'}