# -*- coding: utf-8 -*-
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Fixed asset report",
    "version": "8.0.1.2.0",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "depends": [
        "fixed_asset",
        "report_aeroo",
    ],
    "data": [
        "wizards/wizard_fixed_asset.xml",
        "reports/report_fixed_asset_ods.xml",
        "reports/report_fixed_asset_xls.xml",
    ],
    "application": False,
    "installable": True,
    "license": "AGPL-3",
}
