# -*- coding: utf-8 -*-
{
    'name': "DZ Leave Balance Alert",  # سنزيل (Core) الآن

    'summary': """
        Sends automated alerts when employee leave balance nears exhaustion.""",

    'description': """
        This module helps HR manage employee time off more effectively by:
        - Providing a configuration interface for the alert threshold.
        - (Future) Calculating remaining annual leave balance for each employee.
        - (Future) Triggering automated alerts when usage exceeds a configurable threshold.
        - (Future) Sending notifications to the employee and their manager.
    """,

    'author': "Mr Brahim",
    'website': "https://www.brahim.com",

    'category': 'Human Resources/Time Off',
    'version': '14.0.1.1.0-phase2',  # تحديث الإصدار للمرحلة

    'depends': ['base', 'hr', 'hr_holidays', 'mail'],

    'data': [
        # 1. ملفات الأمان (مجموعات، ثم قواعد الوصول CSV، ثم قواعد السجلات)
        'security/dz_leave_balance_alert_groups.xml',
        'security/ir.model.access.csv',
        # 'security/dz_leave_balance_alert_rules.xml', # سنضيفه لاحقًا عند الحاجة لقواعد السجلات

        # 2. ملفات البيانات (مثل السجل الافتراضي للإعدادات)
        'data/leave_alert_config_data.xml',

        # 3. ملفات الواجهات والقوائم (الواجهات أولاً، ثم القوائم)
        'views/leave_config_views.xml',
        'views/menus.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
