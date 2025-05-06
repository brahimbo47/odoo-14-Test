{
    'name': 'Attendance Bonus Eligibility Check',
    'version': '1.0',
    'summary': 'Check employee attendance and time off for bonus eligibility',
    'description': """
        This module automatically analyzes employees’ Attendance and Time Off records 
        every month to determine if they qualify for a Perfect Attendance Bonus based
        on configurable rules.
    """,
    'author': 'Balhadj',
    'website': 'www.balhadj.com',
    'images': ['static/description/icon.png'],
    'category': 'Human Resources',
    'depends': ['hr_attendance', 'hr_holidays'],
    'data': [
        'security/attendance_bonus_security.xml',
        'security/ir.model.access.csv',
        'data/attendance_bonus_actions.xml',
        'views/attendance_bonus_record_views.xml',
        'views/attendance_bonus_config_views.xml',
        'data/attendance_bonus_cron.xml',
    ],
    'installable': True,
    'application': True,
    'autoInstall': False,
}