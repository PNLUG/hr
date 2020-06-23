# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.exceptions import UserError
import json
import datetime
import logging

_logger = logging.getLogger(__name__)


class ServiceRule(models.Model):
    """
    Definition of the rules available as specific method.
    This model if filled through xls data file.
    """

    # model
    _name = 'service.rule'
    _description = 'Rules to manage Service resources'

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
        @param  resource_type   string: type of the resource
                                        [all | employee | vehicle | equipment]
        @param  obj_id          int:    id of the service; -1 to check all services
        """

        available_resource = ['all', 'employee', 'equipment', 'vehicle']
        rule_result = True
        rule_msg = ''

        if not resource_type in available_resource:
            return {'message': _('Resource not available: %s') % (resource_type),
                    'result': False,
                    'data': {}
                    }

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
                # if lock employee is activated
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
                        # get employees of the parent if exists and template locks them
                        # otherwise service's employees
                        employee_ref = (
                            service_double.parent_service_id.employee_ids
                            if service_double.parent_service_id and
                            service_double.parent_service_id
                                          .service_template_id
                                          .next_lock_employee
                            else service_double.employee_ids
                            )
                        if employee in employee_ref:
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
                        # get equipments of the parent if exists and template locks them
                        # otherwise service's equipments
                        equipment_ref = (
                            service_double.parent_service_id.equipment_ids
                            if service_double.parent_service_id and
                            service_double.parent_service_id
                                          .service_template_id
                                          .next_lock_equipment
                            else service_double.equipment_ids
                            )
                        if equipment in equipment_ref:
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
                        # get vehicles of the parent if exists and template locks them
                        # otherwise service's vehicles
                        vehicle_ref = (
                            service_double.parent_service_id.vehicle_ids
                            if service_double.parent_service_id and
                            service_double.parent_service_id
                                          .service_template_id
                                          .next_lock_vehicle
                            else service_double.vehicle_ids
                            )
                        if vehicle in vehicle_ref:
                            rule_result = False
                            rule_msg += (('Shift %s/%s: %s\n') % (service.id,
                                                                  service_double.id,
                                                                  vehicle.name))

        if obj_id > 0 and not rule_result:
            raise UserError(_('Elements with overlapped shift:')+'\n'+rule_msg)
        return {'message': _('Elements with overlapped shift:')+'\n'+rule_msg,
                'result': rule_result,
                'data': {}
                }

    def rule_call(self, rule_name, parameters, srv_id, res_obj):
        """
        Call requested rule
        @param  rule_name   string: name of the rule
        @param  parameters  json: 'name:value' couples of method's parameters
        @param  srv_id      int: service id
        @param  res_obj     obj: resource object

        @return dict: rule elaboration
        """

        # check if rule method is registered on model
        if not self.env['service.rule'].search([('method', '=', rule_name)]):
            return {'message': 'Rule method '+rule_name+' not registered.',
                    'result': False,
                    'data': {}
                    }
        
        # Get the method from 'self' or invalid method.
        method = getattr(self, rule_name, "_invalid_method")
        # Call the method selected
        if method == '_invalid_method':
            result = self._invalid_method(rule_name)
        else:
            result = method(parameters, srv_id, res_obj)
        return result

    def _invalid_method(self, rule_name):
        """
        Management of method non defined
        """
        # _todo_ log/popup error management
        # raise UserError(_('Method %s not defined') % (rule_name))
        _logger.error('ERROR invalid method: '+rule_name)

        return {'message': 'Method '+rule_name+' not defined.',
                'result': False,
                'data': {}
                }

    ####################################################################################
    # Rules's method definition

    def _rule_method_template(self, parameters, srv_id, res_obj):
        """
        Rules template definition

        For standard development each rule method must have all the same parameters
        defined: use false value in call if not used

        @param  parameters  json: 'name:value' couples of method's parameters
        @param  srv_id      id: id of the service
        @param  res_obj     obj: resource object

        @return dictionary: {'message': string, 'result': boolean, 'data': dict}
            message: description of the elaboration result
            result: True/False based on the logic
            data: informations to be used by another method
        """
        return {'message': 'Template',
                'result': True,
                'data': {}
                }

    def hour_active_periond(self, parameters):
        """
        Calculate the total of active hours of a resource in a period of time.
        Active hours are on no off-duty services.
        @param  parameters  dict: parameters to pass to the method
            @param period dict: {'date_start':, 'date_stop': } period limit
            @param srv_id  int: service to analyze; -1 for all
            @param res_obj obj: resourse object to analyze

        _todo_ manage on-call shift
        """
        total_time = 0
        global_result = {'message': '',
                         'result': True,
                         'data': {},
                         }
        date_start = parameters['period']['date_star'] \
            if parameters['period'] and parameters['period']['date_star'] \
            else datetime.datetime(datetime.datetime.now().year, 1, 1)
        date_stop = parameters['period']['date_stop'] \
            if parameters['period'] and parameters['period']['date_stop'] \
            else datetime.datetime(datetime.datetime.now().year, 12, 31)

        service_list = (self.env['service.allocate']
                            .search([('id', '=', parameters['srv_id'])])
                        if parameters['srv_id']>0
                        else self.env['service.allocate'].search([])
                        )
        for service in service_list:
            for employee in service.employee_ids:
                result = self.hour_active_periond_employee(
                            {'period' : {'date_start': date_start,
                                        'date_stop': date_stop,
                                        },
                            'employee_id': employee.id,
                            })
                total_time += result['data']['hours']
        global_result['message'] += (_('Employees hours %s') % (total_time)) + '\n'
        global_result['data']['hour_empl'] = total_time

        total_time = 0
        for service in service_list:
            for equipment in service.equipment_ids:
                result = self.hour_active_periond_equipment(
                            {'period' : {'date_start': date_start,
                                        'date_stop': date_stop,
                                        },
                            'equipment_id': equipment.id,
                            })
                total_time += result['data']['hours']
        global_result['message'] += (_('Equipments hours %s') % (total_time)) + '\n'
        global_result['data']['hour_eqpm'] = total_time

        total_time = 0
        for service in service_list:
            for vehicle in service.vehicle_ids:
                result = self.hour_active_periond_vehicle(
                            {'period' : {'date_start': date_start,
                                        'date_stop': date_stop,
                                        },
                            'vehicle_id': vehicle.id,
                            })
                total_time += result['data']['hours']
        global_result['message'] += (_('Vehicle hours %s') % (total_time)) + '\n'
        global_result['data']['hour_vhcl'] = total_time

        return {'message': global_result['message'],
                'result': True,
                'data': global_result['data'],
                }

    def hour_active_periond_employee(self, parameters):
        """
        Calculate the total of active hours of an employee in a period of time.
        Active hours are on no off-duty services.
        @param  parameters  dict: parameters to pass to the method
            @param period       dict: {'date_start':, 'date_stop': } period limit
            @param employee_id  int: employee to analyze

        _todo_ 
            manage on-call shift
            manage real start/stop date
        """
        total_time = 0
        # get services where employee is assigned
        sql = ('SELECT service_allocate_id '
               'FROM service_allocate '
               'INNER JOIN hr_employee_service_allocate_rel '
               'on service_allocate.id=service_allocate_id '
               'WHERE '
               'scheduled_start >= %s '
               'and scheduled_stop <= %s '
               'and hr_employee_id = %s '
               )
        self.env.cr.execute(sql,
                            (parameters['period']['date_start'],
                             parameters['period']['date_stop'],
                             str(parameters['employee_id']),
                             )
                            )

        # get duration of each service
        for fetch_srv_id in self.env.cr.fetchall():
            total_time += self.env['service.allocate'] \
                                .search([('id', 'in', fetch_srv_id)]) \
                                .service_template_id.duration
        # _todo_
        # raise UserError(_('Totale ore %s') % (total_time))
        return {'message': _('Totale ore: %s') % (total_time),
                'result': True,
                'data': {'hours': total_time}
                }

    def hour_active_periond_equipment(self, parameters):
        """
        Calculate the total of active hours of an equipment in a period of time.
        Active hours are on no off-duty services.
        @param  parameters  dict: parameters to pass to the method
            @param period       dict: {'date_start':, 'date_stop': } period limit
            @param equipment_id int: equipment to analyze

        _todo_ 
            manage on-call shift
            manage real start/stop date
        """
        total_time = 0
        # get services where equipment is assigned
        sql = ('SELECT service_allocate_id '
               'FROM service_allocate '
               'INNER JOIN maintenance_equipment_service_allocate_rel '
               'on service_allocate.id=service_allocate_id '
               'WHERE '
               'scheduled_start >= %s '
               'and scheduled_stop <= %s '
               'and maintenance_equipment_id = %s '
               )
        self.env.cr.execute(sql,
                            (parameters['period']['date_start'],
                             parameters['period']['date_stop'],
                             str(parameters['equipment_id']),
                             )
                            )

        # get duration of each service
        for fetch_srv_id in self.env.cr.fetchall():
            total_time += self.env['service.allocate'] \
                                .search([('id', 'in', fetch_srv_id)]) \
                                .service_template_id.duration
        # _todo_
        # raise UserError(_('Totale ore %s') % (total_time))
        return {'message': _('Totale ore: %s') % (total_time),
                'result': True,
                'data': {'hours': total_time}
                }

    def hour_active_periond_vehicle(self, parameters):
        """
        Calculate the total of active hours of an vehicle in a period of time.
        Active hours are on no off-duty services.
        @param  parameters  dict: parameters to pass to the method
            @param period       dict: {'date_start':, 'date_stop': } period limit
            @param vehicle_id   int: vehicle to analyze

        _todo_ 
            manage on-call shift
            manage real start/stop date
        """
        total_time = 0
        # get services where vehicle is assigned
        sql = ('SELECT service_allocate_id '
               'FROM service_allocate '
               'INNER JOIN fleet_vehicle_service_allocate_rel '
               'on service_allocate.id=service_allocate_id '
               'WHERE '
               'scheduled_start >= %s '
               'and scheduled_stop <= %s '
               'and fleet_vehicle_id = %s '
               )
        self.env.cr.execute(sql,
                            (parameters['period']['date_start'],
                             parameters['period']['date_stop'],
                             str(parameters['vehicle_id']),
                             )
                            )

        # get duration of each service
        for fetch_srv_id in self.env.cr.fetchall():
            total_time += self.env['service.allocate'] \
                                .search([('id', 'in', fetch_srv_id)]) \
                                .service_template_id.duration
        # _todo_
        # raise UserError(_('Totale ore %s') % (total_time))
        return {'message': _('Totale ore: %s') % (total_time),
                'result': True,
                'data': {'hours': total_time}
                }

    def hour_active_week(self, param, srv_id, res_obj):
        """
        Calculate the total of active hours of a resource in a week.
        By active hours is meant work+on call

        _todo_ define/set active shift
        """
        total_time = 0

        # extract employees of the service
        for employee in (self.env['service.allocate']
                         .search([('id', '=', srv_id)]).employee_ids):
            # get services where employee is assigned
            sql = ('SELECT service_allocate_id '
                   'FROM hr_employee_service_allocate_rel '
                   'WHERE hr_employee_id= %s')
            self.env.cr.execute(sql, (str(employee.id),))
            # get duration of each service
            # _todo_ calculate as end-start
            for fetch_srv_id in self.env.cr.fetchall():
                total_time += self.env['service.allocate'] \
                                  .search([('id', 'in', fetch_srv_id)]) \
                                  .service_template_id.duration
        # _todo_
        # raise UserError(_('Totale ore uomo setimana %s') % (total_time))
        return {'message': _('Totale ore uomo settimana %s') % (total_time),
                'result': True,
                'data': {'hours': total_time}
                }

    def hour_rest_week(self, param, srv_id, res_obj):
        """
        Calculate the total of rest hours of a resource in a week.
        By active hours is meant not work or on call
        _todo_ define/set active shift
        """
        return {'message': 'hour_rest_week To DO', 'result': True, 'data': {'hour': 8}}

    def hour_active_month(self, param, srv_id, res_obj):
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
        self.env.cr.execute(sql, (res_obj.id,))
        # get duration of each service
        # _todo_ calculate as end-start
        for fetch_srv_id in self.env.cr.fetchall():
            total_time += self.env['service.allocate'] \
                              .search([('id', 'in', fetch_srv_id)]) \
                              .service_template_id.duration
        empl_name = self.env['hr.employee'].search([('id', '=', res_obj.id)]).name
        param_dict = json.loads(param)
        # _todo_ remove log
        _logger.info(_('Totale ore (mese) %s: %s [limite %s]')
                     % (empl_name, total_time, param_dict['h_max']))
        return {'message': _('Total hours month: %s') % (total_time),
                'result': True,
                'data': {'hours': total_time}
                }
