/** @odoo-module **/
import { Component, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class TammMapView extends Component {
    setup() {
        this.orm = useService("orm");
    }

    async willStart() {
        this.vehicles = await this.orm.searchRead("fleet.vehicle", [
            ["tamm_vehicle_id", "!=", false]
        ], ["name", "license_plate", "current_latitude", "current_longitude", "current_speed"]);
    }

    onMounted() {
        const map = L.map("tamm_map").setView([24.7136, 46.6753], 6); // Center Saudi Arabia
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 18,
            attribution: "© OpenStreetMap"
        }).addTo(map);

        this.vehicles.forEach(v => {
            if (v.current_latitude && v.current_longitude) {
                const marker = L.marker([v.current_latitude, v.current_longitude]).addTo(map);
                marker.bindPopup(`<b>${v.name}</b><br>${v.license_plate}<br>Speed: ${v.current_speed} km/h`);
            }
        });
    }
}

TammMapView.template = "tamm_fleet.MapView";
registry.category("actions").add("tamm_fleet.map_view", TammMapView);
