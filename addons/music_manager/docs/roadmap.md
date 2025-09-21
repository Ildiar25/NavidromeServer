# 🗺️ Roadmap - NavidromeServer

Este roadmap refleja la evolución del proyecto según los commits del repositorio.

---

## 📅 Timeline

### 🚀 Fase 1: Configuración inicial (Dic 2023)
- Creación del proyecto base.
- Configuración de **Odoo 17**.
- Setup inicial con **PostgreSQL** y dependencias.

---

### 🐳 Fase 2: Infraestructura con Docker (Ene 2024)
- Dockerización del entorno.
- Creación de `docker-compose.yml`.
- Configuración de servicios (Odoo + PostgreSQL + Navidrome).

---

### 🎶 Fase 3: Integración con Navidrome (Feb 2024)
- Conexión entre Odoo y Navidrome.
- Creación del módulo **`music_manager`**.
- Pruebas de autenticación y comunicación entre servicios.

---

### 🔧 Fase 4: Desarrollo del módulo (Mar 2024)
- Modelos y vistas en Odoo para gestionar música.
- Creación de endpoints para sincronizar datos con Navidrome.
- Ajustes en permisos y seguridad.

---

### 📈 Fase 5: Mejoras y refinamiento (Abr–May 2024)
- Refactor de código en el módulo `music_manager`.
- Corrección de bugs y optimización de queries.
- Mejoras en la integración con la API de Navidrome.

---

### 📦 Fase 6: Estabilización y despliegue (Jun 2024 → actual)
- Ajustes finales en Docker y Odoo.
- Configuración para despliegue en entornos de prueba/producción.
- Documentación inicial del proyecto.

---

## ✅ Próximos pasos
- Ampliar la documentación de uso e instalación.
- Implementar tests automatizados.
- Optimizar el rendimiento para colecciones grandes de música.
- Preparar una versión beta pública.

---

## 🏷️ Lista de tareas

 - [ ] **Añadir Pydub para la conversión de archivos de diferentes formatos.**
 - [ ] **Añadir campo que referencien a la extensión de archivo.**
 - [x] Añadir función que se encargue de mover los archivos.
 - [x] Añadir función que se encargue de actualizar nombre de archivo.
 - [x] Añadir función que se encargue de devolver los ID3 tipo Dict.
 - [x] Preparar bien los diferentes pasos del formulario principal.
 - [x] Función al pulsar 'save' que devuelva las etiquetas añadidas al archivo y actualice los campos.
 - [x] Añadir automatización al crear las carpetas principales en Linux (y permisos).
 - [x] Arreglar botón 'Save'. Constrains detecta que no hay URL ni archivo y da error.
 - [ ] **Añadir excepciones específicas en los servicios.**
 - [ ] **Crear test para revisar todos los servicios creados.**
 - [x] Actualizar 'makefile' y el módulo 'Utils.psm1' con el archivo 'permissions.sh'.
 - [x] Arreglar el guardado de metadatos: Actualmente da problemas.
 - [x] Comprobar que el archivo se elimine al eliminar el registro.
 - [ ] **Por ahora no hay problemas de sobreescritura (comprobar al haber dos usuarios modificando el mismo archivo).**
 - [x] Qué ocurre si la canción se elimina y el registro se mantiene: Comprobación del path una vez se abre el formulario.
 - [x] Por ahora no hay lógica que elimine carpetas vacías. Implementar de forma recursiva.
 - [x] Implementar lógica que controle 'collection': Si se marca, various artists, si no que calcule según artista original.
 - [ ] **Cuando se agrega un archivo desde un USB no se calcula su diración. Tener en cuenta al momento de desplegar el proyecto.**
 - [x] Añadir documentacióny tipado de los modelos.
 - [x] Añadir textos informativos al actualizar los metadatos de las canciones.
