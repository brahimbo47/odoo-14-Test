from odoo import models, fields, api
from odoo.addons.base.models.res_currency import Currency

class ResConfigSettingsTransport(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')

    # Transport Allowance Configuration (default value: 1500.0)
    dz_transport_monthly_amount = fields.Float(
        string='Monthly Transport Allowance (DA)',
        currency_field='currency_id',
        config_parameter='dz_payroll_localization.monthly_amount',
        default=1500.0,
        help="Default fixed monthly transport allowance amount."
    )