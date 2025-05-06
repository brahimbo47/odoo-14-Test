from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ExpenseCategory(models.Model):
    _inherit = 'product.product'

    max_limit = fields.Float(string="Maximum Allowed Amount", help="Set 0 for no limit")

class Expense(models.Model):
    _inherit = 'hr.expense'

    @api.constrains('total_amount', 'category_id')
    def _check_expense_limit(self):
        for expense in self:
            limit = expense.product_id.max_limit
            if limit and expense.total_amount > limit:
                raise ValidationError(
                    f"Expense amount ({expense.total_amount}) exceeds the maximum "
                    f"of {limit} for product '{expense.product_id.name}'."
                )