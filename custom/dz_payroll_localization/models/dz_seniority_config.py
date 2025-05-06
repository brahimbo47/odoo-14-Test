from odoo import models, fields, api

class ResConfigSettingsSeniority(models.TransientModel):
    _inherit = 'res.config.settings'

    # Seniority Bonus Configuration (default values: 3 years, 1% per year, max 20%)
    dz_seniority_min_years = fields.Integer(
        string='Minimum Years for Seniority Bonus',
        config_parameter='dz_payroll_localization.min_years',
        default=3,
        help="Minimum number of years of service required to be eligible for the seniority bonus."
    )
    # Seniority Rate Configuration
    dz_seniority_rate_per_year = fields.Float(
        string='Seniority Rate per Year (%)',
        config_parameter='dz_payroll_localization.rate_per_year',
        default=0.01,
        digits='Payroll Rate',
        help="Percentage of the base salary added per year of seniority, after reaching the minimum years."
    )
    # Maximum Seniority Rate Configuration
    dz_seniority_max_rate = fields.Float(
        string='Maximum Seniority Rate (%)',
        config_parameter='dz_payroll_localization.max_rate',
        default=0.2,
        digits='Payroll Rate',
        help="Maximum total percentage for the seniority bonus."
    )