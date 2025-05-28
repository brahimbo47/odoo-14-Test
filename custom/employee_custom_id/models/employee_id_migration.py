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

            name_initials = emp.name[:3].upper() if emp.name else ''
            ssn_last4 = emp.ssnid[-4:] if emp.ssnid and len(emp.ssnid) >= 4 else ''
            job_code = emp.job_id.name[:3].upper() if emp.job_id and emp.job_id.name else ''
            comp_code = emp.company_id.name[:3].upper() if emp.company_id and emp.company_id.name else ''
            dep_id = str(emp.department_id.id) if emp.department_id else ''
            contract_id = ''  # not meaningful here
            join_yyyymm = ''
            hire_year = datetime.today().year

            if emp.contract_ids:
                earliest = min(emp.contract_ids, key=lambda c: c.date_start or datetime.max.date())
                if earliest.date_start:
                    hire_year = earliest.date_start.year
                    join_yyyymm = earliest.date_start.strftime('%Y%m')

            if not join_yyyymm:
                join_yyyymm = emp.create_date.strftime('%Y%m') if emp.create_date else datetime.today().strftime('%Y%m')

            seq = self.env['ir.sequence'].next_by_code('employee.custom.id')

            emp.custom_employee_id = (
                config.format_string
                .replace('{DEP}', dep_code)
                .replace('{YEAR}', str(hire_year))
                .replace('{SEQ}', seq)
                .replace('{NAME}', name_initials)
                .replace('{SSN}', ssn_last4)
                .replace('{JOB}', job_code)
                .replace('{COMP}', comp_code)
                .replace('{DEPID}', dep_id)
                .replace('{CID}', contract_id)
                .replace('{JOIN}', join_yyyymm)
            )

        return {'type': 'ir.actions.act_window_close'}

    def action_clear_ids(self):
        employees = self.env['hr.employee'].search([
            ('custom_employee_id', '!=', False)
        ])
        for emp in employees:
            emp.custom_employee_id = False
        return {'type': 'ir.actions.act_window_close'}
