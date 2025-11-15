
# models/tamm_maintenance.py
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
import requests
import logging

_logger = logging.getLogger(__name__)

class TammMaintenance(models.Model):
    _name = 'tamm.maintenance'
    _description = 'Vehicle Maintenance'
    _order = 'due_date desc, date desc'
    _rec_name = 'name'
    
    name = fields.Char('Maintenance Type', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', 
                                 required=True, ondelete='cascade', index=True)
    date = fields.Date('Date', required=True, default=fields.Date.today)
    due_date = fields.Date('Due Date', index=True)
    odometer = fields.Float('Odometer Reading (km)', digits=(10, 2))
    cost = fields.Monetary('Cost', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', 
                                  default=lambda self: self.env.company.currency_id)
    notes = fields.Text('Notes')
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('due', 'Due'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], 'Status', default='scheduled', required=True, index=True)
    
    maintenance_type = fields.Selection([
        ('oil_change', 'Oil Change'),
        ('tire_rotation', 'Tire Rotation'),
        ('tire_replacement', 'Tire Replacement'),
        ('brake_service', 'Brake Service'),
        ('battery_replacement', 'Battery Replacement'),
        ('inspection', 'Inspection'),
        ('repair', 'Repair'),
        ('cleaning', 'Cleaning'),
        ('other', 'Other')
    ], 'Type', required=True, default='other')
    
    technician_id = fields.Many2one('hr.employee', 'Technician')
    service_center = fields.Char('Service Center')
    invoice_ref = fields.Char('Invoice Reference')
    
    @api.model
    def sync_maintenance(self, vehicle, config):
        """Sync maintenance data from Tamm"""
        if not vehicle.tamm_vehicle_id:
            return False
            
        try:
            response = requests.get(
                f'{config.api_url}/api/v1/vehicles/{vehicle.tamm_vehicle_id}/maintenance',
                headers=config._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                for maint in data.get('maintenance_records', []):
                    # Check if exists
                    existing = self.search([
                        ('vehicle_id', '=', vehicle.id),
                        ('name', '=', maint.get('name')),
                        ('date', '=', maint.get('date'))
                    ], limit=1)
                    
                    if not existing:
                        self.create({
                            'vehicle_id': vehicle.id,
                            'name': maint.get('name'),
                            'date': maint.get('date'),
                            'due_date': maint.get('due_date'),
                            'odometer': maint.get('odometer', 0.0),
                            'cost': maint.get('cost', 0.0),
                            'notes': maint.get('notes', ''),
                            'state': maint.get('state', 'scheduled'),
                            'maintenance_type': maint.get('type', 'other'),
                            'service_center': maint.get('service_center', ''),
                        })
                
                return True
                
        except Exception as e:
            _logger.error(f'Error syncing maintenance for {vehicle.name}: {str(e)}')
            
        return False
    
    @api.model
    def _cron_check_due_maintenance(self):
        """Check and update due maintenance status"""
        today = fields.Date.today()
        scheduled = self.search([
            ('state', '=', 'scheduled'),
            ('due_date', '<=', today)
        ])
        scheduled.write({'state': 'due'})
    
    def action_start(self):
        self.write({'state': 'in_progress'})
    
    def action_complete(self):
        self.write({
            'state': 'completed',
            'date': fields.Date.today()
        })
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
