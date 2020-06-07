from odoo import models, api, fields, _
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError

import datetime


class AllocateService(models.TransientModel):
    _name = 'xlsx.allocate.service.wizard'

    layout_report = fields.Selection(
        [('list', 'List'),
         ('pivot', 'Pivot')
         ],
        'Layout',
        default='pivot'
    )

    d_start = datetime.datetime.now()
    d_end = d_start + datetime.timedelta(days=7)

    date_from = fields.Date(string='From date',
                            default=d_start.strftime(DEFAULT_SERVER_DATE_FORMAT))
    date_to = fields.Date(string='To date',
                          default=d_end.strftime(DEFAULT_SERVER_DATE_FORMAT))

    @api.multi
    def generate_report(self):
        if self.date_from > self.date_to or self.date_to < self.date_from:
            raise UserError(_('Date range is inconsistent.'))

        domain = [
            ('scheduled_start', '>=', self.date_from),
            ('scheduled_start', '<=', self.date_to),
        ]

        service_list = self.env['service.allocate'].search(
            domain, order='service_container_id,service_template_id,scheduled_start')

        if not service_list:
            raise UserError(_('There are not data to show.'))

        datas = {
            'ids': service_list.ids,
            'model': 'service.allocate',
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'layout_report': self.layout_report,
            }
        }

        return self.env.ref('hr_duty_planner.xlsx_allocated_service').\
            report_action(self, data=datas, config=False)
