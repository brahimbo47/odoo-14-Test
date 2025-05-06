# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DzLeaveAlertConfig(models.Model):
    _name = 'dz.leave.alert.config'
    _description = 'Leave Balance Alert Configuration'
    # _log_access = False # لعدم تسجيل سجلات الوصول تلقائيًا لهذا النموذج

    # لضمان وجود سجل إعدادات واحد فقط
    # سنعتمد على res_id في الواجهة بدلاً من قيد SQL صارم في البداية لتبسيط الأمور
    # يمكن إضافة قيد SQL لاحقًا إذا لزم الأمر:
    # _sql_constraints = [
    # ('uniq_config', 'CHECK(1=1)', 'Only one configuration record is allowed.')
    # ]

    name = fields.Char(required=True, default="Default Configuration", readonly=True, copy=False)
    active = fields.Boolean(
        string='Active System',
        default=True,
        help="Activate or deactivate the leave balance alert system."
    )
    alert_threshold = fields.Float(
        string='Alert Threshold (%)',
        default=80.0,
        required=True,
        help="The percentage of leave usage at which an alert should be triggered (e.g., 80 for 80%)."
    )

    # سنضيف حقل أنواع الإجازات لاحقًا
    # leave_type_ids = fields.Many2many(
    # 'hr.leave.type',
    # string='Applicable Leave Types',
    # help="Select the annual leave types to monitor for the balance alert."
    # )

    @api.constrains('alert_threshold')
    def _check_threshold(self):
        for record in self:
            if not (0 < record.alert_threshold <= 100):
                raise ValidationError(_("Alert Threshold must be between 0 (exclusive) and 100 (inclusive)."))

    @api.model
    def get_active_config(self):
        """
        Helper method to get the active configuration record.
        Creates a default one if none exists.
        """
        config = self.env['dz.leave.alert.config'].search([], limit=1)
        if not config:
            config = self.env['dz.leave.alert.config'].create({
                'name': 'Default Configuration',
                'alert_threshold': 80.0,  # قيمة افتراضية عند الإنشاء التلقائي
                'active': True,
            })
            # إشعار للمستخدم بأن الإعدادات تم إنشاؤها
            # self.env.user.notify_info(message=_("Default Leave Alert Configuration created. Please review."))
        return config

    # لمنع إنشاء أكثر من سجل واحد يدويًا (يمكن تحسينه لاحقًا)
    @api.model
    def create(self, vals):
        if self.search_count([]) > 0 and 'name' in vals and vals[
            'name'] != 'Default Configuration (COPY)':  # السماح بالنسخ
            existing_config = self.search([], limit=1)
            raise ValidationError(
                _("Only one Leave Alert Configuration record is allowed. You can edit the existing one (ID: %s).") % existing_config.id
            )
        return super(DzLeaveAlertConfig, self).create(vals)

    def unlink(self):
        # يمكن منع الحذف إذا أردنا دائمًا وجود سجل واحد
        # raise UserError(_("You cannot delete the leave alert configuration record."))
        return super(DzLeaveAlertConfig, self).unlink()
