/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class TammDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
    }

    async refreshData() {
        await this.orm.call("fleet.vehicle", "sync_with_tamm", [[]]);

        // بدل reload، افتح الـ kanban view
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Fleet Dashboard",
            res_model: "fleet.vehicle",
            view_mode: "kanban,list,form",
            domain: [["tamm_vehicle_id", "!=", false]],
            context: { create: false },
        });
    }
}

TammDashboard.template = "tamm_fleet.Dashboard";

registry.category("actions").add("tamm_fleet.dashboard", TammDashboard);
