# 🎵 Navidrome Odoo Server

Este proyecto integra **Odoo 17** con **Navidrome** para la gestión centralizada de música y metadatos, incluyendo un módulo personalizado llamado `music_manager`.

## 🚀 Objetivo

Centralizar la gestión de artistas, álbumes y canciones en Odoo, mientras Navidrome gestiona la reproducción y el streaming.  
El módulo `music_manager` permite crear, editar y administrar tu catálogo musical directamente desde Odoo.

---

## 🧰 Tecnologías

- 🐳 **Docker & Docker Compose** — Orquestación de contenedores
- 🐘 **PostgreSQL** — Base de datos principal de Odoo
- 🟠 **Odoo 17** — Framework ERP y backend principal
- 🎧 **Navidrome** — Servidor de música ligero compatible con Subsonic

---

## ⚙️ Instalación

### 1️⃣ Clonar el repositorio

```bash
git clone <url-del-repo>
cd <repo>
```

### 2️⃣ Configurar y levantar los contenedores

```bash
docker compose up --build
```

Esto levantará:

 * Base de datos PostgreSQL
 * Odoo con configuración personalizada y módulo `music_manager`
 * Navidrome, apuntando al directorio de música

### 3️⃣ Acceso

| Servicio  | URL                                            | Usuario inicial                      |
|-----------|------------------------------------------------|--------------------------------------|
| Odoo      | [http://localhost:8069](http://localhost:8069) | `admin` (definir en primer arranque) |
| Navidrome | [http://localhost:4533](http://localhost:4533) | `admin` / `admin` (por defecto)      |

---

## 📁 Estructura

```
├── addons/                 # Directorio de addons extra (incluye music_manager)
├── data/                   # Datos persistentes (db, configs, etc.)
├── dockerfile.odoo         # Imagen customizada de Odoo
├── entrypoint.sh           # Script de entrada para inicialización db
├── compose.yaml            # Docker Compose config
├── requirements.txt        # Requisitos Python adicionales para Odoo
└── README.md               # Este archivo
```

---

## 💿 Música

> [!WARNING]
> El directorio `./music` no debe ser modificado manualmente.

 * Toda la música será gestionada automáticamente por el módulo **Music Manager** de Odoo.
 * Este módulo se encarga de subir archivos desde Odoo, descargar desde URL's externas (como YouTube), y organizar los directorios.
 * Navidrome se encarga de escanear este directorio y actualizar tu biblioteca automáticamente cada hora.

---

## 🧹 Reseteo completo (desarrollo)

Si quieres limpiar todo y empezar de cero:

```bash
docker compose down
rm -rf ./data/*
docker volume prune -f
docker compose up --build
```

---

## ✨ Módulo Music Manager

La descripción detallada del módulo `music_manager` está en su [README](addons/music_manager/README.md).

---

## 📝 Licencia

Este proyecto está licenciado bajo la licencia **GNU LGPL v3.0**.
Puedes ver el archivo [`LICENSE`](LICENSE.txt) para más detalles.

---

## 🤝 Créditos y licencias de dependencias

 * **Odoo**: LGPL-3.0
 * **Navidrome**: GPL-3.0 (se utiliza como servicio externo, no modificado)
