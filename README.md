<a id="readme-top"></a>

# 🎵 Gestor de Música (Módulo Odoo & Navidrome) — v.1.0.0

Este proyecto integra **Odoo 17** con **Navidrome** para la gestión centralizada de música y metadatos, incluyendo un 
módulo personalizado llamado `music_manager`. Centraliza la gestión de artistas, álbumes y canciones en Odoo, mientras 
Navidrome gestiona la reproducción y el streaming. <br/>
Dicho módulo permite crear, editar y administrar tu catálogo musical directamente desde Odoo.

Puedes ver el *roadmap* aquí: <br/>
[![Static Badge](https://img.shields.io/badge/Music_Manager_(Roadmap)-FB9820?logo=maplibre&labelColor=black)](addons/music_manager/docs/roadmap.md)


Y el proyecto completo aquí: <br/>
[![Static Badge](https://img.shields.io/badge/Music_Manager_v.1.0.0-4285F4?logo=readthedocs&labelColor=black)]()

<!-- Tabla de contenido -->
<details>
	<summary>Índice</summary>
	<ol>
		<li><a href="#tecnologías">Tecnologías</a></li>
		<ul>
            <li><a href="#como-agregar-canciones">Tecnologías</a></li>
        </ul>
	</ol>
</details>

---

## 🧰 Tecnologías

- 🐳 **Docker & Docker Compose** — Orquestación de contenedores.
- 🐘 **PostgreSQL** — Base de datos principal de Odoo.
- 🟣 **Odoo 17** — Framework ERP y backend principal.
- 🎧 **Navidrome** — Servidor de música ligero compatible con Subsonic.

<p align="right"><a href="#readme-top">Volver ⏫</a></p>

## 📘 Guía de usuario

*Esta guía te mostrará las características de este proyecto con diferentes ejemplos GIF*

### Cómo agregar canciones

...

---

### Cómo actualizar los metadatos

...

---

### Cómo añadir imágenes

...

---

### Cómo actualizar varias canciones

...

---

### Cómo eliminar registros

...

<p align="right"><a href="#readme-top">Volver ⏫</a></p>

---

## ⚙️ Guía de instalación

Primero, asegúrate de tener **Python v.3.12.0** o superior, **Git v.2.45.2** o superior y **Docker v.28.4.0** o 
superior instalados en tu sistema. <br/>
Puedes descargarlos desde los siguientes enlaces:

[![Static Badge](https://img.shields.io/badge/Descargar_Python-3776AB?logo=python&labelColor=black)](https://www.python.org/downloads/)
[![Static Badge](https://img.shields.io/badge/Descargar_Git-F05032?logo=git&labelColor=black)](https://git-scm.com/downloads)
[![Static Badge](https://img.shields.io/badge/Descargar_Docker-2496ED?logo=docker&labelColor=black)](https://www.docker.com/)

### 🔹 Crea tu carpeta principal

Abre tu editor IDE favorito, crea una carpeta donde almacenar el proyecto y navega a su interior:
```
# Create new folder
mkdir <new_folder>

# Navigate into it
cd <new_folder>
```

---

### 🔹 Clona el repositorio

Una vez estés dentro de la carpeta nueva, clona el repositorio con el siguiente comando:
```bash
git clone https://github.com/Ildiar25/NavidromeServer
```
Esta acción creará una nueva carpeta llamada `NavidromeServer`. Entra en ella con el comando `cd NavidromeServer`.

---

### 🔹 Crea el entorno virtual

Ahora necesitarás crear el entorno virtual, para ello utilizaremos la librería `venv`:
```bash
python -m venv .venv
```
Una vez creado, deberás activarlo de dependiendo de tu sistema operativo.

**Desde PowerShell (Windows)**
```bash
.venv\Scripts\Activate.ps1
```

**Desde CMD (Windows)**
```bash
.venv\Scripts\Activate.bat
```

> [!IMPORTANT]
> **Windows** puede dar problemas al intentar ejecutar un *Script* sin los permisos necesarios!
> ```
> + .venv/Scripts/Activate.ps1
> + ~~~~~~~~~~~~~~~~~~~~~~~~~~
>     + CategoryInfo          : SecurityError: (:) [], PSSecurityException
>     + FullyQualifiedErrorId : UnauthorizedAccess
> ```

Esto ocurre porque **Windows** trae la ejecución de *Scripts* desactivada por defecto. <br/>
Puedes solucionar el problema abriendo el **PowerShell** de **Windows** en modo *Administrador* y ejecutando el
siguiente comando:
```bash
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted
```

> [!CAUTION]
> Esta acción permitirá que cualquier script de **PowerShell** se ejecute, sin importar si ha sido firmado digitalmente 
> o si no es de una fuente confiable. Esto es útil para desarrolladores o administradores que necesitan ejecutar 
> scripts locales sin bloqueos, pero también puede ser un riesgo si ejecutas accidentalmente un script malicioso.
> ¡Utilízalo solo bajo tu propio criterio!

Ahora ya puedes activar tu entorno virtual.

**Desde Terminal (Linux)**
```bash
source .venv/bin/activate
```

---

### 🔹 Instalar dependencias

Este proyecto utiliza sus propias dependencias que se pueden encontrar en el archivo `requirements.txt`. Los puedes 
instalar automáticamente ejecutando el siguiente comando:
```bash
pip install -r requirements.txt
```
> [!TIP]
> Aunque este proyecto utiliza una imagen de Odoo en Docker, puedes descargar el proyecto original desde su web 
> [Odoo](https://www.odoo.com/documentation/17.0/developer/tutorials/setup_guide.html) y utilizarlo como carpeta de 
> recursos para facilitar el tipado y el autocompletado.

---

### 🔹 Configurar y levantar los contenedores (Compatibilidad Linux vs. Windows)

Para facilitar el despliegue del proyecto, se incluyen dos archivos que manejan el mismo según el sistema operativo. 
Se puede encontrar un `Makefile` que muestra los comandos necesarios para **Linux** y un módulo de **PowerShell** 
llamado `Utils.psm1` para **Windows**.

#### Windows

 * No se requieren permisos especiales.
 * Si las carpetas no existen, **Docker Compose las crea automáticamente** al levantar los contenedores.
 * No es necesario ejecutar ningún script adicional.

Primero importamos el módulo:
```bash
Import-Module ./Utils.psm1

```

```
# Lista de comandos disponibles

⚠  NOTICE: All next commands are for Windows

DkDown               Stop docker services
DkInit               Prepare docker
DkRestart            Restart docker services
DkUp                 Start docker services
GitCommit            Create new commit
GitInit              Do first commit & push-it
Help                 Show this help
Venv                 Create new virtual environment
```

Después, utilizamos los scripts necesarios
```bash
DkUp
```

#### Linux

 * Las carpetas necesarias (`./data/*` y `./music`) **deben existir antes de levantar Docker**.
 * El archivo `permissions.sh` se encarga de crearlas y asignar los permisos correctos a cada contenedor para evitar errores de *permission denied*.
 * Utilizaremos el propio `makefile` integrado.

```bash
make dkup
```

Para ambos casos esto levantará:

 * Base de datos PostgreSQL.
 * Odoo con configuración personalizada y módulo `music_manager`.
 * Navidrome, apuntando al directorio de música.

---

### 🔹 Acceso

Una vez los contenedores estén operativos, se podrá acceder a los servicios gracias a la siguiente tabla:

| Servicio  | URL                                             | Usuario inicial                      |
|-----------|-------------------------------------------------|--------------------------------------|
| Odoo      | [http://localhost:8069](http://localhost:8069)  | `admin` / `admin` (por defecto)      |
| Navidrome | [http://localhost:4533](http://localhost:4533)  | `admin` (definir en primer arranque) |

<p align="right"><a href="#readme-top">Volver ⏫</a></p>

---

## 📁 Estructura

La estructura principal del proyecto se puede observar en el siguiente árbol:
```
├── addons/                 # Directorio de addons extra (incluye el módulo principal music_manager).
├── data/                   # Datos persistentes (db, configs, etc.).
├── dockerfile.odoo         # Imagen customizada de Odoo.
├── entrypoint.sh           # Script de entrada para la inicialización de la base de datos.
├── permissions.sh          # Script de creación de carpetas y asignación de permisos (Linux).
├── compose.yaml            # Docker Compose config.
├── requirements.txt        # Requisitos Python adicionales para Odoo.
└── README.md               # Este archivo.
```

<p align="right"><a href="#readme-top">Volver ⏫</a></p>

---

## 💿 Música

> [!WARNING]
> El directorio `./music` no debe ser modificado manualmente!

Los datos agregados desde Odoo se almacenarán en el directorio compartido entre servicios llamado `music`. Este 
directorio será escaneado por Navidrome cada hora para buscar cambios en el mismo y que queden reflejados en su base 
de datos.

 * Toda la música será gestionada automáticamente desde el módulo **Music Manager** de Odoo.
 * Este módulo se encarga de subir archivos desde Odoo, descargar desde URL's externas (como YouTube), y organizar los directorios.

<p align="right"><a href="#readme-top">Volver ⏫</a></p>

---

## 🧹 Reseteo completo (desarrollo)

Si quieres limpiar todo y empezar de cero:

```bash
docker compose down
rm -rf ./data/*
docker volume prune -f
```

Y volver al punto de [configuración]().

<p align="right"><a href="#readme-top">Volver ⏫</a></p>

---

## ✨ Módulo Music Manager

La descripción detallada del módulo `music_manager` está en su [README](addons/music_manager/README.md).

<p align="right"><a href="#readme-top">Volver ⏫</a></p>

---

## 📝 Licencia

Este proyecto está licenciado bajo la licencia **GNU LGPL v3.0**.
Puedes ver el archivo [`LICENSE`](LICENSE.txt) para más detalles.

<p align="right"><a href="#readme-top">Volver ⏫</a></p>

---

## 🤝 Créditos y licencias de dependencias

 * **Odoo**: LGPL-3.0
 * **Navidrome**: GPL-3.0 (se utiliza como servicio externo, no modificado)

<p align="right"><a href="#readme-top">Volver ⏫</a></p>

---

## Para más información

<div style="center">
    <img src="https://avatars.githubusercontent.com/u/147839908?v=4" alt="Avatar" hspace="20" vspace="10" style="width:100px; height:100px; border-radius:25%; float: left;">
    <p>
        ¡Hola! ¡Mi nombre es Joan y este es mi segundo gran proyecto! Estoy estudiando programación desde 2024, habiendo 
        empezado con Python. Estoy más que contento de poder compartir con todos vosotros mi progreso y mis ideas. Espero 
        que disfrutes del proyecto tanto como yo disfruté al programarlo y si quieres darme feedback, por favor, siéntete 
        libre de hacerlo porque es muy importante para mí. ¡Nos vemos en el siguiente proyecto! <br/>
        ¡Un abrazo!
    </p>
</div>

<br/>
<br/>
Joan <br/>
PD: ¡Te dejo enlaces de interés aquí abajo!

[![Static Badge](https://img.shields.io/badge/Pregunta_a_DeepWiki-3A6ACE?logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAMAAAAolt3jAAAA3lBMVEUAAAABk946as4HnNA0e8MBk94gwJk6as4gwJkBk946as46as4Bk94Bk946as4Bk94gwJk6as4Bk94gwJk6as4gwJkBk946as4Bk94gwJk6as4Bk946as4gwJkgwJkBk94gwJk6as4gwJkBk946as4gwJk6as4gwJkgwJkgwJkgwJkBk946as4Bk946as4Bk94gwJk6as4Bk946as4Bk946as4Bk946as4gwJkgwJkBk946as4gwJkgwJkBk94gwJk6as4Bk94Bk94gwJkBk94gwJk6as4Bk94gwJk6as7gjjPaAAAAR3RSTlMAAQEFBQYGBhgdHTAxMzM6OztKSktPUFBSU1N2dnd4hoaHiI2Oj5CRkpOUpqaqqsDBwtPT1NTX2tvc7%2B%2Fw8fr7%2B%2Fz9%2Ff7%2B%2FgHDj5oAAACRSURBVAjXY2AAAyYmBiTAZ2rMh8TV8%2FTUgTLZ1QxVrD09ZUQNVNmAXBFPTwducXEWG1dXYSBX0M3TnENDS87ew1kApFpKkUvdw8NCQEESrFlCnhPItRRQAnP5HZ3MONQ1Ze09XEGKhRxd7HjExJhtPTxARrEq6ytbubtLQy0CAV13d20kV%2FGaGPEiO5qREUIDAEmQEavt%2BU%2FXAAAAAElFTkSuQmCC&labelColor=black)](https://deepwiki.com/Ildiar25/NavidromeServer)
[![Static Badge](https://img.shields.io/badge/Cont%C3%A1ctame-EA4335?logo=gmail&labelColor=black)](mailto:j.pastor1591@gmail.com)
[![Static Badge](https://img.shields.io/badge/Mi_Perfil_Profesional-006699?logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAAA4AAAAPCAMAAADjyg5GAAAAilBMVEUAAAAAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkWaufzAAAALXRSTlMAAQIDEBETFhcgIycqLS4ySVFXWV1fYWpsbXV7iIqQqa20wsXO0tbg4efq8%2F2PFdscAAAAYklEQVQIW5XHyRbBABBFwSciCNos5qCNkfv%2Fv2cVp4%2Bd2pWUJApGz8cwdAfb0MHtmof%2BmLpPUvfD7FKVPamAZRdeNeDfctq%2FYdz03tIR5k3P0grWoQvY%2FNfMrNM260upWfYBxD8QUVv%2BWwcAAAAASUVORK5CYII%3D&labelColor=black)](https://www.linkedin.com/in/joan-pastor-vicens-aa5b4a55)
[![Static Badge](https://img.shields.io/badge/Portfolio-white?logo=github&labelColor=black)](https://github.com/Ildiar25)

See you coding! 😜

<p align="right"><a href="#readme-top">Volver ⏫</a></p>