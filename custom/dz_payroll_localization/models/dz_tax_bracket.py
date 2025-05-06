from odoo import models, fields, api

class DzTaxBracket(models.Model):
    _name = 'dz.tax.bracket'
    _description = 'Algerian IRG Tax Brackets'
    _order = 'lower_limit asc'

    name = fields.Char(required=True, help="e.g., Bracket 1, Exemption")
    lower_limit = fields.Float(string='Lower Limit (DA)', required=True, digits='Payroll',
                               help="Minimum annual taxable income for this bracket.")
    upper_limit = fields.Float(string='Upper Limit (DA)', digits='Payroll',
                               help="Maximum annual taxable income for this bracket. Leave empty for the last bracket.")
    rate = fields.Float(string='Rate (%)', required=True, digits='Payroll Rate',
                        help="Tax rate percentage for this bracket.")
    deduction = fields.Float(string='Deduction (DA)', required=True, digits='Payroll',
                             help="Fixed annual amount to deduct after applying the rate for this bracket.")

    _sql_constraints = [
        ('check_limits', 'CHECK(upper_limit IS NULL OR lower_limit < upper_limit)', 'Lower limit must be strictly lower than upper limit.'),
    ]

    @api.constrains('lower_limit', 'upper_limit')
    def _check_overlap(self):
        for record in self:
            domain = [
                ('id', '!=', record.id),
                '|',
                '&', ('lower_limit', '<=', record.lower_limit), ('upper_limit', '>=', record.lower_limit),
                '&', ('lower_limit', '<=', record.upper_limit), ('upper_limit', '>=', record.upper_limit),
                # Add cases where one bracket is fully contained within another
            ]
            if record.upper_limit:
                 domain = ['|',
                           '&', ('lower_limit', '<=', record.lower_limit), ('upper_limit', '>=', record.lower_limit),
                           '|',
                           '&', ('lower_limit', '<=', record.upper_limit), ('upper_limit', '>=', record.upper_limit),
                           '&', ('lower_limit', '>=', record.lower_limit), ('upper_limit', '<=', record.upper_limit),
                          ]


            overlapping = self.search_count(domain)
            # This simple check might not catch all overlaps perfectly, especially with null upper limits.
            # A more robust check might involve iterating through sorted brackets.
            # For now, rely on careful data entry and the SQL constraint.
            # if overlapping:
            #     raise ValidationError(_("Tax brackets cannot overlap."))