# Flash OCR Pro

Herramienta de escritorio para la extraccion de texto mediante seleccion de area en pantalla utilizando Python y EasyOCR.

## Instrucciones de Instalacion y Uso

Este proyecto incluye un automatizador para entornos Windows que gestiona las dependencias de forma aislada.

1.  Asegurese de tener instalado Python 3.10 o superior.
2.  Verifique que el archivo `requirements.txt` este presente en la carpeta con el siguiente contenido:
    ```text
    easyocr
    Pillow
    opencv-python
    ```
3.  Ejecute el archivo `iniciar_app.bat`.

El script realizara las siguientes acciones de forma automatica:
- Creacion del entorno virtual (.venv).
- Actualizacion de pip e instalacion de librerias necesarias.
- Ejecucion de la aplicacion principal.

## Guia de Usuario

1.  Al abrir la aplicacion, espere a que el estado indique "Motor Listo".
2.  Haga clic en el boton "Seleccionar Area". La pantalla se oscurecera levemente.
3.  Haga clic y arrastre el cursor para enmarcar el texto que desea extraer.
4.  El texto aparecera en el cuadro principal. Utilice el boton "Copiar" para enviarlo al portapapeles.

## Notas Tecnicas

- El motor EasyOCR requiere descargar modelos de lenguaje (español) durante su primera ejecucion. Esto requiere conexion a internet y aproximadamente 150MB de espacio.
- Para cancelar una seleccion en curso, presione la tecla ESC.
- La aplicacion esta configurada para ejecutarse en CPU por defecto para asegurar compatibilidad.

## Dependencias Principales

- EasyOCR: Motor de reconocimiento optico de caracteres basado en Deep Learning.
- Tkinter: Libreria para la interfaz grafica de usuario.
- Pillow: Gestion de capturas de pantalla (screenshots).