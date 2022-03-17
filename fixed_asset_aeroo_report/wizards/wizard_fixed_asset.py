# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _


class WizardFixedAsset(models.TransientModel):
    _name = "account.wizard_fixed_asset"
    _description = "Print Asset"

    @api.model
    def _default_date(self):
        return fields.Date.today()

    date = fields.Date(
        string="Date",
        required=True,
        default=lambda self: self._default_date(),
    )
    asset_category_ids = fields.Many2many(
        string="Asset Category",
        comodel_name="fixed.asset.category",
        relation="rel_report_fixed_asset_2_category",
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
        data = {"model": "account.asset.asset", "form": self.read()[0]}
        report_name = "fixed_asset_aeroo_report.report_account_fixedAssetXLS"
        return self.env.ref(report_name).report_action(self, data=data)

    @api.multi
    def action_print_ods(self):
        data = {"model": "account.asset.asset", "form": self.read()[0]}
        report_name = "fixed_asset_aeroo_report.report_account_fixedAssetODS"
        return self.env.ref(report_name).report_action(self, data=data)

    @api.multi
    def button_print_report(self):
        self.ensure_one()

        if self.output_format == "ods":
            result = self.action_print_ods()
        elif self.output_format == "xls":
            result = self.action_print_xls()
        else:
            strError = _("No Output Format Selected")
            raise UserError(strError)

        return result
