# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import datetime


class PickingTipWizard(models.TransientModel):
    _name = 'picking.tip.wizard'
    _description = 'picking tip'

    picking_id = fields.Many2one('stock.picking', string='picking')
    tip = fields.Text(string='tip')

    def active_create_purchsdfase_order(self):
        action = self.picking_id.with_context(ts_con=True).button_validate()
        return action
