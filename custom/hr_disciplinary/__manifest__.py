# hr_disciplinary/__manifest__.py

{
    'name': 'HR Disciplinary Actions',
    'version': '1.0',
    'summary': 'Manage employee disciplinary actions and warnings',
    'author': 'Brahim',
    'images': ['static/description/icon.png'],
    'category': 'Human Resources',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/disciplinary_action_views.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
