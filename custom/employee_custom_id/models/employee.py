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
                    dep_code = department.name[:3].upper()
                else:
                    dep_code = 'GEN'

                # getting hire year from contract
                hire_year = None
                contract_data = vals.get('contract_ids')
                if contract_data and isinstance(contract_data, list):
                    # Format: [(0, 0, {contract vals})]
                    for contract in contract_data:
                        if contract[0] == 0 and isinstance(contract[2], dict):
                            date_start_str = contract[2].get('date_start')
                            if date_start_str:
                                try:
                                    hire_year = datetime.strptime(date_start_str, '%Y-%m-%d').year
                                except ValueError:
                                    pass
                            break

                if not hire_year:
                    hire_year = datetime.today().year

                # get the next sequence number
                seq = self.env['ir.sequence'].next_by_code('employee.custom.id') or '000'

                # crerwwate the ID
                emp_id = (
                    config.format_string
                    .replace('{DEP}', dep_code)
                    .replace('{YEAR}', str(hire_year))
                    .replace('{SEQ}', seq)
                )

                vals['custom_employee_id'] = emp_id

        return super(Employee, self).create(vals)