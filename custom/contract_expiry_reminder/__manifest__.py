{
    'name': 'Contract Expiry Reminder',
    'version': '1.0',
    'summary': 'Reminds HR managers about close expiring contracts',
    'author': 'Balhadj',
    'website': 'www.balhadj.com',
    'images': ['static/description/icon.png'],
    'category': 'Human Resources',
    'depends': ['hr_contract', 'mail'],
    'data': [
        'views/contract_reminder_settings_view.xml',
        'views/contract_reminder_chatter_view.xml',
        'data/contract_reminder_cron.xml',
    ],
    'installable': True,
    'application': True,
    'autoInstall': False,
}