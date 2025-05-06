{
    'name': 'Expense Limit',
    'version': '1.0',
    'summary': 'Limit expense amount per category',
    'author': 'Balhadj',
    'website': 'www.balhadj.com',
    'images': ['static/description/icon.png'],
    'category': 'Human Resources',
    'depends': ['hr_expense', 'product'],
    'data': [
        'views/expense_views.xml',
    ],
    'installable': True,
    'application': True,
    'autoInstall': False,
}