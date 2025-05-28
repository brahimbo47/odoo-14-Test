from odoo import models, fields, api
from datetime import datetime


class Employee(models.Model):
    _inherit = 'hr.employee'

    custom_employee_id = fields.Char(string="Employee ID", readonly=True)

    @api.model
    def create(self, vals):
        if 'custom_employee_id' not in vals or not vals['custom_employee_id']:
            config = self.env['employee.id.config'].search([], order="id desc", limit=1)
            if config:
                # Department code
                dep_code = ''
                if vals.get('department_id'):
                    department = self.env['hr.department'].browse(vals['department_id'])
                    dep_code = department.name[:3].upper() if department.name else 'GEN'
                else:
                    dep_code = 'GEN'

                # Name initials
                name_initials = ''
                if vals.get('name'):
                    name_initials = vals['name'][:3].upper()

                # Social security number (last 4)
                ssn_last4 = ''
                if vals.get('ssnid'):
                    ssn = vals['ssnid']
                    ssn_last4 = ssn[-4:] if len(ssn) >= 4 else ssn

                # Job position short
                job_code = ''
                if vals.get('job_id'):
                    job = self.env['hr.job'].browse(vals['job_id'])
                    job_code = job.name[:3].upper() if job.name else ''

                # Company code
                comp_code = ''
                if vals.get('company_id'):
                    company = self.env['res.company'].browse(vals['company_id'])
                    comp_code = company.name[:3].upper() if company.name else ''

                # Department ID
                dep_id = str(vals.get('department_id') or '')

                # Contract ID placeholder (not usable during creation, kept empty)
                contract_id = ''

                # Join date (YYYYMM)
                join_yyyymm = ''
                contract_data = vals.get('contract_ids')
                hire_year = datetime.today().year
                if contract_data and isinstance(contract_data, list):
                    for contract in contract_data:
                        if contract[0] == 0 and isinstance(contract[2], dict):
                            date_start_str = contract[2].get('date_start')
                            if date_start_str:
                                try:
                                    join_date = datetime.strptime(date_start_str, '%Y-%m-%d')
                                    hire_year = join_date.year
                                    join_yyyymm = join_date.strftime('%Y%m')
                                except ValueError:
                                    pass
                            break

                if not join_yyyymm:
                    join_yyyymm = datetime.today().strftime('%Y%m')

                # Sequence
                seq = self.env['ir.sequence'].next_by_code('employee.custom.id') or '000'

                # Generate ID from format
                emp_id = (
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

                vals['custom_employee_id'] = emp_id

        return super(Employee, self).create(vals)
