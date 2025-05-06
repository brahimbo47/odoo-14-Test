# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AttendanceBonusConfig(models.Model):
    _name = 'attendance.bonus.config'
    _description = 'Attendance Bonus Configuration'
    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one configuration record per company is allowed!')
    ]

    display_name = fields.Char(string="Display Name", compute='_compute_display_name', store=False)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    allowed_leave_type_ids = fields.Many2many(
        'hr.leave.type',
        string='Allowed Leave Types',
        help="Select leave types that DO NOT disqualify an employee from the perfect attendance bonus (e.g., Public Holidays, Maternity Leave). "
             "Leaves of types *not* selected here will disqualify the employee if taken.",
        domain="[('active', '=', True)]"
    )

    # Compute method for display_name
    def _compute_display_name(self):
        name = _("Attendance Bonus Configuration Panel")
        for record in self:
            record.display_name = name

    @api.constrains('company_id')
    def _check_company_id(self):
        for record in self:
            if self.search_count([('company_id', '=', record.company_id.id)]) > 1:
                raise ValidationError(_("Configuration already exists for company %s.", record.company_id.name))

    @api.model
    def _get_allowed_leave_types(self, company_id):
        """ Helper method to get allowed leave type IDs for a given company """
        config = self.search([('company_id', '=', company_id)], limit=1)
        if config:
            return config.allowed_leave_type_ids.ids
        else:
            return []