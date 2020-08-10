# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ServiceProfile(models.Model):
    """
    Collection of rules to assign to a resource
    """

    # model
    _name = 'service.profile'
    _description = 'Profile to group rules'

    # fields
    # name
    name = fields.Char('Name', required=True)
    # set rule ignore
    rule_ignore = fields.Boolean('Ignore Rule', default=False,
                                 help='If active all the Rules will not be checked')
    # parameter values
    parameter_ids = fields.Many2many('service.profileparameter', string='Field')
