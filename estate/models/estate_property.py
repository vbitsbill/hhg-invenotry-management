# -*- coding: utf-8 -*-

from urllib import response
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

import requests
import json


class EstateProperty(models.Model):

    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"
    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price > 0)",
         "The expected price must be strictly positive"),
        ("check_selling_price", "CHECK(selling_price >= 0)",
         "The offer price must be positive"),
    ]

    # ---------------------------------------- Default Methods ------------------------------------

    def _default_date_availability(self):
        return fields.Date.context_today(self) + relativedelta(months=3)

    # --------------------------------------- Fields Declaration ----------------------------------

    # Basic
    name = fields.Char("Title", required=True)
    description = fields.Text("Description")
    postcode = fields.Char("Postcode")
    date_availability = fields.Date(
        "Available From", default=lambda self: self._default_date_availability(), copy=False)
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float("Selling Price", copy=False, readonly=True)
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living Area (sqm)")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer("Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[
            ("N", "North"),
            ("S", "South"),
            ("E", "East"),
            ("W", "West"),
        ],
        string="Garden Orientation",
    )

    # Special
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        string="Status",
        required=True,
        copy=False,
        default="new",
    )
    active = fields.Boolean("Active", default=True)

    # Relational
    property_type_id = fields.Many2one(
        "estate.property.type", string="Property Type")
    user_id = fields.Many2one(
        "res.users", string="Salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one(
        "res.partner", string="Buyer", readonly=True, copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many(
        "estate.property.offer", "property_id", string="Offers")

    # Computed
    total_area = fields.Integer(
        "Total Area (sqm)",
        compute="_compute_total_area",
        help="Total area computed by summing the living area and the garden area",
    )
    best_price = fields.Float(
        "Best Offer", compute="_compute_best_price", help="Best offer received")

    # ---------------------------------------- Compute methods ------------------------------------

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for prop in self:
            prop.total_area = prop.living_area + prop.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for prop in self:
            prop.best_price = max(prop.offer_ids.mapped(
                "price")) if prop.offer_ids else 0.0

    # ----------------------------------- Constrains and Onchanges --------------------------------

    @api.constrains("expected_price", "selling_price")
    def _check_price_difference(self):
        for prop in self:
            if (
                not float_is_zero(prop.selling_price, precision_rounding=0.01)
                and float_compare(prop.selling_price, prop.expected_price * 90.0 / 100.0, precision_rounding=0.01) < 0
            ):
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price! "
                    + "You must reduce the expected price if you want to accept this offer."
                )

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "N"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # ------------------------------------------ CRUD Methods -------------------------------------

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        if not set(self.mapped("state")) <= {"new", "canceled"}:
            raise UserError("Only new and canceled properties can be deleted.")

    # ---------------------------------------- Action Methods -------------------------------------

    def action_sold(self):
        if "canceled" in self.mapped("state"):
            raise UserError("Canceled properties cannot be sold.")
        return self.write({"state": "sold"})

    def action_cancel(self):
        if "sold" in self.mapped("state"):
            raise UserError("Sold properties cannot be canceled.")
        return self.write({"state": "canceled"})

    def action_print_label(self):
        url = "http://192.168.123.102:8080/print"
        payload = json.dumps([
            {
                "type": "TEXT",
                "data": "hello\n",
                "size": 24,
                "width": 0,
                "alignment": 1,
                "style": "BOLD_UNDERLINE"
            },
            {
                "type": "BARCODE",
                "data": "gLI5AzFfo379UAA",
                "size": 10,
                "width": 50,
                "alignment": 0,
                "style": "NONE"
            },
            {
                "type": "QR",
                "data": "abckde",
                "size": 8,
                "width": 0,
                "alignment": 2,
                "style": "NONE"
            },
            {
                "type": "BITMAP",
                "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII=",
                "size": 0,
                "width": 0,
                "alignment": 1,
                "style": "NONE"
            },
            {
                "type": "TEXT",
                "data": "\n",
                "size": 0,
                "width": 0,
                "alignment": 1,
                "style": "NONE"
            },
            {
                "type": "TEXT",
                "data": "end",
                "size": 24,
                "width": 0,
                "alignment": 1,
                "style": "NONE"
            }
        ])

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
