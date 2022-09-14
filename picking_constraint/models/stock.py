# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

WARNING_MESSAGE = [
    ('no-message', 'No Message'),
    ('warning', 'Warning'),
    ('block', 'Blocking Message')
]


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    other_product_remove = fields.Boolean(string='Limit additional products out of stock')
    move_type_one = fields.Boolean(string='When all products are ready')
    lot_diff_tip = fields.Selection(WARNING_MESSAGE, 'Warning when Use a different serial number', required=True,
                                    default="block")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    move_type = fields.Selection(default='one')

    def _get_product_error_tip(self):
        a_list = []
        b_list = []
        for move in self.move_ids_without_package:
            if move.product_id.tracking == 'serial':
                for line in move.move_line_ids:
                    if (line.product_uom_qty - line.qty_done) > 0 and line.lot_id:
                        a_list.append(line.product_id.name + ':' + line.lot_id.name)
                    elif (line.qty_done - line.product_uom_qty) > 0 and line.lot_id:
                        b_list.append(line.product_id.name + ':' + line.lot_id.name)
        str_tip = ''
        if a_list:
            str_tip += _("""The following system recommended batches are not out of stock""")
            for i in a_list:
                str_tip += ('\n' + i)
        if str_tip:
            str_tip += '\n\n'
        if b_list:
            str_tip += _("""The following batches are not recommended by the system""")
            for i in b_list:
                str_tip += ('\n' + i)
        return str_tip

    def button_validate(self):
        for rec in self:
            if rec.picking_type_id.other_product_remove:
                # 额外产品出库
                product_2 = rec.move_ids_without_package.filtered(lambda r: r.product_uom_qty > 0).mapped('product_id')
                tip_1 = ''
                for i in rec.move_line_ids_without_package:
                    if i.qty_done > 0 and i.product_id not in product_2:
                        tip_1 += i.product_id.display_name + ':' + i.lot_id.name + '\n'
                if tip_1:
                    raise ValidationError(
                        _("""The following additional products cannot be shipped out\n{}""").format(tip_1))
            if rec.picking_type_id.move_type_one:
                # 数量是否充足
                if rec.move_type == 'one':
                    not_assigned = rec.move_ids_without_package.filtered(
                        lambda r: r.state != 'assigned')
                    if not_assigned:
                        tip_2 = ''
                        for i in not_assigned:
                            tip_2 += _("""{}  missing  {}{}\n""").format(i.product_id.display_name,
                                                                     i.product_uom_qty - i.quantity_done,
                                                                     i.product_uom.name)
                        raise ValidationError(
                            _("""Insufficient quantity of the following products\n{}""").format(tip_2))
            if rec.picking_type_id.lot_diff_tip == 'warning':
                # 批次错误
                ctx = self.env.context
                if not ctx.get('ts_con', False):
                    str_tip = rec._get_product_error_tip()
                    if str_tip:
                        str_tip += _("""\n\nWhether to continue to deliver!""")
                        views = self.env.ref('picking_constraint.picking_tip_wizard_form_view')
                        return {
                            'type': 'ir.actions.act_window',
                            'view_type': 'form',
                            'view_mode': 'form, tree',
                            'res_model': 'picking.tip.wizard',
                            'target': 'new',
                            'views': [(views.id, 'form')],
                            'view_id': views.id,
                            'context': {'default_picking_id': self.id, 'default_tip': str_tip, },
                        }
            elif rec.picking_type_id.lot_diff_tip == 'block':
                str_tip = rec._get_product_error_tip()
                if str_tip:
                    raise ValidationError(_(str_tip))

        res = super(StockPicking, self).button_validate()
        return res
