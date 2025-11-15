
# models/tamm_tracking.py
from odoo import models, fields, api, _
import requests
import logging

_logger = logging.getLogger(__name__)

class TammTracking(models.Model):
    _name = 'tamm.tracking'
    _description = 'Vehicle Tracking'
    _order = 'timestamp desc'
    _rec_name = 'display_name'
    
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', 
                                 required=True, ondelete='cascade', index=True)
    driver_id = fields.Many2one('hr.employee', 'Driver')
    timestamp = fields.Datetime('Timestamp', required=True, 
                               default=fields.Datetime.now, index=True)
    latitude = fields.Float('Latitude', required=True, digits=(10, 8))
    longitude = fields.Float('Longitude', required=True, digits=(11, 8))
    speed = fields.Float('Speed (km/h)', digits=(5, 2))
    heading = fields.Float('Heading (degrees)', digits=(5, 2))
    altitude = fields.Float('Altitude (m)', digits=(7, 2))
    distance = fields.Float('Distance (km)', digits=(10, 2))
    engine_status = fields.Selection([
        ('on', 'Engine On'),
        ('off', 'Engine Off'),
        ('idle', 'Idle')
    ], 'Engine Status', default='off')
    address = fields.Char('Address')
    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    
    @api.depends('vehicle_id.name', 'timestamp')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.vehicle_id.name} - {record.timestamp}"
    
    @api.model
    def sync_vehicle_location(self, vehicle, config):
        """Sync vehicle location from Tamm"""
        if not vehicle.tamm_vehicle_id:
            return False
            
        try:
            response = requests.get(
                f'{config.api_url}/api/v1/vehicles/{vehicle.tamm_vehicle_id}/location',
                headers=config._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                vals = {
                    'vehicle_id': vehicle.id,
                    'timestamp': data.get('timestamp', fields.Datetime.now()),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'speed': data.get('speed', 0.0),
                    'heading': data.get('heading', 0.0),
                    'altitude': data.get('altitude', 0.0),
                    'distance': data.get('distance', 0.0),
                    'engine_status': data.get('engine_status', 'off'),
                    'address': data.get('address', ''),
                }
                
                # Create tracking record
                self.create(vals)
                
                # Update vehicle current location
                vehicle.write({
                    'current_latitude': data.get('latitude'),
                    'current_longitude': data.get('longitude'),
                    'current_speed': data.get('speed', 0.0),
                    'current_heading': data.get('heading', 0.0),
                    'last_location_update': fields.Datetime.now(),
                })
                
                return True
                
        except Exception as e:
            _logger.error(f'Error syncing location for {vehicle.name}: {str(e)}')
            
        return False
