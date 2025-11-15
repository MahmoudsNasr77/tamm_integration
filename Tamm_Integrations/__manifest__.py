# -*- coding: utf-8 -*-
{
    'name': 'Saudi Arabia TAMM Fleet Management Integration',
    'summary': 'Advanced Integration with the Saudi TAMM Fleet Management System including Maintenance, Fuel, Analytics, and Tracking.',
    'version': '18.0.1.0.0',
    'category': 'Fleet Management',
    'author': 'Mahmoud Sabry Mohamed Ahmed',
    'maintainer': 'Mahmoud Sabry Mohamed Ahmed',
    'website': 'https://mahmoudsnasr77.github.io/myportfolio/',
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,

    'depends': ['base', 'fleet', 'hr'],

    'price':2800 ,
    'currency': 'SAR',

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
        'static/description/1.png',
        'static/description/2.png',
        'static/description/3.png',
        'static/description/4.png',
        'static/description/5.png',
        'static/description/6.png',
        'static/description/7.png',
        'static/description/8.png',
        'static/description/9.png',
        'static/description/10.png',
        'static/description/11.png',
        'static/description/12.png',
        'static/description/13.png',
        'static/description/14.png',
    ],

    'description': '''
Tamm Fleet Management Integration for Odoo 18 Community
========================================================

This module provides a complete integration between Odoo 18 and the official Saudi Arabian TAMM Fleet Management System.  
It enables real-time vehicle monitoring, maintenance automation, reporting, and fleet analytics.

Core Features
-------------
- Real-time GPS vehicle tracking and map view
- Maintenance planning and service alerts
- Fuel consumption and cost analytics
- Driver behavior and safety scoring
- Route planning and optimization
- Security alerts and notifications
- KPI dashboards and detailed reports
- Multi-company support

Installation Guide
-------------------
1. Copy the Tamm_Integrations folder into your Odoo addons directory.
2. Activate Developer Mode and update the Apps List.
3. Install the module named "Tamm Fleet Management Integration".
4. Navigate to Tamm Fleet → Configuration → Tamm Settings.
5. Enter your TAMM API URL, API Key, and Secret, then click "Test Connection".
6. Access the Tamm Dashboard to monitor vehicles and alerts.

Documentation
-------------
Full installation and configuration guide:  
https://mahmoudsnasr77.github.io/portfolio

Developer Contact
-----------------
Name: Mahmoud Sabry Mohamed Ahmed  
Email: mahmoudsabrynasr@gmail.com  
Phone: +20 1552404457  
LinkedIn: linkedin.com/in/mahmoudnasr77  
Location: Cairo / Riyadh Timezone  
''',

    'data': [
        'security/tamm_security.xml',
        'security/ir.model.access.csv',
        'data/tamm_cron.xml',
        'data/tamm_sequence.xml',
        'views/tamm_config_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/tamm_tracking_views.xml',
        'views/tamm_maintenance_views.xml',
        'views/tamm_fuel_views.xml',
        'views/tamm_driver_views.xml',
        'views/tamm_route_views.xml',
        'views/tamm_alert_views.xml',
        'views/tamm_report_views.xml',
        'views/tamm_dashboard_views.xml',
        'views/tamm_menu_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'Tamm_Integrations/static/src/css/tamm_dashboard.css',
            'Tamm_Integrations/static/src/js/tamm_dashboard.js',
            'Tamm_Integrations/static/src/xml/tamm_dashboard.xml',
        ],
    },

    'support': 'mahmoudsabrynasr@gmail.com',
    'maintainers': ['mahmoudnasr77'],
    'contributors': [
        'Mahmoud Sabry Mohamed Ahmed <mahmoudsabrynasr@gmail.com>',
    ],
}
