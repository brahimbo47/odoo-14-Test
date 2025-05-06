# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _


class DisciplinaryAction(models.Model):
    _name = 'disciplinary.action'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Disciplinary Action'
    _order = 'date_incident desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date_incident = fields.Date(string='Date of Incident', required=True)
    reason = fields.Text(string='Reason', required=True)

    action_type = fields.Selection([
        ('warning', 'Warning'),
        ('deduction', 'Salary Deduction'),
        ('suspension', 'Suspension'),
        ('termination', 'Termination'),
    ], string='Action Type', required=True)

    punishment_duration = fields.Integer(string='Duration (Days)', help="Duration of suspension or related action")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('applied', 'Applied'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')
    ], string='Status', default='draft', tracking=True)

    document = fields.Binary(string='Attachment')
    document_name = fields.Char(string="File Name")

    # Actions to change state
    def action_under_review(self):
        for rec in self:
            rec.state = 'under_review'
            rec._notify_users(f"The disciplinary action for {rec.employee_id.name} is under review.")

    def action_apply(self):
        for rec in self:
            rec.state = 'applied'
            rec._notify_users(f"The disciplinary action for {rec.employee_id.name} has been applied.")

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'
            rec._notify_users(f"The disciplinary action for {rec.employee_id.name} has been *confirmed*.")

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            rec._notify_users(f"The disciplinary action for {rec.employee_id.name} has been *completed*.")

    def _notify_users(self, message):
        """Send notification to HR manager or related users"""
        group_hr_manager = self.env.ref('hr.group_hr_manager')
        for rec in self:
            users = group_hr_manager.users
            for user in users:
                rec.message_post(
                    body=_(message),
                    partner_ids=[user.partner_id.id]
                )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        # Send notification when created
        record.message_post(
            body=f"New disciplinary action created for {record.employee_id.name}.",
        )
        return record
