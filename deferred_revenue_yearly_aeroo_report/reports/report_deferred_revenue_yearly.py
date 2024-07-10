# -*- coding: utf-8 -*-
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, time

from dateutil.relativedelta import relativedelta
from odoo import api, models


class Parser(models.AbstractModel):
    _inherit = "report.report_aeroo.abstract"
    _name = "deferred_revenue_aeroo_report"

    @api.model
    def aeroo_report(self, docids, data):
        form = data["form"]
        self.year = form["year"]
        category_ids = form["category_ids"]
        categories = self.get_categories(category_ids)
        self = self.with_context(
            get_categories=categories,
            lines=self.get_line,
        )
        return super(Parser, self).aeroo_report(docids, data)    

    def get_year(self):
        return self.yaer

    # def get_salvage_value(self, asset):
    #     salvage_value = 0.0

    #     if asset:
    #         salvage_value = asset.salvage_value

    #     return salvage_value

    # def get_total_value(self, asset):
    #     total_value = 0.0
    #     date_end = datetime(self.year, 12, 31).strftime("%Y-%m-%d")
    #     filtered = asset.depreciation_line_ids.filtered(
    #         lambda x: x.line_date <= date_end and (x.init_entry or x.move_check)
    #     )
    #     if filtered:
    #         sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
    #         sorted = sorteds[0]
    #         total_value = sorted.depreciated_value

    #     return total_value

    def _get_nbv_previous_year(self, deferred_revenue):
        date_end = datetime(self.year - 1, 12, 31).strftime("%Y-%m-%d")
        filtered = deferred_revenue.depreciation_line_ids.filtered(
            lambda x: x.depreciation_date <= date_end and x.move_check
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.depreciation_date), reverse=True)
            sorted = sorteds[0]
            result = sorted.remaining_value
        return result

    def _get_nbv_current_year(self, deferred_revenue):
        date_end = datetime(self.year, 12, 31).strftime("%Y-%m-%d")
        filtered = deferred_revenue.depreciation_line_ids.filtered(
            lambda x: x.depreciation_date <= date_end and x.move_check
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.depreciation_date), reverse=True)
            sorted = sorteds[0]
            result = sorted.remaining_value
        return result

    def _get_dpr_previous_year(self, deferred_revenue):
        date_end = datetime(self.year - 1, 12, 31).strftime("%Y-%m-%d")
        filtered = deferred_revenue.depreciation_line_ids.filtered(
            lambda x: x.depreciation_date <= date_end and x.move_check
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.depreciation_date), reverse=True)
            sorted = sorteds[0]
            result = sorted.depreciated_value
        return result

    def _get_dpr_current_year(self, deferred_revenue):
        date_end = datetime(self.year, 12, 31).strftime("%Y-%m-%d")
        filtered = deferred_revenue.depreciation_line_ids.filtered(
            lambda x: x.depreciation_date <= date_end and x.move_check
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.depreciation_date), reverse=True)
            sorted = sorteds[0]
            result = sorted.depreciated_value
        return result

    # def _get_asset_value(self, asset):
    #     return asset.purchase_value

    def _get_depreciation_amount(self, deferred_revenue, month):
        dt_date_start = datetime(self.year, month, 1)
        date_start = dt_date_start.strftime("%Y-%m-%d")
        date_end = (dt_date_start + relativedelta(months=1, days=-1)).strftime(
            "%Y-%m-%d"
        )
        filtered = deferred_revenue.depreciation_line_ids.filtered(
            lambda x: (
                x.move_check
                and x.depreciation_date >= date_start
                and x.depreciation_date <= date_end
            )
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.depreciation_date), reverse=True)
            for sorted in sorteds:
                result += sorted.amount
        return result

    def get_categories(self, category_ids):
        Category = self.env["account.asset.category"]

        if category_ids:
            categories = Category.browse(category_ids)
        else:
            categories = Category.search([])

        return categories

    def get_line(self, category_id):
        self.lines = []
        DeferredRevenue = self.env["account.asset.asset"]

        date_end = datetime(self.year, 12, 31).strftime("%Y-%m-%d")

        criteria = [
            ("type", "=", "sale"),
            ("date", "<=", date_end),
            ("state", "in", ["open", "close"]),
            ("category_id", "=", category_id),
        ]

        deferred_revenues = DeferredRevenue.search(criteria, order="date")

        if deferred_revenues:
            for deferred_revenue in deferred_revenues:
                no = 1
                convert_dt = datetime.strptime(deferred_revenue.date, "%Y-%m-%d")
                res = {
                    "no": no,
                    "code": deferred_revenue.code,
                    "name": deferred_revenue.name,
                    "acquisition_value": deferred_revenue.value,
                    "vendor": deferred_revenue.partner_id
                    and deferred_revenue.partner_id.commercial_partner_id.name
                    or "-",
                    "start_date": convert_dt.strftime("%d %B %Y"),
                    "age": str(deferred_revenue.method_number),
                    "nbv_previous_year": self._get_nbv_previous_year(deferred_revenue),
                    "dpr_previous_year": self._get_dpr_previous_year(deferred_revenue),
                    "depr1": self._get_depreciation_amount(deferred_revenue, 1),
                    "depr2": self._get_depreciation_amount(deferred_revenue, 2),
                    "depr3": self._get_depreciation_amount(deferred_revenue, 3),
                    "depr4": self._get_depreciation_amount(deferred_revenue, 4),
                    "depr5": self._get_depreciation_amount(deferred_revenue, 5),
                    "depr6": self._get_depreciation_amount(deferred_revenue, 6),
                    "depr7": self._get_depreciation_amount(deferred_revenue, 7),
                    "depr8": self._get_depreciation_amount(deferred_revenue, 8),
                    "depr9": self._get_depreciation_amount(deferred_revenue, 9),
                    "depr10": self._get_depreciation_amount(deferred_revenue, 10),
                    "depr11": self._get_depreciation_amount(deferred_revenue, 11),
                    "depr12": self._get_depreciation_amount(deferred_revenue, 12),
                    "dpr_current_year": self._get_dpr_current_year(deferred_revenue),
                    "nbv_current_year": self._get_nbv_current_year(deferred_revenue),
                }

                self.lines.append(res)
                no += 1

        return self.lines
