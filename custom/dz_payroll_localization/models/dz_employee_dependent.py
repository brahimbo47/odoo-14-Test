from odoo import models, fields, api

class DzEmployeeDependent(models.Model):
    _name = 'dz.employee.dependent'
    _description = 'Employee Dependents (Children)'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    # Consider adding relation type if needed (child, spouse etc.)
    # relation_type = fields.Selection([('child', 'Child'), ('spouse', 'Spouse')], string='Relation', default='child')
    child_name = fields.Char(string='Dependent Name') # Optional as per request
    birth_date = fields.Date(string='Date of Birth') # Optional as per request
    # Add fields relevant for allowances if needed (e.g., is_student, is_disabled)

    # You might add constraints, e.g., birth_date validation