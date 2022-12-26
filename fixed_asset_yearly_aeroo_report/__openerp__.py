# -*- coding: utf-8 -*-
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Fixed Asset Yearly report",
    "version": "8.0.1.0.5",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "depends": [
        "fixed_asset_aeroo_report",
    ],
    "data": [
        "wizards/wizard_fixed_yearly_asset.xml",
        "reports/report_fixed_asset_yearly_ods.xml",
        "reports/report_fixed_asset_yearly_xls.xml",
    ],
    "application": False,
    "installable": True,
    "license": "AGPL-3",
}
