import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-open-synergy-opnsynid-fixed-asset-aeroo-report",
    description="Meta package for open-synergy-opnsynid-fixed-asset-aeroo-report Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-deferred_revenue_aeroo_report',
        'odoo11-addon-deferred_revenue_yearly_aeroo_report',
        'odoo11-addon-fixed_asset_aeroo_report',
        'odoo11-addon-fixed_asset_yearly_aeroo_report',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
