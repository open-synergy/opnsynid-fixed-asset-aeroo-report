# -*- coding: utf-8 -*-
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, time

from openerp.report import report_sxw


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.no = 1
        self.localcontext.update(
            {
                "time": time,
                "get_date": self.get_date,
                "get_category_ids": self.get_category_ids,
                "line": self.get_line,
            }
        )

    def set_context(self, objects, data, ids, report_type=None):
        self.form = data["form"]
        self.date = self.form["date"]
        self.asset_category_ids = self.form["asset_category_ids"]
        return super(Parser, self).set_context(objects, data, ids, report_type)

    def get_date(self):
        convert_dt = datetime.strptime(self.date, "%Y-%m-%d")
        return convert_dt.strftime("%d %B %Y")

    def get_salvage_value(self, asset):
        salvage_value = 0.0

        if asset:
            salvage_value = asset.salvage_value

        return salvage_value

    def get_total_value(self, asset):
        total_value = 0.0
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= self.date and (x.init_entry or x.move_check)
        )
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            sorted = sorteds[0]
            total_value = sorted.depreciated_value + sorted.amount

        return total_value

    def get_category_asset_ids(self):
        obj_fixed_asset = self.pool.get("account.asset.asset")

        criteria = [("date_start", "<=", self.date), ("state", "in", ["open", "close"])]

        asset_ids = obj_fixed_asset.search(
            self.cr, self.uid, criteria, order="date_start"
        )

        asset = obj_fixed_asset.browse(self.cr, self.uid, asset_ids)

        return asset.mapped("category_id").ids

    def get_category_ids(self):
        obj_asset_category = self.pool.get("account.asset.category")
        category_ids = []

        if self.asset_category_ids:
            category_ids = self.asset_category_ids
        else:
            category_ids = self.get_category_asset_ids()

        category_ids = obj_asset_category.browse(self.cr, self.uid, category_ids)

        return category_ids

    def get_line(self, category_id):
        self.lines = []
        obj_fixed_asset = self.pool.get("account.asset.asset")

        criteria = [
            ("date_start", "<=", self.date),
            ("state", "in", ["open", "close"]),
            ("category_id", "=", category_id),
        ]

        asset_ids = obj_fixed_asset.search(
            self.cr, self.uid, criteria, order="date_start"
        )

        if asset_ids:
            for asset in obj_fixed_asset.browse(self.cr, self.uid, asset_ids):
                convert_dt = datetime.strptime(asset.date_start, "%Y-%m-%d")
                salvage_value = self.get_salvage_value(asset)
                total_value = self.get_total_value(asset)
                asset_value = asset.purchase_value - salvage_value - total_value
                res = {
                    "no": self.no,
                    "code": asset.code,
                    "name": asset.name,
                    "acquisition_value": asset.purchase_value,
                    "start_date": convert_dt.strftime("%d %B %Y"),
                    "age": asset.method_number,
                    "salvage_value": salvage_value,
                    "total_value": total_value,
                    "asset_value": asset_value,
                }

                self.lines.append(res)
                self.no += 1

        return self.lines
