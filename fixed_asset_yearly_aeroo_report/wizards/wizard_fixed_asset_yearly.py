# -*- coding: utf-8 -*-
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class WizardFixedAssetYearly(models.TransientModel):
    _name = "account.wizard_fixed_asset_yearly"
    _description = "Print Yearly Asset Report"

    year = fields.Integer(
        string="Year",
        required=True,
    )
    asset_category_ids = fields.Many2many(
        string="Asset Category",
        comodel_name="account.asset.category",
        relation="rel_report_fixed_asset_yearly_2_category",
        column1="wizard_id",
        column2="asset_category_id",
    )
    output_format = fields.Selection(
        string="Output Format",
        required=True,
        default="ods",
        selection=[("xls", "XLS"), ("ods", "ODS")],
    )

    @api.multi
    def action_print_xls(self):
        datas = {}
        datas["form"] = self.read()[0]
        return {
            "type": "ir.actions.report.xml",
            "report_name": "report_fixed_asset_yearly_xls",
            "datas": datas,
        }

    @api.multi
    def action_print_ods(self):
        datas = {}
        datas["form"] = self.read()[0]
        return {
            "type": "ir.actions.report.xml",
            "report_name": "report_fixed_asset_yearly_ods",
            "datas": datas,
        }

    @api.multi
    def button_print_report(self):
        self.ensure_one()

        if self.output_format == "ods":
            result = self.action_print_ods()
        elif self.output_format == "xls":
            result = self.action_print_xls()
        else:
            raise UserError(_("No Output Format Selected"))

        return result
