from odoo import models, fields

# Overtime rates for Algeria (default values: 150%, 175%, 200%)
class DzOvertimeRate(models.Model):
    _name = 'dz.overtime.rate'
    _description = 'Algerian Overtime Rates'

    name = fields.Char(required=True, help="e.g., Weekday 17h-21h, Weekend Day, Night Shift")
    code = fields.Char(required=True, help="Technical code used to link with worked days lines (e.g., OT150, OT175, OT200)")
    multiplier = fields.Float(string='Multiplier', required=True, digits='Payroll Rate',
                              help="Rate multiplier (e.g., 1.5 for 150%, 1.75 for 175%, 2.0 for 200%).")

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The Overtime Code must be unique!')
    ]