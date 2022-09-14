# -*- coding: utf-8 -*-
{
    'name': "捡货优化",
    'summary': """
        捡货优化
    """,
    'description': """
        所有产品就绪才能交货
        额外的产品移动不能验证
        捡货时批次不一致，系统有提示
    """,
    'author': "simon",
    'category': 'Uncategorized',
    'version': '15.0',
    'depends': ['sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock.xml',
        'wizard/picking_tip.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
