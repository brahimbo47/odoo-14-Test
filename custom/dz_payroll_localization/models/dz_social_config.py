from odoo import models, fields, api

class ResConfigSettingsSocial(models.TransientModel):
    _inherit = 'res.config.settings'

    # CNAS Rates
    dz_employee_cnas_rate = fields.Float(
        string='Employee CNAS Rate (%)',
        config_parameter='dz_payroll_localization.employee_cnas_rate',
        default=0.09,
        help="Employee contribution rate for CNAS (Social Security)."
    )
    dz_employer_cnas_rate = fields.Float(
        string='Employer CNAS Rate (%)',
        config_parameter='dz_payroll_localization.employer_cnas_rate',
        default=0.26, # Note: Often cited as 26%, but 25% is the base employer part. Check current law.
        help="Employer contribution rate for CNAS (Social Security)."
    )

    # CSS Rates (Usually part of CNAS, but kept separate as requested)
    # Check if CSS (Chômage - Unemployment) is separate or included in the 26% employer rate.
    # Assuming it's separate for now as per request. Adjust if needed.
    dz_employee_css_rate = fields.Float(
        string='Employee Unemployment Rate (%)',
        config_parameter='dz_payroll_localization.employee_css_rate',
        default=0.00,
        help="Employee contribution rate for Unemployment Insurance (if applicable separately)."
    )
    dz_employer_css_rate = fields.Float(
        string='Employer Unemployment Rate (%)',
        config_parameter='dz_payroll_localization.employer_css_rate',
        default=0.01,
        help="Employer contribution rate for Unemployment Insurance."
    )

    # Add other global social settings if needed