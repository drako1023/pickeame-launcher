# pickeame-launcher
Pickeame launcher es un lanzador de minecraft java dedicado a jugar con los mods packs de mis servidores.

## Instalación

En PowerShell, desde la carpeta del proyecto, crea un entorno virtual e instala las dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe pickeame.py
```

Para la rotación del fondo, coloca hasta seis imágenes PNG en `recursos/fondos/` con estos nombres: `fondo1.png`, `fondo2.png`, `fondo3.png`, `fondo4.png`, `fondo5.png` y `fondo6.png`. Se muestran en ese orden con una transición de difuminado.
