# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VehicleProfile(models.Model):
    """
    Add Profile reference to Vehicle
    """

    _inherit = 'fleet.vehicle'

    # Profile reference
    profile_id = fields.Many2one('service.profile',
                                 'Service profile',
                                 help='Vehicle service profile')
