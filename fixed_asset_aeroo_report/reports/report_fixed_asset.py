# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import api, models


class Parser(models.AbstractModel):
    _inherit = "report.report_aeroo.abstract"
    _name = "report.report_fixed_asset"

    @api.model
    def aeroo_report(self, docids, data):
        form = data["form"]
        date = form["date"]
        asset_category_ids = form["asset_category_ids"]
        convert_date = self.get_date(date)
        categ_ids = self.get_category_ids(asset_category_ids, date)
        self = self.with_context(
            get_date=date,
            get_conv_date=convert_date,
            get_category=categ_ids,
            lines=self.get_line,
        )
        return super(Parser, self).aeroo_report(docids, data)

    def get_date(self, date):
        convert_dt = datetime.strptime(date, "%Y-%m-%d")
        return convert_dt.strftime("%d %B %Y")

    def _prepare_criteria_category_asset(self, date):
        criteria = [("date_start", "<=", date), ("state", "in", ["open", "close"])]
        return criteria

    def get_category_asset_ids(self, date):
        obj_fixed_asset = self.env["fixed.asset.asset"]

        criteria = self._prepare_criteria_category_asset(date)

        asset_ids = obj_fixed_asset.search(criteria, order="date_start")

        return asset_ids.mapped("category_id")

    def get_category_ids(self, asset_category_ids, date):
        category_ids = []
        if asset_category_ids:
            obj_fixed_asset_category = self.env["fixed.asset.category"]
            category_ids = obj_fixed_asset_category.browse(asset_category_ids)
        else:
            category_ids = self.get_category_asset_ids(date)
        return category_ids

    def get_salvage_value(self, asset):
        salvage_value = 0.0

        if asset:
            salvage_value = asset.salvage_value

        return salvage_value

    def get_total_value(self, date, asset):
        total_value = 0.0
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= date and (x.init_entry or x.move_check)
        )
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            sorted = sorteds[0]
            total_value = sorted.depreciated_value + sorted.amount

        return total_value

    def _prepare_criteria_asset(self, date, category_id):
        criteria = [
            ("date_start", "<=", date),
            ("state", "in", ["open", "close"]),
            ("category_id", "=", category_id),
        ]
        return criteria

    def get_line(self, date, category_id):
        lines = []
        no = 1
        obj_fixed_asset = self.env["fixed.asset.asset"]

        criteria = self._prepare_criteria_asset(date, category_id)

        asset_ids = obj_fixed_asset.search(criteria, order="date_start")

        if asset_ids:
            for asset in asset_ids:
                convert_dt = datetime.strptime(asset.date_start, "%Y-%m-%d")
                salvage_value = self.get_salvage_value(asset)
                total_value = self.get_total_value(date, asset)
                asset_value = asset.purchase_value - salvage_value - total_value
                res = {
                    "no": no,
                    "code": asset.code,
                    "name": asset.name,
                    "acquisition_value": asset.purchase_value,
                    "start_date": convert_dt.strftime("%d %B %Y"),
                    "age": asset.method_number,
                    "salvage_value": salvage_value,
                    "total_value": total_value,
                    "asset_value": asset_value,
                }

                lines.append(res)
                no += 1

        return lines
