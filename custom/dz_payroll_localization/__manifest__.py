{
    'name': "Algerian Payroll Localization",
    'summary': """Payroll Rules and Structures based on om_hr_payroll and the Algerian market.""",
    'description': """
        This module provides:
        - Algerian Salary Rule Categories
        - Algerian Salary Rules (IRG, CNAS, CSS, Allowances)
        - Configuration models for rates and brackets (IRG, CNAS, Family, Seniority, Transport, Overtime)
        - Employee dependents tracking
        - Basic Salary Structures (Employee, Freelance, Intern)
        - Reporting Wizard placeholder
        - Designed for Odoo 14 and requires 'om_hr_payroll'.
    """,
    'author': "Balhadj",
    'website': "https://www.balhadj.com",
    'images': ['static/description/icon.png'],
    'category': 'Human Resources',
    'version': '14.0.1.0.0',
    'depends': ['base', 'hr', 'om_hr_payroll','hr_attendance'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/dz_tax_bracket_data.xml',
        # 'data/hr_salary_rule_category_data.xml',
        'data/hr_payslip_input_type_data.xml',
        # 'data/hr_salary_rule_data.xml',
        # 'data/hr_payroll_structure_data.xml',
        # 'data/ir_cron_data.xml',
        #
        # 'views/dz_tax_bracket_views.xml',
        # 'views/dz_overtime_rate_views.xml',
        # 'views/dz_employee_dependent_views.xml',
        # 'views/hr_employee_views.xml',
        # 'views/hr_payslip_report_views.xml',
        # 'views/payroll_menus.xml',
        # 'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
