# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
import datetime


class ServiceUtility(models.Model):
    """
    Utility model to create a management form
    """

    # model
    _name = 'service.utility'
    _description = 'Services utility'

    # fields
    title = fields.Char(default='Dashboard')
    result_message = fields.Text('Check result')

    # define record name to display in form view
    _rec_name = 'title'

    def double_assign(self, parameters):
        """
        Chek for double assignments
        """
        result = self.env['service.rule'].double_assign(parameters['resource_type'],
                                                        parameters['srv_id'])
        self.result_message = result['message']
        return result

    def rule_call(self, parameters):
        """
        Call a rule method
        @param  parameters  dict: parameters to pass to the method
                rule_name   string: name of the method
                param       json: [name:value] couples with method parameters
                srv_id      int: id of the service
                res_obj     obj: resourse object to check with the roule
        """
        result = self.env['service.rule'].rule_call(parameters['rule_name'],
                                                    parameters['param'],
                                                    parameters['srv_id'],
                                                    parameters['res_obj'],
                                                    )
        self.result_message = result['message']
        return result

    def check_resource_rule(self, parameters):
        """
        Check rules for each resource associated to the service
        @param srv_id   int: id of the service
        """
        result = self.env['service.allocate'].check_resource_rule(parameters)
        self.result_message = (result['employee']['message'] +
                               result['equipment']['message'] +
                               result['vehicle']['message'])
        return result

    def hour_active_periond(self, parameters):
        """
        Calculate the total of active hours of a resource in a period of time.
        Active hours are on not off-duty services.
        @param  parameters  dict: {'date_start':, 'date_stop': } period limit
        @param  srv_id  int: service to analyze
        @param  res_obj obj: resourse object to analyze
        """
        result = self.env['service.rule'] \
                     .hour_active_periond({'period': False,
                                           'srv_id': parameters['srv_id'],
                                           'res_obj': False,
                                           })
        self.result_message = result['message']
        return result

    def hour_active_month(self, parameters):
        """
        Calculate the total of active hours of a resource in the last 28 days.
        Active hours are on not off-duty services.
        @param  parameters  dict: {'date_stop':} last day of month to check
        @param  srv_id  int: service to analyze
        @param  res_obj obj: resourse object to analyze
        """
        date_stop = parameters['period']['date_stop'] \
            if parameters['period'] and parameters['period']['date_stop'] \
            else datetime.datetime.now()

        result = self.env['service.rule'] \
                     .hour_active_month({'period': {'date_stop': date_stop,
                                                    },
                                         'srv_id': parameters['srv_id'],
                                         'res_obj': False,
                                         })
        self.result_message = result['message']
        return result
