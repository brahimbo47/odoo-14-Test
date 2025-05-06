{
    'name': 'Attendance Bonus Payroll Integration',
    'version': '1.0',
    'summary': 'Integrate perfect attendance bonus with payroll',
    'description': """
        This module automatically adds the Perfect Attendance Bonus into employees' Payslips,
        based on their eligibility data recorded by the attendance_bonus_check module.
        It adds a salary rule conditioned on the eligibility status.
    """,
    'category': 'Human Resources/Payroll',
    'author': 'Mr Brahim (Refined by Assistant)',
    'website': 'www.brahim.com',
    'license': 'LGPL-3',
    'depends': [
        'om_hr_payroll',
        'attendance_bonus_check',
    ],
    'data': [
        'security/dz_leave_balance_alert_rules.xml',
        'security/ir.model.access.csv',
        'views/hr_payslip_views.xml',
        'data/hr_salary_rule_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}