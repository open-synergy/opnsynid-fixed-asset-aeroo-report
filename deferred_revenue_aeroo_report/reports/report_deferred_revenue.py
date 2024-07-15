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
        category_ids = form["category_ids"]
        deferred_revenues = self.get_deferred_revenue(category_ids)
        self = self.with_context(
            get_deferred_revenue=deferred_revenues,
            # get_line=self.get_line,
        )
        return super(Parser, self).aeroo_report(docids, data)    

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

    def get_deferred_revenue(self, category_ids):
        Category = self.env["account.asset.category"]
        DeferredRevenue = self.env["account.asset.asset"]
        DeferredRevenueLine = self.env["account.asset.depreciation.line"]
        self.deferred_revenues = []
        criteria = [
            ("asset_id.type", "=", "sale"),
            ("asset_id.state", "in", ["open", "close"]),
            ("move_check", "=", True),
        ]
        if category_ids:
            criteria  += [
                ("asset_id.category_id", "in", category_ids),
            ]

        deferred_revenues = DeferredRevenueLine.search(criteria, order="asset_id, depreciation_date")

        if deferred_revenues:
            current = False
            for deferred_revenue in deferred_revenues:
                
                no = 1
                convert_dt = datetime.strptime(deferred_revenue.asset_id.date, "%Y-%m-%d")
                extra_amount = 0.0
                if deferred_revenue.asset_id.extra_move_id:
                    if deferred_revenue.asset_id.extra_move_id.line_ids[0].debit > 0.0:
                        extra_amount = deferred_revenue.asset_id.extra_move_id.line_ids[0].debit
                    else:
                        extra_amount = deferred_revenue.asset_id.extra_move_id.line_ids[0].credit
                if current == deferred_revenue.asset_id:
                    res = {
                        "no": no,
                        "start_date": "",
                        "invoice_number": "",
                        "client": "",      
                        "category": "",
                        "gross_value": "",
                        "residual_value": "",
                        "extra_accounting_entry": "",  
                        "extra_accounting_entry_amount": "",
                        "age": "",
                        "depreciation_date": deferred_revenue.depreciation_date,
                        "depreciation_entry": deferred_revenue.move_id.name,
                        "depreciation_entry_amount": deferred_revenue.amount,
                    }
                else:
                    res = {
                        "no": no,
                        "start_date": deferred_revenue.asset_id.date,
                        "invoice_number": deferred_revenue.asset_id.invoice_id and deferred_revenue.asset_id.invoice_id.number or "-",
                        "client": deferred_revenue.asset_id.partner_id
                        and deferred_revenue.asset_id.partner_id.commercial_partner_id.name
                        or "-",      
                        "category": deferred_revenue.asset_id.category_id.name,
                        "gross_value": deferred_revenue.asset_id.value,
                        "residual_value": deferred_revenue.asset_id.value_residual,
                        "extra_accounting_entry": deferred_revenue.asset_id.extra_move_id and deferred_revenue.asset_id.extra_move_id.name or "-",  
                        "extra_accounting_entry_amount": extra_amount,
                        "age": str(deferred_revenue.asset_id.method_number),
                        "depreciation_date": deferred_revenue.depreciation_date,
                        "depreciation_entry": deferred_revenue.move_id.name,
                        "depreciation_entry_amount": deferred_revenue.amount,
                    }                    

                self.deferred_revenues.append(res)
                current = deferred_revenue.asset_id
                no += 1        


        return self.deferred_revenues

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
