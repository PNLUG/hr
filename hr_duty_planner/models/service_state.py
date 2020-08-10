# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ServiceState(models.Model):
    """
    State of the allocated services
    """

    # model
    _name = 'service.state'
    _description = 'States of allocated services'

    # fields
    # name
    name = fields.Char('Name')
    # description
    description = fields.Char('Description')
