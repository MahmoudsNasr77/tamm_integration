/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

// Fix webIcon if it's not a string
const originalWebIcon = session.web_icon;
if (originalWebIcon && typeof originalWebIcon !== 'string') {
    console.warn('webIcon is not a string, converting to empty string');
    session.web_icon = '';
}

// Also patch it in the company info
if (session.user_companies) {
    session.user_companies.current_company = session.user_companies.current_company || 1;
    const companies = session.user_companies.allowed_companies;
    if (companies) {
        Object.values(companies).forEach(company => {
            if (company && company.web_icon && typeof company.web_icon !== 'string') {
                console.warn(`Company ${company.name} webIcon is not a string, fixing...`);
                company.web_icon = '';
            }
        });
    }
}