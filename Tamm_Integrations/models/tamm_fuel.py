# models/tamm_fuel.py
from odoo import models, fields, api, _
import requests
import logging

_logger = logging.getLogger(__name__)

class TammFuelLog(models.Model):
    _name = 'tamm.fuel.log'
    _description = 'Fuel Log'
    _order = 'date desc'
    _rec_name = 'display_name'
    
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', 
                                 required=True, ondelete='cascade', index=True)
    driver_id = fields.Many2one('hr.employee', 'Driver')
    date = fields.Datetime('Date', required=True, 
                          default=fields.Datetime.now, index=True)
    quantity = fields.Float('Quantity (Liters)', required=True, digits=(10, 2))
    price_per_liter = fields.Float('Price per Liter', digits=(10, 3))
    total_cost = fields.Monetary('Total Cost', compute='_compute_total_cost', 
                                 store=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', 
                                  default=lambda self: self.env.company.currency_id)
    odometer = fields.Float('Odometer (km)', digits=(10, 2))
    station_name = fields.Char('Station Name')
    invoice_reference = fields.Char('Invoice Reference')
    notes = fields.Text('Notes')
    fuel_type = fields.Selection([
        ('gasoline_91', 'Gasoline 91'),
        ('gasoline_95', 'Gasoline 95'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
    ], 'Fuel Type', default='gasoline_91')
    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    
    @api.depends('quantity', 'price_per_liter')
    def _compute_total_cost(self):
        for log in self:
            log.total_cost = log.quantity * log.price_per_liter
    
    @api.depends('vehicle_id.name', 'date', 'quantity')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.vehicle_id.name} - {record.quantity}L - {record.date}"
    
    @api.model
    def sync_fuel_data(self, vehicle, config):
        """Sync fuel data from Tamm"""
        if not vehicle.tamm_vehicle_id:
            return False
            
        try:
            response = requests.get(
                f'{config.api_url}/api/v1/vehicles/{vehicle.tamm_vehicle_id}/fuel',
                headers=config._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                for fuel in data.get('fuel_logs', []):
                    existing = self.search([
                        ('vehicle_id', '=', vehicle.id),
                        ('date', '=', fuel.get('date')),
                        ('quantity', '=', fuel.get('quantity')),
                        ('invoice_reference', '=', fuel.get('invoice_reference'))
                    ], limit=1)
                    
                    if not existing:
                        self.create({
                            'vehicle_id': vehicle.id,
                            'date': fuel.get('date'),
                            'quantity': fuel.get('quantity'),
                            'price_per_liter': fuel.get('price_per_liter', 0.0),
                            'odometer': fuel.get('odometer', 0.0),
                            'station_name': fuel.get('station_name', ''),
                            'invoice_reference': fuel.get('invoice_reference', ''),
                            'notes': fuel.get('notes', ''),
                            'fuel_type': fuel.get('fuel_type', 'gasoline_91'),
                        })
                
                return True
                
        except Exception as e:
            _logger.error(f'Error syncing fuel data for {vehicle.name}: {str(e)}')
            
        return False
