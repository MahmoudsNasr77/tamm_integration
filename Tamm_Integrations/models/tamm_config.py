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