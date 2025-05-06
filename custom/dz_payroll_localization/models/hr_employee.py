from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    dependent_ids = fields.One2many(
        'dz.employee.dependent',
        'employee_id',
        string='Dependents',
        help="List of employee's dependents, typically children for family allowance calculation."
    )
    # Add other Algerian-specific fields if needed (e.g., CNAS number)
    dz_cnas_number = fields.Char(string="CNAS Number")