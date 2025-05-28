from odoo import models, fields, api


class EmployeeIDConfig(models.Model):
    _name = 'employee.id.config'
    _description = 'Employee ID Format Configuration'

    name = fields.Char(
        default='Default Config',
        readonly=True
    )

    placeholder_ids = fields.Many2many(
        'employee.id.placeholder',
        string='Format Parts',
        help='Select fields to include in the custom Employee ID',
    )

    @api.depends('placeholder_ids')
    def _compute_format_string(self):
        for rec in self:
            rec.format_string = '-'.join(p.code for p in rec.placeholder_ids)

    format_string = fields.Char(
        string='Computed Format String',
        compute='_compute_format_string',
        store=True,
        readonly=True,
    )

    @api.model
    def create(self, vals):
        existing = self.search([], limit=1)
        if existing:
            return existing
        return super(EmployeeIDConfig, self).create(vals)
