# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)


class ServiceRule(models.Model):
    """
    Definition of the rules available as specific method.
    This model if filled through xls data file.
    """

    # model
    _name = 'service.rule'
    _description = 'Rules to manage Services'

    # fields
    # method of the rule
    method = fields.Char('Method')
    # rule description
    description = fields.Char('Description')
    # method's fields
    field_ids = fields.Many2many('service.rulefield', string='Fields')
    # define if rule is used
    is_active = fields.Boolean('Active', default=True,
                               help='Set if the rule had to be evaluated')

    # define record name to display in form view
    _rec_name = 'description'

    def double_assign(self, resource_type, obj_id):
        """
        Check if a resource has more than one shift assigned at same time
        @param  resource_type    string: type of the resource
                                        [all, employee, vehicle, equipment]
        @param  obj_id          int:    id of the service; -1 to check all services
        """
        # _TODO_ optimize

        rule_result = True
        rule_msg = ''

        # select service to check
        if obj_id > 0:
            allocate_ids = self.env['service.allocate'].search([('id', '=', obj_id)])
        else:
            allocate_ids = self.env['service.allocate'].search([])

        # get the service data
        for service in allocate_ids:
            date_ini = service.scheduled_start
            date_fin = service.scheduled_stop

            if resource_type in ('employee', 'all') :
                # if it is a next service uses the parent employees for check
                # if lock is activated
                lock = service.parent_service_id.service_template_id.next_lock_employee
                employee_list = (
                    service.employee_ids
                    if not service.parent_service_id or not lock
                    else self.env['service.allocate']
                             .search([('id', '=', service.parent_service_id.id),
                                      ]).employee_ids
                    )
                for employee in employee_list:
                    all_services = self.env['service.allocate'] \
                                       .search([('id', '!=', service.id),
                                                ('scheduled_start', '<', date_fin),
                                                ('scheduled_stop', '>', date_ini),
                                                ('state', '!=', 'closed')
                                                ])
                    for service_double in all_services:
                        if employee in service_double.employee_ids:
                            rule_result = False
                            rule_msg += (('Shift %s/%s: %s\n') % (service.id,
                                                                  service_double.id,
                                                                  employee.name))

            if resource_type in ('equipment', 'all'):
                # if it is a next service uses the parent equipments for check
                # if lock is activated
                lock = service.parent_service_id.service_template_id.next_lock_equipment
                equipment_list = (
                    service.equipment_ids
                    if not service.parent_service_id or not lock
                    else self.env['service.allocate']
                             .search([('id', '=', service.parent_service_id.id),
                                      ]).equipment_ids
                    )
                for equipment in equipment_list:
                    all_services = self.env['service.allocate'] \
                                       .search([('id', '!=', service.id),
                                                ('scheduled_start', '<', date_fin),
                                                ('scheduled_stop', '>', date_ini),
                                                ('state', '!=', 'closed')
                                                ])
                    for service_double in all_services:
                        if equipment in service_double.equipment_ids:
                            rule_result = False
                            rule_msg += (('Shift %s/%s: %s\n') % (service.id,
                                                                  service_double.id,
                                                                  equipment.name))

            if resource_type in ('vehicle', 'all'):
                # if it is a next service uses the parent vehicles for check
                # if lock is activated
                lock = service.parent_service_id.service_template_id.next_lock_vehicle
                vehicle_list = (
                    service.vehicle_ids
                    if not service.parent_service_id or not lock
                    else self.env['service.allocate'].search(
                        [('id', '=', service.parent_service_id.id),
                         ]).vehicle_ids
                    )
                for vehicle in vehicle_list:
                    all_services = self.env['service.allocate'] \
                                       .search([('id', '!=', service.id),
                                                ('scheduled_start', '<', date_fin),
                                                ('scheduled_stop', '>', date_ini),
                                                ('state', '!=', 'closed'),
                                                ])
                    for service_double in all_services:
                        if vehicle in service_double.vehicle_ids:
                            rule_result = False
                            rule_msg += (('Shift %s/%s: %s\n') % (service.id,
                                                                  service_double.id,
                                                                  vehicle.name))

        if not rule_result:
            raise UserError(_('Elements with overlapped shift:')+'\n'+rule_msg)
        return rule_result

    def rule_call(self, rule, param, obj_id):
        """
        Call requested rule
        @param  rule  string: name of the rule
        @param  param json: parameters to pass to the method
        @param  obj_id  obj: object on wich check the method

        @return    rule elaboration
        """

        # _TODO_ check if in rule_id
        rule_name = rule
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, rule_name, "_invalid_rule")
        # Call the method as we return it
        if method == '_invalid_rule':
            result = self._invalid_rule(rule_name)
        else:
            result = method(param, obj_id)
        return result

    def _invalid_rule(self, rule_name):
        """
        Management of method non defined
        """
        # raise UserError(_('Method %s not defined') % (rule_name))
        _logger.error('ERROR _invalid_rule: '+rule_name)

    def _rule_method_template(self):
        """
        Rules definition template
        @param  _todo_
        @return _todo_
        """
        return 0

    def hour_active_week(self, param, obj_id):
        """
        Calculate the total of active hours of a resource in a week.
        By active hours is meant work+on call

        _todo_ define/set active shift
        """
        total_time = 0

        # extract employees of the service
        for employee in (self.env['service.allocate']
                         .search([('id', '=', obj_id)]).employee_ids):
            # get services where employee is assigned
            sql = ('SELECT service_allocate_id '
                   'FROM hr_employee_service_allocate_rel '
                   'WHERE hr_employee_id= %s')
            self.env.cr.execute(sql % str(employee.id))
            # get duration of each service
            # _todo_ calculate as end-start
            for srv_id in self.env.cr.fetchall():
                total_time += self.env['service.allocate'] \
                                  .search([('id', 'in', srv_id)]) \
                                  .service_template_id.duration
        raise UserError(_('Totale ore uomo %s') % (total_time))
        # return total_time

    def hour_rest_week(self, param, obj_id):
        """
        Calculate the total of rest hours of a resource in a week.
        By active hours is meant not work or on call
        _todo_ define/set active shift
        """
        return 8

    def hour_active_month(self, param, res_id):
        """
        Calculate the total of active hours of a resource in a month.
        By active hours is meant work+on call

        _todo_ define/set active shift
        """
        total_time = 0

        # get services where employee is assigned
        sql = ('SELECT service_allocate_id '
               'FROM hr_employee_service_allocate_rel '
               'WHERE hr_employee_id= %s')
        self.env.cr.execute(sql, (tuple(res_id),))
        # get duration of each service
        # _todo_ calculate as end-start
        for srv_id in self.env.cr.fetchall():
            total_time += self.env['service.allocate'] \
                              .search([('id', 'in', srv_id)]) \
                              .service_template_id.duration
        emp_name = self.env['hr.employee'].search([('id', '=', res_id)]).name
        param_dict = json.loads(param)
        # raise UserError
        _logger.error(_('Totale ore (mese) %s: %s [limite %s]')
                      % (emp_name, total_time, param_dict['h_max']))
        # return total_time
