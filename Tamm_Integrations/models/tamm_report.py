from odoo import models, fields, api, tools, _

class TammReport(models.Model):
    _name = 'tamm.report'
    _description = 'Fleet Analytics Report'
    _auto = False
    _rec_name = 'vehicle_id'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', readonly=True)
    date = fields.Date('Date', readonly=True)
    total_distance = fields.Float('Total Distance (km)', readonly=True, digits=(10, 2))
    total_fuel = fields.Float('Total Fuel (L)', readonly=True, digits=(10, 2))
    total_cost = fields.Monetary('Total Cost', readonly=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', readonly=True)
    average_speed = fields.Float('Average Speed (km/h)', readonly=True, digits=(5, 2))
    fuel_efficiency = fields.Float('Fuel Efficiency (km/L)', readonly=True, digits=(5, 2))
    driving_time = fields.Float('Driving Time (hours)', readonly=True, digits=(5, 2))
    idle_time = fields.Float('Idle Time (hours)', readonly=True, digits=(5, 2))
    alert_count = fields.Integer('Number of Alerts', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER () AS id,
                    t.vehicle_id,
                    DATE(t.timestamp) AS date,
                    COALESCE(MAX(f.currency_id), NULL) AS currency_id,
                    SUM(t.distance) AS total_distance,
                    COALESCE(SUM(f.quantity), 0) AS total_fuel,
                    COALESCE(SUM(f.total_cost), 0) AS total_cost,
                    AVG(t.speed) AS average_speed,
                    CASE 
                        WHEN SUM(f.quantity) > 0 
                        THEN SUM(t.distance) / SUM(f.quantity)
                        ELSE 0
                    END AS fuel_efficiency,
                    SUM(CASE WHEN t.engine_status = 'on' THEN 1 ELSE 0 END) / 60.0 AS driving_time,
                    SUM(CASE WHEN t.engine_status = 'idle' THEN 1 ELSE 0 END) / 60.0 AS idle_time,
                    COUNT(a.id) AS alert_count
                FROM tamm_tracking t
                LEFT JOIN tamm_fuel_log f 
                    ON f.vehicle_id = t.vehicle_id 
                    AND DATE(f.date) = DATE(t.timestamp)
                LEFT JOIN tamm_alert a 
                    ON a.vehicle_id = t.vehicle_id 
                    AND DATE(a.timestamp) = DATE(t.timestamp)
                GROUP BY t.vehicle_id, DATE(t.timestamp)
            )
        """ % self._table)
