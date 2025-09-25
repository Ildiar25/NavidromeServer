<a id="readme-top"></a>

# 🎸 Módulo para Odoo: Music Manager

Módulo personalizado para Odoo que permite **gestionar** y **organizar** tu colección musical según *artistas*, 
*álbumes*, *canciones* y *géneros*. <br/>
Este módulo guía al usuario paso a paso a completar los metadatos de la canción añadida (mediante la carga de un 
archivo o la descarga del mismo) y guarda el archivo final de forma ordenada en la carpeta principal `music`.

Puedes ver la lista de tareas aquí: <br/>
[![Static Badge](https://img.shields.io/badge/Tareas_Pendientes-2684FC?logo=googletasks&labelColor=black)](docs/TODO.md)

---

## 🎯 Objetivo

Mantener el directorio compartido con **Navidrome** (`music`) completamente organizado en carpetas (nombre del 
*artista*, nombre del *álbum*, número de pista y título de la canción) y los metadatos de la canción actualizados 
según los datos proporcionados por el usuario. De esta forma, **Navidrome** puede mostrar una biblioteca ordenada a 
sus clientes. <br/>
También permite que cada usuario tenga una biblioteca de música única (**Odoo**) pero una biblioteca musical 
compartida (**Navidrome**), siendo los usuarios quienes van ampliando la misma.

<p align="right"><a href="#readme-top">Volver ⏫</a></p>

---

## ⚙️ Instalación

Primero, asegúrate de tener **Python v.3.12.0** o superior, **Git v.2.45.2** o superior, **Docker v.28.4.0** o 
superior y **Odoo 17.0** instalados en tu sistema. <br/>
Puedes descargarlos desde los siguientes enlaces:

[![Static Badge](https://img.shields.io/badge/Descargar_Python-3776AB?logo=python&labelColor=black)](https://www.python.org/downloads/)
[![Static Badge](https://img.shields.io/badge/Descargar_Git-F05032?logo=git&labelColor=black)](https://git-scm.com/downloads)
[![Static Badge](https://img.shields.io/badge/Descargar_Docker-2496ED?logo=docker&labelColor=black)](https://www.docker.com/)
[![Static Badge](https://img.shields.io/badge/Descargar_Odoo-714B67?logo=odoo&labelColor=black)](https://www.odoo.com/documentation/17.0/developer/tutorials/setup_guide.html)

> [!NOTE]
> Para instalar el módulo desde el proyecto **NavidromeServer**, sigue los pasos a partir de la 
> [instalación del módulo](#-instalación-del-módulo).

### 🔹 Copia el módulo

En la carpeta `addons/` añade la carpeta del módulo en minúsculas y sustituyendo los espacios por guiones bajos 
(Music Manager → music_manager).

---

### 🔹 Reinicia Odoo

Utilizando la terminal reinicia el sistema con el siguiente comando:
```bash
./odoo-bin -c /etc/odoo/odoo.conf
```

Esto dentendrá todo proceso y volverá a levantar el servidor de **Odoo**.

---

### 🔹 Modo desarrollador

Habilita el modo desarrollador en la página principal de **Odoo** para poder actualizar las aplicaciones.

*Settings* > *Developer Tools* > *Activate the developer mode* > *Apps* > *Update Apps List*

Al realizar este paso, la aplicación debería aparecer en la lista de aplicaciones que se pueden instalar.

![How to activate developer mode](docs/img/developer-mode.gif "Developer mode")

---

### 🔹 Instalación del módulo

Busca la aplicación *Music Manager* y pulsa el botón **Activar**.

![How to activate the app](docs/img/activate-module.gif "Module activation")

Como este módulo crea dos grupos específicos de Usuario, deberás ir a *'Settings'*, y en *'Manage Users'* asignar los 
permisos a cada usuario.

#### Music Manager Admin

 * Permite la eliminación de canciones de la carpeta principal de **Navidrome**.
 * Agrupa las canciones según su propietario.

#### Music Manager User

 * Solo pueden eliminar registros de su base de datos, los archivos físicos se mantienen en la carpeta de **Navidrome**.

> [!IMPORTANT]
> Para poder ver el módulo activo, deberás asignar el grupo a tu usuario. ¡De lo contrario, **Music Manager** 
> no se mostrará! Una vez asignes los roles a los usuarios, tan solo necesitarás refrescar la página.

<p align="right"><a href="#readme-top">Volver ⏫</a></p>

---

## 🧩 Modelos

Los modelos se encargan de representar de forma digital los conceptos dados.

> [!NOTE]
> Puede que los atributos cambien a medida que se van desarrollando los mismos. Por ahora se mostrarán los 
> atributos más genéricos que se pueden encontrar.

En este modelo hemos creado los siguientes

### 👤 Artista

Representa al artista o grupo musical de la canción añadida.

 * Nombre del artista
 * Álbum
 * Descripción
 * Fotografía

### 💿 Álbum

Representa al álbum al que pertenece la canción.

 * Título del álbum
 * Artista
 * Número de disco
 * Año
 * Género
 * Canciones

### 🎵 Canción

Representa la canción en sí misma.

 * Título
 * Artista
 * Género
 * Álbum
 * Número de pista
 * Dirección donde se almacena el archivo

### 🗃️ Género

Representa el género de una canción o álbum

 * Nombre
 * Canción
 * Álbum

<p align="right"><a href="#readme-top">Volver ⏫</a></p>

---

## 🔗 Posibles integraciones futuras

 * Descarga automática de metadatos (por ejemplo, *MusicBrainz*)
 * Configuración de conversión de archivos
 * Soporte para múltiples lenguajes

---

## 📝 Licencia

Este módulo está protegido bajo la licencia **GNU LGPL v3.0**. <br/>
Puedes consultar el archivo [LICENSE](../../LICENSE.txt) para más información.

---

## 💬 Contacto

<div align="center">
    <img src="https://avatars.githubusercontent.com/u/147839908?v=4" alt="Avatar" style="width:120px; height:120px; border-radius:25%;">
</div>

¡Hola! ¡Mi nombre es Joan y este módulo es parte de mi segundo gran proyecto! Estoy estudiando programación desde 2023, 
habiendo empezado con Python. Estoy más que contento de poder compartir con todos vosotros mi progreso y mis ideas. 
Espero que disfrutes del proyecto tanto como yo disfruté al programarlo y si quieres darme feedback, por favor, siéntete 
libre de hacerlo porque es muy importante para mí. ¡Nos vemos en el siguiente proyecto! <br/>
¡Un abrazo! <br/>
<br/>
Joan <br/>
PD: ¡Te dejo enlaces de interés aquí abajo!

[![Static Badge](https://img.shields.io/badge/Pregunta_a_DeepWiki-3A6ACE?logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAMAAAAolt3jAAAA3lBMVEUAAAABk946as4HnNA0e8MBk94gwJk6as4gwJkBk946as46as4Bk94Bk946as4Bk94gwJk6as4Bk94gwJk6as4gwJkBk946as4Bk94gwJk6as4Bk946as4gwJkgwJkBk94gwJk6as4gwJkBk946as4gwJk6as4gwJkgwJkgwJkgwJkBk946as4Bk946as4Bk94gwJk6as4Bk946as4Bk946as4Bk946as4gwJkgwJkBk946as4gwJkgwJkBk94gwJk6as4Bk94Bk94gwJkBk94gwJk6as4Bk94gwJk6as7gjjPaAAAAR3RSTlMAAQEFBQYGBhgdHTAxMzM6OztKSktPUFBSU1N2dnd4hoaHiI2Oj5CRkpOUpqaqqsDBwtPT1NTX2tvc7%2B%2Fw8fr7%2B%2Fz9%2Ff7%2B%2FgHDj5oAAACRSURBVAjXY2AAAyYmBiTAZ2rMh8TV8%2FTUgTLZ1QxVrD09ZUQNVNmAXBFPTwducXEWG1dXYSBX0M3TnENDS87ew1kApFpKkUvdw8NCQEESrFlCnhPItRRQAnP5HZ3MONQ1Ze09XEGKhRxd7HjExJhtPTxARrEq6ytbubtLQy0CAV13d20kV%2FGaGPEiO5qREUIDAEmQEavt%2BU%2FXAAAAAElFTkSuQmCC&labelColor=black)](https://deepwiki.com/Ildiar25/NavidromeServer)
[![Static Badge](https://img.shields.io/badge/Cont%C3%A1ctame-EA4335?logo=gmail&labelColor=black)](mailto:j.pastor1591@gmail.com)
[![Static Badge](https://img.shields.io/badge/Mi_Perfil_Profesional-006699?logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAAA4AAAAPCAMAAADjyg5GAAAAilBMVEUAAAAAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkAZpkWaufzAAAALXRSTlMAAQIDEBETFhcgIycqLS4ySVFXWV1fYWpsbXV7iIqQqa20wsXO0tbg4efq8%2F2PFdscAAAAYklEQVQIW5XHyRbBABBFwSciCNos5qCNkfv%2Fv2cVp4%2Bd2pWUJApGz8cwdAfb0MHtmof%2BmLpPUvfD7FKVPamAZRdeNeDfctq%2FYdz03tIR5k3P0grWoQvY%2FNfMrNM260upWfYBxD8QUVv%2BWwcAAAAASUVORK5CYII%3D&labelColor=black)](https://www.linkedin.com/in/joan-pastor-vicens-aa5b4a55)
[![Static Badge](https://img.shields.io/badge/Portfolio-white?logo=github&labelColor=black)](https://github.com/Ildiar25)

See you coding! 😜

<p align="right"><a href="#readme-top">Volver ⏫</a></p>