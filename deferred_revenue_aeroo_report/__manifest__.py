# -*- coding: utf-8 -*-
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Deferred Revenue Report",
    "version": "11.0.1.0.0",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "depends": [
        "account_deferred_revenue_extra_move",
        "report_aeroo",
    ],
    "data": [
        "wizards/deferred_revenue_report.xml",
        "reports/report_deferred_revenue_ods.xml",
        "reports/report_deferred_revenue_xls.xml",
    ],
    "application": False,
    "installable": True,
    "license": "AGPL-3",
}
