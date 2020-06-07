# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class XlsxAllocatedService(models.AbstractModel):
    _name = 'report.hr_duty_planner.xlsx_allocated_service'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, extra):

        layout_report = data['form']['layout_report']

        if layout_report == 'pivot':
            self._export_pivot(workbook, data)
        else:
            self._export_list(workbook, data)

    def _export_list(self, workbook, data):

        ids = data['ids']
        services = self.env['service.allocate'].browse(ids)
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']

        sheet = workbook.add_worksheet(_('Service allocate'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_column(0, 1, 20)
        sheet.set_column(2, 3, 35)
        sheet.set_column(4, 7, 15)
        sheet.set_column(8, 11, 35)

        bold_style = workbook.add_format({'bold': True,
                                          'font_size': 14,
                                          'bottom': 1,
                                          })

        title_style = workbook.add_format({'bold': False,
                                           'align': 'center',
                                           'bg_color': '#C0C0C0',
                                           'bottom': 1,
                                           })

        center_style = workbook.add_format({'bold': False,
                                            'align': 'center',
                                            'valign': 'top',
                                            })

        left_style = workbook.add_format({'bold': False,
                                          'align': 'left',
                                          'valign': 'top',
                                          })

        right_style = workbook.add_format({'bold': False,
                                           'align': 'right',
                                           'valign': 'top',
                                           })

        # rows
        row = 0
        header = False
        for service in services:
            # header
            if not header:
                header = True
                sheet.write(row, 0, _('Allocated service'), bold_style)
                sheet.write(row, 3, _('From:'), bold_style)
                from_date = date_from[8:10] + '/' + date_from[5:7] + '/' + date_from[:4]
                sheet.write(row, 4, from_date, bold_style)
                sheet.write(row, 5, _('To:'), bold_style)
                to_date = date_to[8:10] + '/' + date_to[5:7] + '/' + date_to[:4]
                sheet.write(row, 6, to_date, bold_style)

                row += 2
                self.header_ = [_('Scheduled start'),
                                _('Scheduled stop'),
                                _('Container'),
                                _('Name'),
                                _('State'),
                                _('Duration'),
                                _('Uom'),
                                _('Employees'),
                                _('Vehicles'),
                                _('Equipments'),
                                ]

                sheet_title = self.header_
                sheet.write_row(row, 0, sheet_title, title_style)
                row += 1

            s_start = service.scheduled_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            s_stop = service.scheduled_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            s_container = service.service_container_id.name
            s_name = service.service_template_id.name
            s_state = service.state
            s_duration = service.service_template_id.duration
            s_duration_uom = service.service_template_id.duration_uom_id.name

            # used to set row height
            max_rows = 1

            s_employees = ''
            for employee in service.employee_ids:
                s_employees += employee.name + ';\n'
            if s_employees:
                s_employees = s_employees[:-2]
            if len(service.employee_ids) > max_rows:
                max_rows = len(service.employee_ids)

            s_vehicles = ''
            for vehicle in service.vehicle_ids:
                s_vehicles += vehicle.name + ';\n'
            if s_vehicles:
                s_vehicles = s_vehicles[:-2]
            if len(service.vehicle_ids) > max_rows:
                max_rows = len(service.vehicle_ids)

            s_equipments = ''
            for equipment in service.equipment_ids:
                s_equipments += equipment.name + ';\n'
            if s_equipments:
                s_equipments = s_equipments[:-2]
            if len(service.equipment_ids) > max_rows:
                max_rows = len(service.equipment_ids)

            # row height
            if max_rows > 1:
                sheet.set_row(row, 25 * (max_rows - 1))

            # row details
            sheet.write(row, 0, s_start or '', center_style)
            sheet.write(row, 1, s_stop or '', center_style)
            sheet.write(row, 2, s_container or '', left_style)
            sheet.write(row, 3, s_name or '', left_style)
            sheet.write(row, 4, s_state or '', left_style)
            sheet.write(row, 5, s_duration or '', right_style)
            sheet.write(row, 6, s_duration_uom or '', left_style)
            sheet.write(row, 7, s_employees or '', left_style)
            sheet.write(row, 8, s_vehicles or '', left_style)
            sheet.write(row, 9, s_equipments or '', left_style)

            row += 1
        return row

    def _export_pivot(self, workbook, data):

        ids = data['ids']
        services = self.env['service.allocate'].browse(ids)
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']

        # mapped scheduled_start
        datestime_start = sorted(set(services.mapped('scheduled_start')))

        # _todo_ if possible optimized mapped on only date?
        dates_start = []
        for datetime_start in datestime_start:
            date_start = datetime_start.strftime(DEFAULT_SERVER_DATE_FORMAT)
            if date_start not in dates_start:
                dates_start.append(date_start)

        sheet = workbook.add_worksheet(_('Service allocate'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_column(0, 1, 20)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 30, 25)

        bold_style = workbook.add_format({'bold': True,
                                          'font_size': 14,
                                          'bottom': 1})

        title_style = workbook.add_format({'bold': False,
                                           'align': 'center',
                                           'bg_color': '#C0C0C0',
                                           'bottom': 1})

        left_style = workbook.add_format({'bold': False,
                                          'align': 'left',
                                          'valign': 'top'})

        # rows
        row = 0

        #  used to write only one time each record
        already_read = []

        # used to add header
        header = False

        for service in services:
            # header
            if not header:
                header = True
                sheet.write(0, 0, _('Allocated service'), bold_style)
                sheet.write(1, 0, _('From:'), bold_style)
                from_date = date_from[8:10] + '/' + date_from[5:7] + '/' + date_from[:4]
                sheet.write(1, 1, from_date, bold_style)
                sheet.write(2, 0, _('To:'), bold_style)
                to_date = date_to[8:10] + '/' + date_to[5:7] + '/' + date_to[:4]
                sheet.write(2, 1, to_date, bold_style)

                # dates
                col = 3
                for date_start in dates_start:
                    sheet.write(2, col, date_start, title_style)
                    col += 1

            if service.id not in already_read:

                # service in focus
                focus_container = service.service_container_id
                focus_template = service.service_template_id
                focus_start = service.scheduled_start.strftime('%H:%M:%S')
                focus_stop = service.scheduled_stop.strftime('%H:%M:%S')

                # row identification
                row += 3
                s_container = service.service_container_id.name
                s_name = (service.service_template_id.name + '\n' +
                          focus_start + '-' + focus_stop + '\n' +
                          str(service.service_template_id.duration)
                          )

                sheet.write(row, 0, s_container or '', left_style)
                sheet.write(row, 1, s_name or '', left_style)
                sheet.write(row, 2, _('Employees'), left_style)
                sheet.write(row + 1, 2, _('Vehicles'), left_style)
                sheet.write(row + 2, 2, _('Equipments'), left_style)

                # write service
                self._write_service(service, row, sheet, workbook, dates_start)

                # identify record
                already_read.append(service.id)

                for find in services:
                    if focus_container == find.service_container_id and \
                       focus_template == find.service_template_id and \
                       focus_start == find.scheduled_start.strftime('%H:%M:%S') and \
                       focus_stop == find.scheduled_stop.strftime('%H:%M:%S'):

                        if find.id not in already_read:
                            # write service
                            self._write_service(find, row, sheet, workbook, dates_start)

                            # identify record
                            already_read.append(find.id)
        return row

    def _write_service(self, service, row, sheet, workbook, dates_start):

        left_style = workbook.add_format({'bold': False,
                                          'align': 'left',
                                          'valign': 'top'})

        # locate column
        col = 3
        for date_start in dates_start:
            if date_start == service.scheduled_start \
                                    .strftime(DEFAULT_SERVER_DATE_FORMAT):
                break
            col += 1

        # used to set row height
        max_rows = 3

        s_employees = ''
        for employee in service.employee_ids:
            s_employees += employee.name + ';\n'
        if s_employees:
            s_employees = s_employees[:-2]
        if len(service.employee_ids) > max_rows:
            max_rows = len(service.employee_ids)

        s_vehicles = ''
        for vehicle in service.vehicle_ids:
            s_vehicles += vehicle.name + ';\n'
        if s_vehicles:
            s_vehicles = s_vehicles[:-2]
        if len(service.vehicle_ids) > max_rows:
            max_rows = len(service.vehicle_ids)

        s_equipments = ''
        for equipment in service.equipment_ids:
            s_equipments += equipment.name + ';\n'
        if s_equipments:
            s_equipments = s_equipments[:-2]
        if len(service.equipment_ids) > max_rows:
            max_rows = len(service.equipment_ids)

        # row height
        sheet.set_row(row, 20 * max_rows)
        sheet.set_row(row+1, 20 * max_rows)
        sheet.set_row(row+2, 20 * max_rows)

        # row details
        sheet.write(row, col, s_employees or '', left_style)
        sheet.write(row+1, col, s_vehicles or '', left_style)
        sheet.write(row+2, col, s_equipments or '', left_style)
