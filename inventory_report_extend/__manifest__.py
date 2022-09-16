# -*- coding: utf-8 -*-
{
    'name': "Print Barcode",
    'depends': ['base', 'product', 'stock'],
    'category': 'Uncategorized',
    'summary': """
        Print Barcode
    """,
    'description': """

    """,
    'author': "john",
    'version': '15.0',
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'report/product_product_templates.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
