# 🧰 Installation Guide - Tamm Fleet Integration

## 🧾 Prerequisites

- **Odoo 18.0 Community Edition**
- **Python package:** `requests`
- **Valid Tamm API credentials** (API URL, Key, Secret)
- **Internet access** to communicate with Tamm API

---

## ⚙️ Installation Steps

### 1. Copy module folder
Copy the `tamm_fleet` folder to your Odoo `addons` directory.

### 2. Update the app list
Go to:  
`Settings → Apps → Update Apps List`  
then search for **"Tamm Fleet Management Integration"**.

### 3. Install the module
Click **Install** from the Apps menu.

### 4. (Alternatively via terminal)
Run this command:
```bash
./odoo-bin -u tamm_fleet -d your_database_name
### 5. Configure Tamm credentials

- Navigate to: **Tamm Fleet → Configuration → Tamm Settings**
- Click **Create**
- Fill in:
  - **API URL** (e.g. `https://api.tamm.sa`)
  - **API Key**
  - **API Secret**
- Click **Test Connection** to verify the connection.

---

### 6. View and monitor vehicles

- Open **Tamm Fleet → Dashboard**
- You’ll see vehicle stats, maintenance schedules, and alerts synced directly from Tamm.

---

## 🛰️ Optional Features (Advanced)

- **Multi-company support** → Each company has its own configuration and data.
- **Map View (Realtime Tracking)** → View all vehicles on a live interactive map.
- **Scheduled Sync (Cron)** → Automatic background synchronization every 15 minutes.

---

## 🧩 Support & Contact

For technical support, installation help, or customization:

**Developer:** Mahmoud Sabry Mohamed Ahmed  
**Role:** Odoo Backend Developer & Integrations Engineer  
**Phone:** 📞 +20 1552404457  
**Email:** ✉️ [mahmoudsabrynasr@gmail.com](mailto:mahmoudsabrynasr@gmail.com)  
**LinkedIn:** 🔗 [linkedin.com/in/mahmoudnasr77](http://linkedin.com/in/mahmoudnasr77)  
**Portfolio:** 🌐 [mahmoudsnasr77.github.io/portfolio](https://mahmoudsnasr77.github.io/portfolio)

**SLA:** Response within **24 hours** for production issues.  
**Timezone:** GMT+2 (Cairo / Riyadh)

---

## ✅ Verification

Once installation and configuration are complete:

- Dashboard data updates automatically every **15 minutes**.
- You can trigger manual sync anytime from:  
  **Tamm Settings → Sync Now**
- You’ll receive real-time success or failure notifications inside Odoo.

---

## 💡 Tip

> For production deployment, always use **HTTPS** and store your API credentials securely in Odoo’s `ir.config_parameter`.
