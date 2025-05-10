from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    missing_hour_penalty_amount = fields.Float(
        string="Missing Hour Penalty (DZD)",
        default=100.0,
        help="Amount (e.g., DZD 100) to deduct per missing hour of work."
    )


class DzPayrollConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    missing_hour_penalty_amount = fields.Float(
        related='company_id.missing_hour_penalty_amount',
        string="Missing Hour Penalty (DZD)",
        readonly=False,
        help="Amount (e.g., DZD 100) to deduct per missing hour of work."
    )
    # If you prefer a global setting instead of company-specific:
    # missing_hour_penalty_amount = fields.Float(
    #     string="Missing Hour Penalty (DZD)",
    #     config_parameter='dz_payroll_localization.missing_hour_penalty_amount',
    #     default=100.0,
    #     help="Amount (e.g., DZD 100) to deduct per missing hour of work."
    # )
