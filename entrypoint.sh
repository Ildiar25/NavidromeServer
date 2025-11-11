#!/bin/bash

# Settings
DB_NAME="${POSTGRES_DB}"
DB_USER="${POSTGRES_USER}"
DB_HOST="database"
DB_PASSWORD="${POSTGRES_PASSWORD}"

echo -e "\n⏳ Waiting for PostgreSQL to start on host '$DB_HOST'..."

RETRIES=10
until PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USER" -h "$DB_HOST" -d postgres -c '\q' 2>/dev/null; do
    RETRIES=$((RETRIES-1))
    if [ $RETRIES -le 0 ]; then
        echo "❌ PostgreSQL not reachable after multiple attempts. Exiting..."
        exit 1
    fi
    echo "🔄 Still waiting for PostgreSQL... ($RETRIES retries left)"
    sleep 5
done

echo "✅ PostgreSQL is ready!"

# Entrypoint with extra commands
if [ -n "$1" ]; then
    echo -e "\n⚙️  Ejecutando comando personalizado: $*\n"
    exec odoo -c /etc/odoo/odoo.conf "$@"
    exit $?
fi


# Odoo database checking

echo -e "\n🔍  Checking if Odoo database '$DB_NAME' exists..."

DB_EXIST=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USER" -h "$DB_HOST" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'")

# Odoo execute
if [ "$DB_EXIST" = "1" ]; then
    echo "✅  Database already exists. Checking if Odoo is installed..."

    DB_INIT=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USER" -h "$DB_HOST" -d "$DB_NAME" -tAc "SELECT 1 FROM pg_tables WHERE tablename = 'ir_module_module'")

    if [ "$DB_INIT" = "1" ]; then
        echo -e "✅  Odoo DB already initialized. Starting Odoo...\n"
        exec odoo -c /etc/odoo/odoo.conf --without-demo=all
    else
        echo -e "⚠️  DB exists but not initialized. Running -i base...\n"
        odoo -c /etc/odoo/odoo.conf -d "$DB_NAME" -i base --without-demo=all --stop-after-init
        echo -e "\n🚀  Initial DB created. Now starting Odoo normally...\n"
        exec odoo -c /etc/odoo/odoo.conf --without-demo=all
    fi

else
    echo -e "🆕  Database not found. Initializing...\n"
    odoo -c /etc/odoo/odoo.conf -d "$DB_NAME" -i base --without-demo=all --stop-after-init

    echo "🚀  Initial DB created. Now starting Odoo normally..."
    exec odoo -c /etc/odoo/odoo.conf --without-demo=all
fi
