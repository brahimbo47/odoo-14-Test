from odoo import models, fields, api
from datetime import timedelta

class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Contract with expiry reminder and chatter'

    reminder_days = fields.Integer(
        string='Reminder Days Before Expiry',
        default=30,
        help="Number of days before expiry to notify HR",
        tracking=True
    )

    # cron function
    def check_expiring_contracts(self):

        # Get the current date
        today = fields.Date.context_today(self)
        contracts = self.search([
            ('date_end', '!=', False),
            ('state', 'in', ['draft', 'open']),
        ])

        # Filter contracts that are expiring soon
        expiring = self._filter_by_reminder(contracts, today)
        if not expiring:
            return

        # Find all HR users once
        hr_group = self.env.ref('hr.group_hr_user')
        hr_users = self.env['res.users'].search([
            ('groups_id', 'in', [hr_group.id])
        ])

        # Prepare the message
        lines = [
            f"• {c.employee_id.name} – ends on {c.date_end} "
            f"(remind {c.reminder_days} days before)"
            for c in expiring
        ]
        combined_body = (
                "⚠️ <b>Contract Expiry Reminder</b>\n\n"
                + "\n".join(lines)
        )

        # For each expiring contract send a message
        expiring.message_post(
            body=combined_body,
            subject="Contract Expiry Reminder",
            partner_ids=[(4, u.partner_id.id) for u in hr_users],
        )

        # Send popup notification to all HR users
        expiring_list = "\n".join(lines)
        payload = {
            'type': 'simple_notification',
            'title': 'Contract Expiry Reminder',
            'message': expiring_list,
            'sticky': False,
        }
        for user in hr_users:
            channel = (self._cr.dbname, 'res.partner', user.partner_id.id)
            self.env['bus.bus'].sendone(channel, payload)

    # Filter contracts based on reminder_days
    def _filter_by_reminder(self, contracts, today):
        res = self.env['hr.contract']
        for c in contracts:
            if c.reminder_days is not None:
                if today >= c.date_end - timedelta(days=c.reminder_days):
                    res |= c
        return res
