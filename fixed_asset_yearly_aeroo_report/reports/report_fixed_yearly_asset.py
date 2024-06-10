# -*- coding: utf-8 -*-
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, time

from dateutil.relativedelta import relativedelta
from odoo import api, models


class Parser(models.AbstractModel):
    _inherit = "report.report_aeroo.abstract"
    _name = "report.report_fixed_asset"

    @api.model
    def aeroo_report(self, docids, data):
        form = data["form"]
        self.year = form["year"]
        asset_category_ids = form["asset_category_ids"]
        categories = self.get_asset_categories(asset_category_ids)
        self = self.with_context(
            get_categories=categories,
            lines=self.get_line,
        )
        return super(Parser, self).aeroo_report(docids, data)    

    def get_year(self):
        return self.yaer

    def get_salvage_value(self, asset):
        salvage_value = 0.0

        if asset:
            salvage_value = asset.salvage_value

        return salvage_value

    def get_total_value(self, asset):
        total_value = 0.0
        date_end = datetime(self.year, 12, 31).strftime("%Y-%m-%d")
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= date_end and (x.init_entry or x.move_check)
        )
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            sorted = sorteds[0]
            total_value = sorted.depreciated_value

        return total_value

    def _get_nbv_previous_year(self, asset):
        date_end = datetime(self.year - 1, 12, 31).strftime("%Y-%m-%d")
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= date_end and (x.init_entry or x.move_check)
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            sorted = sorteds[0]
            result = sorted.remaining_value
        return result

    def _get_nbv_current_year(self, asset):
        date_end = datetime(self.year, 12, 31).strftime("%Y-%m-%d")
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= date_end and (x.init_entry or x.move_check)
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            sorted = sorteds[0]
            result = sorted.remaining_value
        return result

    def _get_dpr_previous_year(self, asset):
        date_end = datetime(self.year - 1, 12, 31).strftime("%Y-%m-%d")
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= date_end and (x.init_entry or x.move_check)
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            sorted = sorteds[0]
            result = sorted.depreciated_value + sorted.amount
        return result

    def _get_dpr_current_year(self, asset):
        date_end = datetime(self.year, 12, 31).strftime("%Y-%m-%d")
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= date_end and (x.init_entry or x.move_check)
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            sorted = sorteds[0]
            result = sorted.depreciated_value + sorted.amount
        return result

    def _get_asset_value(self, asset):
        return asset.purchase_value

    def _get_depreciation_amount(self, asset, month):
        dt_date_start = datetime(self.year, month, 1)
        date_start = dt_date_start.strftime("%Y-%m-%d")
        date_end = (dt_date_start + relativedelta(months=1, days=-1)).strftime(
            "%Y-%m-%d"
        )
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: (
                x.init_entry
                and x.line_date >= date_start
                and x.line_date <= date_end
                and (x.type == "depreciate" or x.type == "remove")
            )
            or (
                x.move_check
                and x.move_id.date >= date_start
                and x.move_id.date <= date_end
                and (x.type == "depreciate" or x.type == "remove")
            )
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            for sorted in sorteds:
                result += sorted.amount
        return result

    def get_asset_categories(self, asset_category_ids):
        AssetCategory = self.env["fixed.asset.category"]

        if asset_category_ids:
            categories = AssetCategory.browse(asset_category_ids)
        else:
            categories = AssetCategory.search([])

        return categories

    def get_line(self, category_id):
        self.lines = []
        FixedAsset = self.env["fixed.asset.asset"]

        date_end = datetime(self.year, 12, 31).strftime("%Y-%m-%d")

        #TODO
        criteria = [
            ("date_start", "<=", date_end),
            ("state", "in", ["open", "close", "removed"]),
            ("category_id", "=", category_id),
        ]

        assets = FixedAsset.search(criteria, order="date_start")

        if assets:
            for asset in assets:
                no = 1
                convert_dt = datetime.strptime(asset.date_start, "%Y-%m-%d")
                res = {
                    "no": no,
                    "code": asset.code,
                    "name": asset.name,
                    "acquisition_value": asset.purchase_value,
                    "vendor": asset.partner_id
                    and asset.partner_id.commercial_partner_id.name
                    or "-",
                    "start_date": convert_dt.strftime("%d %B %Y"),
                    "age": str(asset.method_number) + " " + asset.method_time,
                    "salvage_value": asset.salvage_value,
                    "nbv_previous_year": self._get_nbv_previous_year(asset),
                    "dpr_previous_year": self._get_dpr_previous_year(asset),
                    "depr1": self._get_depreciation_amount(asset, 1),
                    "depr2": self._get_depreciation_amount(asset, 2),
                    "depr3": self._get_depreciation_amount(asset, 3),
                    "depr4": self._get_depreciation_amount(asset, 4),
                    "depr5": self._get_depreciation_amount(asset, 5),
                    "depr6": self._get_depreciation_amount(asset, 6),
                    "depr7": self._get_depreciation_amount(asset, 7),
                    "depr8": self._get_depreciation_amount(asset, 8),
                    "depr9": self._get_depreciation_amount(asset, 9),
                    "depr10": self._get_depreciation_amount(asset, 10),
                    "depr11": self._get_depreciation_amount(asset, 11),
                    "depr12": self._get_depreciation_amount(asset, 12),
                    "dpr_current_year": self._get_dpr_current_year(asset),
                    "nbv_current_year": self._get_nbv_current_year(asset),
                }

                self.lines.append(res)
                no += 1

        return self.lines
