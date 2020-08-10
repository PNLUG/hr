# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExpectedEquipmentCategory(models.Model):
    """
    Equipment category list expected on a service
    """

    # model
    _name = 'expected.eqpmnt_cat'
    _description = 'Service expected equipment'

    # fields
    # minimum quantity
    min_qty = fields.Integer('Minimum quantity', required=True, default=1)
    # maximum quantity: 0 for no limit
    max_qty = fields.Integer('Maximum quantity', help="Value 0 means no limit")
    # equipment category required
    eqp_cat_id = fields.Many2one('maintenance.equipment.category',
                                 string='Equipment category',
                                 required=True)

    # define record name to display in form view
    _rec_name = 'eqp_cat_id'
