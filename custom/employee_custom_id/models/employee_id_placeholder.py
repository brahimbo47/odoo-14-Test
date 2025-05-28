from odoo import models, fields


class EmployeeIDPlaceholder(models.Model):
    _name = 'employee.id.placeholder'
    _description = 'Employee ID Placeholder'

    name = fields.Char(required=True)
    code = fields.Char(required=True)  # e.g., {NAME}, {YEAR}, etc.
