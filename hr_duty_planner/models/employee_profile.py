# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EmployeeProfile(models.Model):
    """
    Add Profile reference to Employee
    """

    _inherit = 'hr.employee'

    # Profile reference
    profile_id = fields.Many2one('service.profile',
                                 'Service profile',
                                 help='Employee service profile')
