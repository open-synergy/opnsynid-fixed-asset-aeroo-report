# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class Parser(models.AbstractModel):
    _inherit = "report.report_fixed_asset"
    _name = "report.report_fixed_asset_ods"
