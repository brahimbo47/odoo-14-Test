from odoo import models, fields, api
from odoo.addons.base.models.res_currency import Currency

class ResConfigSettingsFamily(models.TransientModel):
    _inherit = 'res.config.settings'

    # Get company currency - assumes single company or consistent currency
    # A multi-company setup might need company_id field here.
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')

    # Family Allowance Configuration (default values: 600 DA per child, max 5 children)
    dz_amount_per_child = fields.Float(
        string='Amount per Child (DA)',
        currency_field='currency_id',
        config_parameter='dz_payroll_localization.amount_per_child',
        default=600.0,
        help="Monthly family allowance amount per eligible child."
    )
    dz_max_children = fields.Integer(
        string='Maximum Children for Allowance',
        config_parameter='dz_payroll_localization.max_children',
        default=5,
        help="Maximum number of children eligible for the family allowance."
    )