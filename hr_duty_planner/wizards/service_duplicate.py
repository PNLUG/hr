# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
import datetime


class ServiceDuplicateWizard(models.TransientModel):
    """
    Generation of a duplicate of an allocate service
    """

    _name = 'service.duplicate'
    _description = 'Duplicate an allocate service'

    # allocate service reference
    service_allocate_id = fields.Many2one('service.allocate',
                                          string='Allocate service',
                                          )

    # scheduled start time
    date_init = fields.Datetime('Start date', required=True)
    # scheduled start time
    date_stop = fields.Datetime('Stop date', required=True)
    # standard duration
    interval = fields.Integer('Interval', required=True, default=8)
    # resources options
    copy_employee = fields.Boolean('Copy Employees', default=True)
    copy_equipment = fields.Boolean('Copy Equipments', default=True)
    copy_vehicle = fields.Boolean('Copy Vehicles', default=True)
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

    def duplicate_service(self):
        """
        Generate a series of allocate services based on the selected tone with
        start date inside the period limits
        """

        service_allocate = self.service_allocate_id
        duration = self.service_allocate_id.service_template_id.duration
        date_pointer = self.date_init
        interval_set = self.interval
        copy_employee = self.copy_employee
        copy_equipment = self.copy_equipment
        copy_vehicle = self.copy_vehicle
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
            interval_set = (interval_set if interval_set > duration
                            else duration)

            # check end of requested period
            if(date_pointer > self.date_stop):
                break

            # chek week days requested
            if not day_week[date_pointer.weekday()]:
                # calculate next start date
                date_pointer = date_pointer + datetime.timedelta(hours=interval_set)
                continue

            # _todo_ check calendar for working days and holidays

            _tmp_template_id = self.service_allocate_id.service_template_id.id
            _tmp_container_id = self.service_allocate_id.service_container_id.id

            new_service_data = {
                "service_template_id"   : _tmp_template_id,
                "service_container_id"  : _tmp_container_id,
                "scheduled_start"       : date_pointer,
                "generation_id"         : generation_id,
                }

            new_service = self.env['service.allocate'].create(new_service_data)

            # copy resources from the original service
            if copy_employee:
                new_service.employee_ids = service_allocate.employee_ids
            if copy_equipment:
                new_service.equipment_ids = service_allocate.equipment_ids
            if copy_vehicle:
                new_service.vehicle_ids = service_allocate.vehicle_ids

            # update resource info
            new_service.check_skill_request()
            new_service.check_equipment_request()
            new_service.check_vehicle_request()

            # calculate next start date
            date_pointer = date_pointer + datetime.timedelta(hours=interval_set)
        return
