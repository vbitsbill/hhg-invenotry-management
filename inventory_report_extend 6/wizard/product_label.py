from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CustomProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    print_format = fields.Selection(selection_add=[
        # ('2x7', '2 x 7 without price'),
        ('4x8', '4 x 8 without price'),
    ],
        ondelete={
        # '2x7': 'set default',
        '4x8': 'set default'
    }
    )

    def action_print_label(self):
        return True
