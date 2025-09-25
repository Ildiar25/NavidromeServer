## 🏷️ Lista de tareas

### Automatización

 - [x] Añadir automatización al crear las carpetas principales en Linux (y permisos).
 - [x] Actualizar 'makefile' y el módulo 'Utils.psm1' con el archivo 'permissions.sh'.

### Modelos

 - [ ] **Añadir campo que almacene a extensión de archivo.**

### Servicios

 - [ ] **Añadir Pydub para la conversión de archivos de diferentes formatos.**
 - [x] Añadir método que se encargue de mover los archivos.
 - [x] Añadir método que se encargue de actualizar nombre de archivo.
 - [x] Añadir método que se encargue de devolver los ID3 tipo Dict.
 - [ ] **Añadir excepciones específicas en los servicios.**
 - [x] Arreglar el guardado de metadatos: Actualmente da problemas.
 - [x] Comprobar que el archivo se elimine al eliminar el registro.
 - [x] Por ahora no hay lógica que elimine carpetas vacías. Implementar de forma recursiva.

### Módulo

 - [x] Preparar bien los diferentes pasos del formulario principal.
 - [x] Método al pulsar 'save' que devuelva las etiquetas añadidas al archivo y actualice los campos.
 - [x] Arreglar botón 'Save'. Constrains detecta que no hay URL ni archivo y da error.
 - [ ] **Crear test para revisar todos los servicios creados.**
 - [ ] **Por ahora no hay problemas de sobreescritura (comprobar al haber dos usuarios modificando el mismo archivo).**
 - [x] Qué ocurre si la canción se elimina y el registro se mantiene: Comprobación del 'path' una vez se abre el formulario.
 - [x] Implementar lógica que controle 'collection': Si se marca, various artists, si no que calcule según artista original.
 - [ ] **Cuando se agrega un archivo desde un USB no se calcula su duración. Tener en cuenta al momento de desplegar el proyecto.**
 - [x] Añadir documentación y tipado de los modelos.
 - [x] Añadir textos informativos al actualizar los metadatos de las canciones.
 - [ ] **Implementar soporte multilenguaje.**
   - [x] Inglés.
   - [ ] **Francés.**
   - [ ] **Español.**
   - [ ] **Catalán.**
