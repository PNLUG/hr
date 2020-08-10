# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
import datetime


class ServiceGenerateWizard(models.TransientModel):
    """
    Generation of empty allocated services from a template
    """
    _name = 'service.generate'
    _description = 'Generate a list of services'

    # template service reference
    service_template_id = fields.Many2one('service.template',
                                          string='Template service',
                                          required=True,
                                          )
    # container service reference
    service_container_id = fields.Many2one('service.container',
                                           string='Container service',
                                           required=True,
                                           )

    # scheduled start time
    date_init = fields.Datetime('Start date', required=True)
    # scheduled start time
    date_stop = fields.Datetime('Stop date', required=True)
    # standard duration
    interval = fields.Integer('Interval', required=True, default=8)
    # calendar options
    day_mon = fields.Boolean('Monday', default=True)
    day_tue = fields.Boolean('Tuensday', default=True)
    day_wed = fields.Boolean('Wednesday', default=True)
    day_thu = fields.Boolean('Thursday', default=True)
    day_fri = fields.Boolean('Friday', default=True)
    day_sat = fields.Boolean('Saturday', default=True)
    day_sun = fields.Boolean('Sunday', default=True)
    day_wrk = fields.Boolean('Working Days', default=False,
                             help='Uses only calendar working days')
    day_hol = fields.Boolean('Holidays', default=False,
                             help='Include calendar holidays')

    # utility to filter container services to template's container services
    @api.onchange('service_template_id')
    def _get_template_container(self):
        """
        Extract list of container services associated to the template service
        """
        container_list = []
        # reset value to avoid errors
        self.service_container_id = [(5)]
        for container_service in self.service_template_id.service_container_ids:
            container_list.append(container_service.id)

        return {'domain': {'service_container_id': [('id', 'in', container_list)]}}

    def generate_service(self):
        """
        Generate a series of allocate services based on the selected template with
        start date inside the period limits
        """

        service_template = self.service_template_id
        date_pointer = self.date_init
        interval_set = self.interval
        day_week = {0: self.day_mon,
                    1: self.day_tue,
                    2: self.day_wed,
                    3: self.day_thu,
                    4: self.day_fri,
                    5: self.day_sat,
                    6: self.day_sun
                    }
        generation_id = datetime.datetime.now().strftime("A %Y-%m-%d-%H-%M-%S")

        while True:
            # get minimum between interval and duration
            interval_set = (interval_set if interval_set > service_template.duration
                            else service_template.duration)

            # check end of requested period
            if(date_pointer > self.date_stop):
                break

            # chek week days requested
            if not day_week[date_pointer.weekday()]:
                # calculate next start date
                date_pointer = date_pointer + datetime.timedelta(hours=interval_set)
                continue

            # _todo_ check calendar for working days and holidays

            new_service_data = {
                "service_template_id"   : self.service_template_id.id,
                "service_container_id"  : self.service_container_id.id,
                "scheduled_start"       : date_pointer,
                "generation_id"         : generation_id,
                }

            self.env['service.allocate'].create(new_service_data)

            # calculate next start date
            date_pointer = date_pointer + datetime.timedelta(hours=interval_set)
        return
