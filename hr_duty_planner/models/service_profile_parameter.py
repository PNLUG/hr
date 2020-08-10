# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ServiceProfileParameter(models.Model):
    """
    Assign values to the rules fields
    """

    # model
    _name = 'service.profileparameter'
    _description = 'Define value of fields used by rules in profile'

    # fields
    # rule reference
    rule_id = fields.Many2one('service.rule', 'Rule')
    # rule field
    rule_field_id = fields.Many2one('service.rulefield', 'Field')
    # Value to use in method
    field_value = fields.Char('Value')

    # define record name to display in form view
    _rec_name = 'rule_id'
