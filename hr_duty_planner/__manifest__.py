# Copyright 2019 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name":     "HR - Duty Planner",
    "summary":  "Management of duty planning.",
    "version":  "12.0.1.0.0",

    "author":   "Stefano Consolaro <stefano.consolaro@mymage.it>, "
    "Marcelo Frare <mf2965@gmail.com>"
    "Associazione PNLUG - Gruppo Odoo, "
    "Odoo Community Association (OCA)",
    "website":  "https://github.com/PNLUG/vertical-ngo/",
    "license":  "AGPL-3",

    "category": "Human Resources",

    "depends": [
        'fleet',
        'maintenance',
        'hr',
        'product',
        # OCA modules
        'web_timeline',
        'web_widget_color',
        'hr_skill',
        # 'hr_employee_partner_external',
        'fleet_vehicle_category',
        'report_xlsx',
        ],
    "data": [
        'data/data_service_rule.xml',
        'data/data_service_rulefield.xml',
        'data/demo.xml',
        'security/ir.model.access.csv',
        'wizards/service_generate.xml',
        'views/service_menu.xml',
        'views/service_allocate_view.xml',
        'views/service_rule_view.xml',
        'views/service_profile_view.xml',
        'views/service_aggregator_view.xml',
        'views/service_container_view.xml',
        'views/service_expected_view.xml',
        'views/service_template_view.xml',
        'views/employee_profile.xml',
        'reports/xlsx_allocated_service.xml',
        ],
    "css": [
        'static/src/css/hr_duty_planner.css',
        ],
}
