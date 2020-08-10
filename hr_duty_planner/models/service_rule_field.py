# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ServiceRuleField(models.Model):
    """
    Definition of the fields used by rule's methods.
    Field value type will be ever saved as string then converted inside methods
    """

    # model
    _name = 'service.rulefield'
    _description = 'fields available to rule\'s methods'

    # fields
    # reference rule
    rule_id = fields.Many2one('service.rule', string='Rule', required=True)
    # field name used in the method
    field_name = fields.Char('Field', required=True,
                             help='Name of the field used inside method')
    # field description
    field_desc = fields.Char('Description', required=True,
                             help='Describe what this field is used for')
    # defualt value
    field_default = fields.Char('Default value',
                                help='Value used if the field is not filled by user')
    # set field mandatory
    field_mandatory = fields.Boolean('Mandatory', default=False,
                                     help='Indicate that the field has to be set')

    # define record name to display in form view
    _rec_name = 'field_name'
