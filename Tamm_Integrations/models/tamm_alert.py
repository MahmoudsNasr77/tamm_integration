
# models/tamm_alert.py
from odoo import models, fields, api, _
import requests
import logging

_logger = logging.getLogger(__name__)

class TammAlert(models.Model):
    _name = 'tamm.alert'
    _description = 'Vehicle Alert'
    _order = 'timestamp desc'
    _rec_name = 'display_name'
    
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', 
                                 required=True, index=True)
    driver_id = fields.Many2one('hr.employee', 'Driver')
    timestamp = fields.Datetime('Timestamp', required=True, 
                               default=fields.Datetime.now, index=True)
    alert_type = fields.Selection([
        ('speeding', 'Speeding'),
        ('harsh_braking', 'Harsh Braking'),
        ('harsh_acceleration', 'Harsh Acceleration'),
        ('engine_fault', 'Engine Fault'),
        ('low_fuel', 'Low Fuel'),
        ('maintenance_due', 'Maintenance Due'),
        ('theft', 'Theft Alert'),
        ('accident', 'Accident'),
        ('geofence_violation', 'Geofence Violation'),
        ('battery_low', 'Battery Low'),
        ('tire_pressure', 'Tire Pressure Warning'),
        ('other', 'Other')
    ], 'Alert Type', required=True, index=True)
    
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], 'Severity', required=True, default='medium', index=True)
    
    description = fields.Text('Description', required=True)
    latitude = fields.Float('Latitude', digits=(10, 8))
    longitude = fields.Float('Longitude', digits=(11, 8))
    location_address = fields.Char('Location Address')
    resolved = fields.Boolean('Resolved', default=False, index=True)
    resolved_date = fields.Datetime('Resolved Date')
    resolved_by = fields.Many2one('res.users', 'Resolved By')
    resolution_notes = fields.Text('Resolution Notes')
    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    
    @api.depends('vehicle_id.name', 'alert_type', 'timestamp')
    def _compute_display_name(self):
        for record in self:
            alert_label = dict(self._fields['alert_type'].selection).get(record.alert_type)
            record.display_name = f"{record.vehicle_id.name} - {alert_label} - {record.timestamp}"
    
    @api.model
    def sync_alerts(self, vehicle, config):
        """Sync alerts from Tamm"""
        if not vehicle.tamm_vehicle_id:
            return False
            
        try:
            response = requests.get(
                f'{config.api_url}/api/v1/vehicles/{vehicle.tamm_vehicle_id}/alerts',
                headers=config._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                for alert in data.get('alerts', []):
                    existing = self.search([
                        ('vehicle_id', '=', vehicle.id),
                        ('timestamp', '=', alert.get('timestamp')),
                        ('alert_type', '=', alert.get('alert_type'))
                    ], limit=1)
                    
                    if not existing:
                        self.create({
                            'vehicle_id': vehicle.id,
                            'timestamp': alert.get('timestamp'),
                            'alert_type': alert.get('alert_type'),
                            'severity': alert.get('severity', 'medium'),
                            'description': alert.get('description', ''),
                            'latitude': alert.get('latitude'),
                            'longitude': alert.get('longitude'),
                            'location_address': alert.get('address', ''),
                        })
                
                return True
                
        except Exception as e:
            _logger.error(f'Error syncing alerts for {vehicle.name}: {str(e)}')
            
        return False
    
    def action_resolve(self):
        """Mark alert as resolved"""
        self.write({
            'resolved': True,
            'resolved_date': fields.Datetime.now(),
            'resolved_by': self.env.user.id,
        })
        return True
    
    def action_unresolve(self):
        """Mark alert as unresolved"""
        self.write({
            'resolved': False,
            'resolved_date': False,
            'resolved_by': False,
        })
        return True
