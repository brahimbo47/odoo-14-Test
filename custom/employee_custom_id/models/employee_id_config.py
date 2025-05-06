from odoo import models, fields, api

class EmployeeIDConfig(models.Model):
    _name = 'employee.id.config'
    _description = 'Employee ID Format Configuration'

    name = fields.Char(
        default='Default Config',
        readonly=True
    )

    format_string = fields.Char(
        string='Format',
        help='Use {DEP} for department, {YEAR} for year, {SEQ} for sequence number',
        default='{DEP}-{YEAR}-{SEQ}'
    )

    @api.model
    def create(self, vals):
        existing = self.search([], limit=1)
        if existing:
            return existing
        return super(EmployeeIDConfig, self).create(vals)