
# models/tamm_route.py
from odoo import models, fields, api, _

class TammRoute(models.Model):
    _name = 'tamm.route'
    _description = 'Vehicle Route'
    _order = 'start_time desc'
    _rec_name = 'name'
    
    name = fields.Char('Route Name', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', 
                                 required=True, index=True)
    driver_id = fields.Many2one('hr.employee', 'Driver')
    start_time = fields.Datetime('Start Time', required=True, index=True)
    end_time = fields.Datetime('End Time')
    start_location = fields.Char('Start Location')
    end_location = fields.Char('End Location')
    start_latitude = fields.Float('Start Latitude', digits=(10, 8))
    start_longitude = fields.Float('Start Longitude', digits=(11, 8))
    end_latitude = fields.Float('End Latitude', digits=(10, 8))
    end_longitude = fields.Float('End Longitude', digits=(11, 8))
    planned_distance = fields.Float('Planned Distance (km)', digits=(10, 2))
    actual_distance = fields.Float('Actual Distance (km)', digits=(10, 2))
    duration = fields.Float('Duration (hours)', compute='_compute_duration', 
                           store=True, digits=(5, 2))
    status = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], 'Status', default='planned', required=True, index=True)
    
    # Route optimization
    optimized = fields.Boolean('Route Optimized', default=False)
    fuel_estimate = fields.Float('Estimated Fuel (L)', digits=(10, 2))
    fuel_actual = fields.Float('Actual Fuel (L)', digits=(10, 2))
    duration_estimate = fields.Float('Estimated Duration (hours)', digits=(5, 2))
    cost_estimate = fields.Monetary('Estimated Cost', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', 
                                  default=lambda self: self.env.company.currency_id)
    notes = fields.Text('Notes')
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for route in self:
            if route.start_time and route.end_time:
                delta = route.end_time - route.start_time
                route.duration = delta.total_seconds() / 3600.0
            else:
                route.duration = 0.0
    
    def action_start(self):
        self.write({
            'status': 'in_progress',
            'start_time': fields.Datetime.now()
        })
    
    def action_complete(self):
        self.write({
            'status': 'completed',
            'end_time': fields.Datetime.now()
        })
    
    def action_cancel(self):
        self.write({'status': 'cancelled'})
