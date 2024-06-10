# -*- coding: utf-8 -*-
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class WizardFixedAssetYearly(models.TransientModel):
    _name = "account.wizard_fixed_asset_yearly"
    _description = "Print Yearly Asset Report"

    year = fields.Integer(
        string="Year",
        required=True,
    )
    asset_category_ids = fields.Many2many(
        string="Asset Category",
        comodel_name="fixed.asset.category",
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
        data = {"model": "fixed.asset.asset", "form": self.read()[0]}
        report_name = "fixed_asset_yearly_aeroo_report.report_account_fixedAssetYearlyXLS"
        return self.env.ref(report_name).report_action(self, data=data)

    @api.multi
    def action_print_ods(self):
        data = {"model": "fixed.asset.asset", "form": self.read()[0]}
        report_name = "fixed_asset_yearly_aeroo_report.report_account_fixedAssetYearlyODS"
        return self.env.ref(report_name).report_action(self, data=data)

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
