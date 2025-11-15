
# README.md
# Tamm Fleet Management Integration for Odoo 18 Community

Complete integration module for Tamm Fleet Management System with Odoo 18 Community Edition.

## Features

- ✅ Real-time GPS vehicle tracking
- ✅ Maintenance management and scheduling
- ✅ Fuel consumption monitoring
- ✅ Driver performance analysis
- ✅ Route planning and optimization
- ✅ Alerts and notifications system
- ✅ Comprehensive reporting and analytics
- ✅ Full Arabic support

## Installation

1. Copy the `tamm_fleet` folder to your Odoo addons directory
2. Update apps list: Settings → Apps → Update Apps List
3. Search for "Tamm Fleet Management Integration"
4. Click Install

## Configuration

1. Go to Tamm Fleet → Configuration → Tamm Settings
2. Create a new configuration
3. Enter your Tamm API credentials:
   - API URL
   - API Key
   - API Secret
4. Click "Test Connection" to verify
5. Configure sync interval (default: 15 minutes)

## Usage

### Vehicle Setup
1. Go to Fleet → Vehicles
2. Open a vehicle record
3. In "Tamm Integration" tab, enter:
   - Tamm Vehicle ID
   - GPS Device ID
4. Click "Sync with Tamm" to start synchronization

### Monitoring
- **Dashboard**: Real-time overview of all vehicles
- **Tracking**: View location history and routes
- **Maintenance**: Schedule and track maintenance
- **Fuel**: Monitor consumption and costs
- **Alerts**: Receive safety and system notifications
- **Reports**: Analyze fleet performance

## Requirements

- Odoo 18.0 Community Edition
- Python packages: requests
- Valid Tamm API credentials

## Support

For issues and feature requests, please contact your system administrator.

## License

LGPL-3
