# -*- coding: utf-8 -*-
# Copyright (C) 2025 Joan Pastor
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

# noinspection PyStatementEffect
{
    'name': "Music Manager",
    'version': "1.0",
    'category': "Manager",
    'description': """
        This module allows the user to manage a music directory, doing CRUD operations with music files and
        update music metadata with ID3 labels.
    """,
    'author': "Joan Pastor",
    'website': "",
    'depends': [
        "base",
    ],
    'data': [
        # "security/ir.model.access.csv",
        "security/music_manager_groups.xml",
        # "views/test_views.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': "LGPL-3",
}
