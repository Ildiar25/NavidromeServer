# -*- coding: utf-8 -*-
# Copyright (C) 2025 Joan Pastor
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

# noinspection PyStatementEffect
{
    'name': "Music Manager",
    'version': "1.0.0",
    'category': "Manager",
    'description': """
        This module allows the user to manage a music directory, doing CRUD operations with music files and
        update music metadata with ID3 labels.
    """,
    'author': "Joan Pastor",
    'website': "",
    'depends': [
        "base",
        "web"
    ],
    'assets': {
        'web.assets_backend': [
            'music_manager/static/src/css/styles.css'
        ]
    },
    'data': [
        # Security
        "security/music_manager_groups.xml",
        "security/ir.model.access.csv",

        # Views
        "views/music_manager_album_views.xml",
        "views/music_manager_artist_views.xml",
        "views/music_manager_genre_views.xml",
        "views/music_manager_track_views.xml",

        # Menus
        "views/music_manager_menus.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': "LGPL-3",
}
