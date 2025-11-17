#!/bin/bash

# Project root
ROOT_DIR="$(dirname "$0")"

# Necessary directories
NAVIDROME_DIR="${ROOT_DIR}/data/navidrome"
ODOO_DIR="${ROOT_DIR}/data/odoo_files"
POSTGRES_DIR="${ROOT_DIR}/data/postgres_db"
MUSIC_DIR="${ROOT_DIR}/music"

# Determine whether to use sudo (not present in most containers; also unnecessary as root)
if command -v sudo >/dev/null 2>&1 && [ "$(id -u)" != "0" ]; then
    SUDO="sudo"
else
    SUDO=""
fi


echo -e "\n📦️  Preparing persistent volumes..."

# Navidrome -> user_id:1000 | group_id:1000
if [ ! -d "$NAVIDROME_DIR" ]; then
    echo "  ➡️  Creating $NAVIDROME_DIR dir!"
    mkdir -p "$NAVIDROME_DIR"

    echo -e "Setting NAVIDROME permissions! 💿️ \n"
    $SUDO chown 1000:1000 "$NAVIDROME_DIR"
fi

# Odoo -> user_id:101 | group_id:101
if [ ! -d "$ODOO_DIR" ]; then
    echo "  ➡️  Creating $ODOO_DIR dir!"
    mkdir -p "$ODOO_DIR"

    echo -e "Setting ODOO permissions! 🟣 \n"
    $SUDO chown 101:101 "$ODOO_DIR"
fi

# Postgres -> user_id:999 | group_id:999
if [ ! -d "$POSTGRES_DIR" ]; then
    echo "  ➡️  Creating $POSTGRES_DIR dir!"
    mkdir -p "$POSTGRES_DIR"

    echo -e "Setting POSTGRES permissions! 🐘 \n"
    $SUDO chown 999:999 "$POSTGRES_DIR"
fi

# Music directory -> Owner = Odoo(101:101) | Read permissions = 755
if [ ! -d "$MUSIC_DIR" ]; then
    echo "  ➡️  Creating $MUSIC_DIR dir!"
    mkdir -p "$MUSIC_DIR"

    echo -e "Setting MUSIC permissions! 🎵 \n"
    $SUDO chown 101:101 "$MUSIC_DIR"
    $SUDO chmod 755 "$MUSIC_DIR"
fi

echo -e "✅️  All volumes are ready!\n"
