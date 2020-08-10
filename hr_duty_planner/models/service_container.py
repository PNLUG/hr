# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ServiceContainer(models.Model):
    """
    General service definition that includes several time managed services
    """

    # model
    _name = 'service.container'
    _description = 'General service definition'

    # fields
    # name
    name = fields.Char('Name')
    # description
    description = fields.Char('Description')
