
# -*- coding: utf-8 -*-
{
    'name': 'Tamm Fleet Management Integration',
    'version': '18.0.1.0.0',
    'category': 'Fleet',
    'summary': 'Integration with Tamm Fleet Management System for Saudi Arabia',
    'description': '''
        Tamm Fleet Management Integration for Odoo 18 Community
        ========================================================
        * Real-time vehicle tracking and GPS integration
        * Vehicle management and maintenance scheduling
        * Fuel consumption monitoring
        * Driver behavior analysis
        * Route optimization
        * Safety and security alerts
        * Comprehensive reporting and analytics
    ''',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'fleet', 'hr'],
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
            'tamm_fleet/static/src/css/tamm_dashboard.css',
            'tamm_fleet/static/src/js/tamm_dashboard.js',
            'tamm_fleet/static/src/xml/tamm_dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# models/__init__.py
from . import tamm_config
from . import fleet_vehicle
from . import tamm_tracking
from . import tamm_maintenance
from . import tamm_fuel
from . import tamm_driver
from . import tamm_route
from . import tamm_alert
from . import tamm_report

# models/tamm_config.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import logging
import json

_logger = logging.getLogger(__name__)

class TammConfig(models.Model):
    _name = 'tamm.config'
    _description = 'Tamm System Configuration'
    _rec_name = 'name'
    
    name = fields.Char('Configuration Name', required=True)
    api_url = fields.Char('Tamm API URL', required=True, 
                          help='Base URL for Tamm API endpoint')
    api_key = fields.Char('API Key', required=True)
    api_secret = fields.Char('API Secret', required=True)
    company_id = fields.Many2one(
        'res.company', 
        'Company', 
        required=True, 
        default=lambda self: self.env.company
    )
    active = fields.Boolean('Active', default=True)
    sync_interval = fields.Integer('Sync Interval (minutes)', default=15)
    last_sync = fields.Datetime('Last Sync', readonly=True)
    sync_status = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending')
    ], 'Sync Status', default='pending', readonly=True)
    sync_error = fields.Text('Last Sync Error', readonly=True)
    
    _sql_constraints = [
        ('name_company_unique', 'unique(name, company_id)', 
         'Configuration name must be unique per company!')
    ]
    
    @api.model
    def get_active_config(self):
        """Get active Tamm configuration for current company"""
        return self.search([
            ('active', '=', True),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
    
    def _get_headers(self):
        """Prepare API headers"""
        self.ensure_one()
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'X-API-Secret': self.api_secret
        }
    
    def test_connection(self):
        """Test connection to Tamm API"""
        self.ensure_one()
        try:
            response = requests.get(
                f'{self.api_url}/api/v1/health',
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                self.write({
                    'sync_status': 'success',
                    'sync_error': False,
                    'last_sync': fields.Datetime.now()
                })
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Connection to Tamm API successful!'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_('API returned status code: %s') % response.status_code)
                
        except Exception as e:
            error_msg = str(e)
            _logger.error(f'Tamm connection error: {error_msg}')
            self.write({
                'sync_status': 'failed',
                'sync_error': error_msg
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Failed to connect: %s') % error_msg,
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_sync_now(self):
        """Manual sync trigger"""
        self.ensure_one()
        vehicles = self.env['fleet.vehicle'].search([
            ('tamm_vehicle_id', '!=', False),
            ('company_id', '=', self.company_id.id)
        ])
        vehicles.sync_with_tamm()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Started'),
                'message': _('Syncing %s vehicles...') % len(vehicles),
                'type': 'info',
            }
        }

# models/fleet_vehicle.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    # Tamm Integration Fields
    tamm_vehicle_id = fields.Char('Tamm Vehicle ID', index=True)
    gps_device_id = fields.Char('GPS Device ID')
    gps_provider = fields.Selection([
        ('tamm', 'Tamm'),
        ('other', 'Other')
    ], 'GPS Provider', default='tamm')
    
    # Tracking Fields
    tracking_ids = fields.One2many('tamm.tracking', 'vehicle_id', 'Tracking History')
    tracking_count = fields.Integer('Tracking Records', compute='_compute_counts')
    
    # Maintenance Fields
    maintenance_ids = fields.One2many('tamm.maintenance', 'vehicle_id', 'Maintenance Records')
    maintenance_count = fields.Integer('Maintenance Records', compute='_compute_counts')
    next_maintenance_date = fields.Date('Next Maintenance', compute='_compute_maintenance_info')
    maintenance_due = fields.Boolean('Maintenance Due', compute='_compute_maintenance_info')
    
    # Fuel Fields
    fuel_log_ids = fields.One2many('tamm.fuel.log', 'vehicle_id', 'Fuel Logs')
    fuel_log_count = fields.Integer('Fuel Logs', compute='_compute_counts')
    average_fuel_consumption = fields.Float('Avg Fuel (L/100km)', 
                                           compute='_compute_fuel_stats', 
                                           digits=(10, 2))
    total_fuel_cost = fields.Monetary('Total Fuel Cost', 
                                      compute='_compute_fuel_stats',
                                      currency_field='currency_id')
    
    # Route Fields
    route_ids = fields.One2many('tamm.route', 'vehicle_id', 'Routes')
    route_count = fields.Integer('Routes', compute='_compute_counts')
    
    # Alert Fields
    alert_ids = fields.One2many('tamm.alert', 'vehicle_id', 'Alerts')
    alert_count = fields.Integer('Alerts', compute='_compute_counts')
    open_alert_count = fields.Integer('Open Alerts', compute='_compute_counts')
    
    # Current Location
    current_latitude = fields.Float('Current Latitude', digits=(10, 8))
    current_longitude = fields.Float('Current Longitude', digits=(11, 8))
    current_speed = fields.Float('Current Speed (km/h)', digits=(5, 2))
    current_heading = fields.Float('Current Heading (°)', digits=(5, 2))
    last_location_update = fields.Datetime('Last Location Update')
    
    # Statistics
    total_distance = fields.Float('Total Distance (km)', 
                                  compute='_compute_distance_stats',
                                  digits=(12, 2))
    monthly_distance = fields.Float('Monthly Distance (km)',
                                    compute='_compute_distance_stats',
                                    digits=(10, 2))
    
    currency_id = fields.Many2one('res.currency', 
                                  default=lambda self: self.env.company.currency_id)
    
    @api.depends('tracking_ids', 'maintenance_ids', 'fuel_log_ids', 
                 'route_ids', 'alert_ids', 'alert_ids.resolved')
    def _compute_counts(self):
        for vehicle in self:
            vehicle.tracking_count = len(vehicle.tracking_ids)
            vehicle.maintenance_count = len(vehicle.maintenance_ids)
            vehicle.fuel_log_count = len(vehicle.fuel_log_ids)
            vehicle.route_count = len(vehicle.route_ids)
            vehicle.alert_count = len(vehicle.alert_ids)
            vehicle.open_alert_count = len(vehicle.alert_ids.filtered(
                lambda a: not a.resolved))
    
    @api.depends('maintenance_ids', 'maintenance_ids.state', 
                 'maintenance_ids.due_date')
    def _compute_maintenance_info(self):
        today = fields.Date.today()
        for vehicle in self:
            due_maintenance = vehicle.maintenance_ids.filtered(
                lambda m: m.state in ['scheduled', 'due'] and m.due_date
            ).sorted('due_date')
            
            if due_maintenance:
                vehicle.next_maintenance_date = due_maintenance[0].due_date
                vehicle.maintenance_due = due_maintenance[0].due_date <= today
            else:
                vehicle.next_maintenance_date = False
                vehicle.maintenance_due = False
    
    @api.depends('tracking_ids.distance')
    def _compute_distance_stats(self):
        for vehicle in self:
            vehicle.total_distance = sum(vehicle.tracking_ids.mapped('distance'))
            
            # Calculate monthly distance
            first_day = fields.Date.today().replace(day=1)
            monthly_tracking = vehicle.tracking_ids.filtered(
                lambda t: t.timestamp and 
                fields.Date.to_date(t.timestamp) >= first_day
            )
            vehicle.monthly_distance = sum(monthly_tracking.mapped('distance'))
    
    @api.depends('fuel_log_ids.quantity', 'fuel_log_ids.total_cost', 
                 'total_distance')
    def _compute_fuel_stats(self):
        for vehicle in self:
            total_fuel = sum(vehicle.fuel_log_ids.mapped('quantity'))
            vehicle.total_fuel_cost = sum(vehicle.fuel_log_ids.mapped('total_cost'))
            
            if total_fuel > 0 and vehicle.total_distance > 0:
                vehicle.average_fuel_consumption = (total_fuel / vehicle.total_distance) * 100
            else:
                vehicle.average_fuel_consumption = 0.0
    
    def sync_with_tamm(self):
        """Sync vehicle data with Tamm system"""
        config = self.env['tamm.config'].get_active_config()
        if not config:
            raise UserError(_('No active Tamm configuration found. Please configure Tamm integration first.'))
        
        success_count = 0
        for vehicle in self.filtered(lambda v: v.tamm_vehicle_id):
            try:
                # Sync location
                self.env['tamm.tracking'].sync_vehicle_location(vehicle, config)
                
                # Sync fuel data
                self.env['tamm.fuel.log'].sync_fuel_data(vehicle, config)
                
                # Sync maintenance
                self.env['tamm.maintenance'].sync_maintenance(vehicle, config)
                
                # Sync alerts
                self.env['tamm.alert'].sync_alerts(vehicle, config)
                
                success_count += 1
                
            except Exception as e:
                _logger.error(f'Error syncing vehicle {vehicle.name}: {str(e)}')
                
        config.write({
            'last_sync': fields.Datetime.now(),
            'sync_status': 'success' if success_count > 0 else 'failed'
        })
        
        return True
    
    def action_view_tracking(self):
        self.ensure_one()
        return {
            'name': _('Vehicle Tracking'),
            'type': 'ir.actions.act_window',
            'res_model': 'tamm.tracking',
            'view_mode': 'list,form,map',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}
        }
    
    def action_view_maintenance(self):
        self.ensure_one()
        return {
            'name': _('Maintenance Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'tamm.maintenance',
            'view_mode': 'list,form,calendar',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}
        }
    
    def action_view_fuel_logs(self):
        self.ensure_one()
        return {
            'name': _('Fuel Logs'),
            'type': 'ir.actions.act_window',
            'res_model': 'tamm.fuel.log',
            'view_mode': 'list,form,pivot,graph',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}
        }
    
    def action_view_alerts(self):
        self.ensure_one()
        return {
            'name': _('Vehicle Alerts'),
            'type': 'ir.actions.act_window',
            'res_model': 'tamm.alert',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}
        }

