

# models/tamm_driver.py
from odoo import models, fields, api, _

class TammDriver(models.Model):
    _name = 'tamm.driver'
    _description = 'Driver Performance'
    _order = 'date desc'
    _rec_name = 'display_name'
    
    employee_id = fields.Many2one('hr.employee', 'Driver', 
                                  required=True, index=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    date = fields.Date('Date', required=True, 
                      default=fields.Date.today, index=True)
    
    # Performance metrics
    speeding_count = fields.Integer('Speeding Violations', default=0)
    harsh_braking_count = fields.Integer('Harsh Braking', default=0)
    harsh_acceleration_count = fields.Integer('Harsh Acceleration', default=0)
    idle_time = fields.Float('Idle Time (hours)', digits=(5, 2))
    driving_time = fields.Float('Driving Time (hours)', digits=(5, 2))
    distance_driven = fields.Float('Distance Driven (km)', digits=(10, 2))
    
    # Safety score
    safety_score = fields.Float('Safety Score', compute='_compute_safety_score', 
                               store=True, digits=(5, 2))
    score_category = fields.Selection([
        ('excellent', 'Excellent (90-100)'),
        ('good', 'Good (75-89)'),
        ('average', 'Average (60-74)'),
        ('poor', 'Poor (0-59)')
    ], 'Score Category', compute='_compute_safety_score', store=True)
    
    notes = fields.Text('Notes')
    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    
    @api.depends('speeding_count', 'harsh_braking_count', 'harsh_acceleration_count')
    def _compute_safety_score(self):
        for driver in self:
            base_score = 100.0
            penalties = (driver.speeding_count * 5) + \
                       (driver.harsh_braking_count * 3) + \
                       (driver.harsh_acceleration_count * 2)
            driver.safety_score = max(0.0, base_score - penalties)
            
            # Determine category
            if driver.safety_score >= 90:
                driver.score_category = 'excellent'
            elif driver.safety_score >= 75:
                driver.score_category = 'good'
            elif driver.safety_score >= 60:
                driver.score_category = 'average'
            else:
                driver.score_category = 'poor'
    
    @api.depends('employee_id.name', 'date')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.employee_id.name} - {record.date}"
