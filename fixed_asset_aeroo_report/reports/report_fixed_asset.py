# -*- coding: utf-8 -*-
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, time

from openerp.report import report_sxw


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.lines = []
        self.localcontext.update(
            {
                "time": time,
                "get_date": self.get_date,
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

    def get_residual_value(self, asset):
        remaining_value = 0.0
        sorted = []
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= self.date and x.init_entry or x.move_check
        )

        if filtered:
            sorted = filtered.sorted(key=lambda s: s.line_date, reverse=True)
            remaining_value = sorted[0].mapped("remaining_value")

        return remaining_value

    def get_total_value(self, asset):
        total_value = 0.0
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= self.date
            and not x.init_entry
            and x.move_check
        )
        if filtered:
            total_value += [x.amount for x in filtered][0]

        return total_value

    def get_line(self):
        obj_fixed_asset = self.pool.get("account.asset.asset")

        criteria = [
            ("date_start", "<=", self.date),
            ("state", "in", ["open", "close"])
        ]

        if self.asset_category_ids:
            criteria = [
                ("category_id", "in", self.asset_category_ids),
            ] + criteria

        asset_ids = obj_fixed_asset.search(
            self.cr, self.uid, criteria, order="date_start"
        )

        if asset_ids:
            no = 1
            for asset in obj_fixed_asset.browse(self.cr, self.uid, asset_ids):
                convert_dt = datetime.strptime(asset.date_start, "%Y-%m-%d")
                res = {
                    "no": no,
                    "code": asset.code,
                    "name": asset.name,
                    "category": asset.category_id.name,
                    "acquisition_value": asset.purchase_value,
                    "start_date": convert_dt.strftime("%d %B %Y"),
                    "age": asset.method_number,
                    "residual_value": self.get_residual_value(asset),
                    "total_value": self.get_total_value(asset),
                    "asset_value": asset.asset_value,
                }

                self.lines.append(res)
                no += 1

        return self.lines