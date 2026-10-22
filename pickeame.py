import json
import ctypes
import importlib
import shutil
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import urllib.request

try:
    Image = importlib.import_module("PIL.Image")
    ImageTk = importlib.import_module("PIL.ImageTk")
except ModuleNotFoundError:
    Image = None
    ImageTk = None


class pickeame:
    def __init__(self, root):
        self.root = root
        self.root.title("Fyham Launcher")
        self.root.geometry("1920x1080")
        self.root.minsize(700, 450)

        self.base_dir = Path(__file__).resolve().parent
        ruta_icono = self.base_dir / "recursos" / "cerdito.png"
        ruta_icono_windows = self.base_dir / "recursos" / "cerdito.ico"
        if ruta_icono.exists():
            try:
                self.icono = tk.PhotoImage(master=self.root, file=str(ruta_icono))
                self.root.iconphoto(True, self.icono)
            except tk.TclError as error:
                print(f"Error al cargar el ícono: {error}")
        if ruta_icono_windows.exists():
            try:
                self.root.iconbitmap(str(ruta_icono_windows))
            except tk.TclError as error:
                print(f"Error al cargar el ícono de Windows: {error}")
        self.carpeta_fondos = self.base_dir / "recursos" / "fondos"
        self.carpeta_fondos.mkdir(parents=True, exist_ok=True)

        self.URL_INSTALACIONES_JSON = "https://raw.githubusercontent.com/TU_USUARIO/TU_REPO/main/instalaciones.json"
        self.ADMIN_PASSWORD = "Drako"

        self.lista_instalaciones_data = []
        self.lista_fondos_data = []

        self.ram_asignada = tk.IntVar(master=self.root, value=4)
        self.ram_mostrada = False

        # --- PANEL PRINCIPAL CON CANVAS DE FONDO ---
        self.principal_panel = tk.Frame(self.root, bg="#010B3B")
        self.principal_panel.pack(side="top", fill="both", expand=True)

        self.bg_canvas = tk.Canvas(
            self.principal_panel,
            bg="#010B3B",
            highlightthickness=0,
            bd=0
        )
        self.bg_canvas.pack(fill="both", expand=True)

      
        self.fondos_pil = []
        self.idx_fondo_actual = 0
        self.idx_fondo_siguiente = 0
        self.img_tk_actual = None
        self.bg_container_id = None
        self.pasos_transicion = 15  
        self.paso_actual = 0
        self.timer_slideshow = None
        self.ancho_panel = 1920
        self.alto_panel = 1080

      
        self.sidebar = tk.Frame(self.root, bg="#000000", height=100)
        self.sidebar.pack(side="bottom", fill="x")
        self.sidebar.pack_propagate(False)

        self.instalaciones_frame = tk.Frame(self.sidebar, bg="#000000", width=225, height=60)
        self.instalaciones_frame.place(x=15, rely=0.5, anchor="w", width=225, height=60)

        self.boton_instalaciones = tk.Button(
            self.instalaciones_frame,
            text="Instalaciones",
            command=self.alternar_instalaciones,
            bg="#333333",
            fg="#FFFFFF",
            font=("Arial", 15, "bold"),
            activebackground="#555555",
            activeforeground="white",
            cursor="hand2"
        )
        self.boton_instalaciones.place(x=0, y=0, relwidth=1.0, relheight=1.0)

        self.ram_button_frame = tk.Frame(self.sidebar, bg="#000000", width=60, height=60)
        self.ram_button_frame.place(relx=1.0, x=-15, rely=0.5, anchor="e", width=60, height=60)

        ruta_creeper = self.base_dir / "recursos" / "creeper.png"
        try:
            img_creeper_original = tk.PhotoImage(master=self.root, file=str(ruta_creeper))
            factor_btn = max(1, img_creeper_original.width() // 50)
            self.creeper_img = img_creeper_original.subsample(factor_btn, factor_btn)
            factor_knob = max(1, img_creeper_original.width() // 24)
            self.creeper_knob_img = img_creeper_original.subsample(factor_knob, factor_knob)

            self.boton_ram = tk.Button(
                self.ram_button_frame,
                image=self.creeper_img,
                command=self.alternar_ram,
                bg="#000000",
                activebackground="#202020",
                bd=0,
                cursor="hand2"
            )
        except tk.TclError:
            self.creeper_knob_img = None
            self.boton_ram = tk.Button(
                self.ram_button_frame,
                text="RAM",
                command=self.alternar_ram,
                bg="#333333",
                fg="white",
                font=("Arial", 12, "bold"),
                activebackground="#555555",
                cursor="hand2"
            )
        self.boton_ram.place(x=0, y=0, relwidth=1.0, relheight=1.0)

        self.ram_panel = tk.Frame(
            self.sidebar,
            bg="#000000",
            highlightbackground="#333333",
            highlightthickness=1,
            padx=10,
            pady=5
        )

        self.lbl_ram_val = tk.Label(
            self.ram_panel,
            text=f"{self.ram_asignada.get()} GB",
            font=("Arial", 11, "bold"),
            fg="#A4C805",
            bg="#000000"
        )
        self.lbl_ram_val.pack(side="left", padx=(0, 10))

        self.x_min_ram = 15
        self.x_max_ram = 155
        self.canvas_ram = tk.Canvas(
            self.ram_panel,
            width=170,
            height=36,
            bg="#000000",
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )
        self.canvas_ram.pack(side="left")

        self.linea_fondo = self.canvas_ram.create_line(
            self.x_min_ram, 18, self.x_max_ram, 18,
            fill="#333333", width=6, capstyle="round"
        )
        self.linea_activa = self.canvas_ram.create_line(
            self.x_min_ram, 18, self.x_min_ram, 18,
            fill="#A4C805", width=6, capstyle="round"
        )

        if self.creeper_knob_img:
            self.handle_ram = self.canvas_ram.create_image(self.x_min_ram, 18, image=self.creeper_knob_img)
        else:
            self.handle_ram = self.canvas_ram.create_rectangle(
                self.x_min_ram - 8, 10, self.x_min_ram + 8, 26,
                fill="#A4C805", outline="white"
            )

        self.canvas_ram.bind("<Button-1>", self.arrastrar_ram)
        self.canvas_ram.bind("<B1-Motion>", self.arrastrar_ram)

        self.lista_instalaciones_frame = tk.Frame(
            self.root,
            bg="#000000",
            highlightbackground="#333333",
            highlightthickness=1
        )

        self.canvas_instalaciones = tk.Canvas(
            self.lista_instalaciones_frame,
            bg="#000000",
            highlightthickness=0,
            borderwidth=0
        )
        self.canvas_instalaciones.pack(side="left", fill="both", expand=True)

        self.tarjetas_instalaciones = tk.Frame(self.canvas_instalaciones, bg="#000000")
        self.canvas_instalaciones.create_window((0, 0), window=self.tarjetas_instalaciones, anchor="nw")
        self.tarjetas_instalaciones.bind("<Configure>", self.actualizar_region_instalaciones)

        self.botones_frame = tk.Frame(self.sidebar, bg="#000000")
        self.botones_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Configuración del Título y Botón Principal sobre el Canvas
        self.crear_elementos_sobre_fondo()

        self.boton_jugar = tk.Button(
            self.botones_frame,
            text="Perder el tiempo",
            command=self.perder_tiempo,
            bg="#A4C805",
            fg="#FFFFFF",
            font=("Arial", 20, "bold"),
            activebackground="#7C9A00",
            activeforeground="white",
            width=18,
            height=1,
            bd=3,
            relief="raised",
            cursor="hand2"
        )
        self.boton_jugar.pack(padx=15, pady=5)

        self.instalacion_seleccionada = tk.StringVar(master=self.root, value="")
        self.instalacion_imgs = []
        self.instalaciones_mostradas = False

        
        self.bg_canvas.bind("<Configure>", self.al_redimensionar_panel)
        self.cargar_fondos()
        self.iniciar_rotacion_fondos()

    def crear_elementos_sobre_fondo(self):
        """Genera el título incrustado directamente sobre el Canvas de fondo"""
        ruta_imagen = self.base_dir / "recursos" / "tittulo.png"
        try:
            self.title_img = tk.PhotoImage(master=self.root, file=str(ruta_imagen))
            self.title_canvas_id = self.bg_canvas.create_image(
                self.ancho_panel // 2,
                60,
                image=self.title_img,
                anchor="n"
            )
        except tk.TclError:
            self.title_img = None
            self.title_canvas_id = self.bg_canvas.create_text(
                self.ancho_panel // 2,
                60,
                text="PICKEAME LAUNCHER",
                font=("Arial", 32, "bold"),
                fg="#A4C805",
                anchor="n"
            )

        self.bg_canvas.tag_bind(
            self.title_canvas_id,
            "<Double-Button-1>",
            lambda e: self.abrir_login_admin()
        )

  
    def cargar_fondos(self):
        """Carga fondo1.png a fondo6.png en orden."""
        self.fondos_pil.clear()
        if Image is None or ImageTk is None:
            messagebox.showerror(
                "Falta Pillow",
                "El Python actual no tiene Pillow instalado. Ejecuta el launcher con:\n"
                r".\.venv\Scripts\python.exe pickeame.py",
                parent=self.root
            )
            return
        for numero in range(1, 7):
            nombre_archivo = f"fondo{numero}.png"
            ubicaciones = (
                self.carpeta_fondos / nombre_archivo,
                self.base_dir / "recursos" / nombre_archivo
            )
            archivo = next((ruta for ruta in ubicaciones if ruta.is_file()), None)
            if archivo is None:
                continue
            try:
                with Image.open(archivo) as imagen:
                    self.fondos_pil.append(imagen.convert("RGB"))
            except OSError as error:
                messagebox.showwarning(
                    "Fondo no válido",
                    f"No se pudo cargar {archivo.name}: {error}",
                    parent=self.root
                )

        if self.fondos_pil:
            self.idx_fondo_actual %= len(self.fondos_pil)
            self.mostrar_fondo_actual()
        else:
            messagebox.showwarning(
                "No hay fondos",
                "Coloca al menos una imagen con nombre fondo1.png en recursos/fondos/.",
                parent=self.root
            )

    def al_redimensionar_panel(self, event):
        """Redimensiona la imagen actual al cambiar el tamaño de la ventana"""
        if event.width < 10 or event.height < 10:
            return
        self.ancho_panel = event.width
        self.alto_panel = event.height
        
        if self.title_canvas_id:
            self.bg_canvas.coords(self.title_canvas_id, self.ancho_panel // 2, 60)

        self.mostrar_fondo_actual()

    def mostrar_fondo_actual(self):
        if not self.fondos_pil or Image is None or ImageTk is None:
            return

        imagen = self.fondos_pil[self.idx_fondo_actual].resize(
            (self.ancho_panel, self.alto_panel), Image.Resampling.LANCZOS
        )
        self.img_tk_actual = ImageTk.PhotoImage(imagen)

        if self.bg_container_id:
            self.bg_canvas.itemconfig(self.bg_container_id, image=self.img_tk_actual)
        else:
            self.bg_container_id = self.bg_canvas.create_image(
                0, 0, image=self.img_tk_actual, anchor="nw"
            )
            self.bg_canvas.tag_lower(self.bg_container_id)

    def iniciar_rotacion_fondos(self):
        """Inicia el ciclo de cambio automático de fondo cada 7 segundos"""
        if len(self.fondos_pil) > 1:
            self.idx_fondo_siguiente = (self.idx_fondo_actual + 1) % len(self.fondos_pil)
            self.paso_actual = 0
            self.ejecutar_transicion()
        else:
            self.root.after(5000, self.iniciar_rotacion_fondos)

    def ejecutar_transicion(self):
        """Efecto de desvanecimiento suave (Crossfade) mediante Alpha Blending"""
        if len(self.fondos_pil) < 2 or Image is None or ImageTk is None:
            return

        if self.paso_actual <= self.pasos_transicion:
            alpha = self.paso_actual / float(self.pasos_transicion)
            
            img_a = self.fondos_pil[self.idx_fondo_actual].resize((self.ancho_panel, self.alto_panel), Image.Resampling.BILINEAR)
            img_b = self.fondos_pil[self.idx_fondo_siguiente].resize((self.ancho_panel, self.alto_panel), Image.Resampling.BILINEAR)
            
            img_mezclada = Image.blend(img_a, img_b, alpha)
            self.img_tk_actual = ImageTk.PhotoImage(img_mezclada)
            
            if self.bg_container_id:
                self.bg_canvas.itemconfig(self.bg_container_id, image=self.img_tk_actual)
            else:
                self.bg_container_id = self.bg_canvas.create_image(0, 0, image=self.img_tk_actual, anchor="nw")
                self.bg_canvas.tag_lower(self.bg_container_id)

            self.paso_actual += 1
            self.root.after(40, self.ejecutar_transicion)
        else:
            self.idx_fondo_actual = self.idx_fondo_siguiente
            self.root.after(6000, self.iniciar_rotacion_fondos)

    # --- OBTENCIÓN Y GESTIÓN DE DATOS ---
    def obtener_instalaciones_remotas(self):
        """Descarga la lista de modpacks y fondos desde la nube o lee fallback local"""
        ruta_local = self.base_dir / "recursos" / "instalaciones.json"

        try:
            req = urllib.request.Request(
                self.URL_INSTALACIONES_JSON,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                datos = json.loads(response.read().decode())
                if isinstance(datos, dict):
                    self.lista_instalaciones_data = datos.get("instalaciones", [])
                    self.lista_fondos_data = datos.get("fondos", [])
                else:
                    self.lista_instalaciones_data = datos
                return
        except Exception:
            pass

        if ruta_local.exists():
            try:
                with open(ruta_local, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                    if isinstance(datos, dict):
                        self.lista_instalaciones_data = datos.get("instalaciones", [])
                        self.lista_fondos_data = datos.get("fondos", [])
                    else:
                        self.lista_instalaciones_data = datos
                    return
            except Exception:
                pass

        self.lista_instalaciones_data = []

    def mostrar_instalaciones(self):
        for elemento in self.tarjetas_instalaciones.winfo_children():
            elemento.destroy()

        self.obtener_instalaciones_remotas()

        if not self.lista_instalaciones_data:
            lbl_vacio = tk.Label(
                self.tarjetas_instalaciones,
                text="No hay modpacks disponibles",
                fg="gray",
                bg="#000000",
                font=("Arial", 10),
                pady=20
            )
            lbl_vacio.pack()
            return

        if not self.instalacion_seleccionada.get():
            self.instalacion_seleccionada.set(self.lista_instalaciones_data[0].get("nombre", ""))

        self.instalacion_imgs.clear()

        for instalacion in self.lista_instalaciones_data:
            tarjeta = tk.Frame(
                self.tarjetas_instalaciones,
                bg="#202020",
                width=210,
                height=135,
                padx=8,
                pady=5
            )
            tarjeta.pack(side="top", padx=5, pady=(5, 5))
            tarjeta.pack_propagate(False)

            ruta_img = self.base_dir / "recursos" / instalacion.get("imagen", "")
            try:
                imagen_original = tk.PhotoImage(master=self.root, file=str(ruta_img))
                factor = max(
                    1,
                    (imagen_original.width() + 99) // 100,
                    (imagen_original.height() + 49) // 50
                )
                imagen = imagen_original.subsample(factor, factor)
                self.instalacion_imgs.append(imagen)
                tk.Label(tarjeta, image=imagen, bg="#202020").pack(pady=(0, 2))
            except tk.TclError:
                tk.Label(
                    tarjeta, text="Sin Imagen", width=20, height=2, fg="white", bg="#303030"
                ).pack(pady=(0, 2))

            tk.Label(
                tarjeta, text=instalacion.get("nombre", "Modpack"),
                font=("Arial", 10, "bold"), fg="white", bg="#202020"
            ).pack(pady=1)

            tk.Label(
                tarjeta, text=instalacion.get("version", "1.20.1"),
                font=("Arial", 8), fg="#BBBBBB", bg="#202020"
            ).pack()

            tk.Radiobutton(
                tarjeta, text="Seleccionar",
                variable=self.instalacion_seleccionada,
                value=instalacion.get("nombre", ""),
                fg="white", bg="#202020", selectcolor="#010B3B",
                activebackground="#202020", activeforeground="white"
            ).pack()

        self.root.update_idletasks()
        self.actualizar_region_instalaciones()
        self.vincular_rueda(self.lista_instalaciones_frame)

    # --- PANEL DE ADMINISTRACIÓN AMPLIADO ---
    def abrir_login_admin(self):
        ventana_pass = tk.Toplevel(self.root)
        ventana_pass.title("Acceso Creador")
        ventana_pass.geometry("300x150")
        ventana_pass.configure(bg="#010B3B")
        ventana_pass.resizable(False, False)

        tk.Label(ventana_pass, text="Contraseña Admin:", fg="white", bg="#010B3B", font=("Arial", 11)).pack(pady=10)
        entry_pass = tk.Entry(ventana_pass, show="*", font=("Arial", 12))
        entry_pass.pack(pady=5)

        def verificar():
            if entry_pass.get() == self.ADMIN_PASSWORD:
                ventana_pass.destroy()
                self.abrir_panel_subir_modpack()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta", parent=ventana_pass)

        tk.Button(
            ventana_pass, text="Entrar", command=verificar, bg="#A4C805", fg="white", font=("Arial", 10, "bold")
        ).pack(pady=10)

    def abrir_panel_subir_modpack(self):
        ventana_admin = tk.Toplevel(self.root)
        ventana_admin.title("Panel de Creador - Modpacks y Fondos")
        ventana_admin.geometry("500x550")
        ventana_admin.configure(bg="#000000")

        notebook = ttk.Notebook(ventana_admin)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        tab_modpacks = tk.Frame(notebook, bg="#111111")
        tab_fondos = tk.Frame(notebook, bg="#111111")

        notebook.add(tab_modpacks, text="Modpacks")
        notebook.add(tab_fondos, text="Fondos del Launcher")

        # --- PESTAÑA 1: MODPACKS ---
        tk.Label(tab_modpacks, text="Añadir Modpack a la Nube", font=("Arial", 12, "bold"), fg="white", bg="#111111").pack(pady=10)
        
        tk.Label(tab_modpacks, text="Nombre del Modpack:", fg="white", bg="#111111").pack(anchor="w", padx=20)
        e_nombre = tk.Entry(tab_modpacks, width=45)
        e_nombre.pack(padx=20, pady=2)

        tk.Label(tab_modpacks, text="Versión (ej: Forge 1.20.1):", fg="white", bg="#111111").pack(anchor="w", padx=20)
        e_version = tk.Entry(tab_modpacks, width=45)
        e_version.pack(padx=20, pady=2)

        tk.Label(tab_modpacks, text="Imagen de la tarjeta:", fg="white", bg="#111111").pack(anchor="w", padx=20)
        frame_img = tk.Frame(tab_modpacks, bg="#111111")
        frame_img.pack(fill="x", padx=20, pady=2)
        e_imagen = tk.Entry(frame_img, width=30)
        e_imagen.pack(side="left")

        ruta_origen_img = {"path": None}

        def buscar_imagen_modpack():
            archivo = filedialog.askopenfilename(
                parent=ventana_admin,
                title="Seleccionar imagen para la tarjeta",
                filetypes=[("Imágenes", "*.png *.jpg *.jpeg")]
            )
            if archivo:
                ruta = Path(archivo)
                ruta_origen_img["path"] = ruta
                e_imagen.delete(0, tk.END)
                e_imagen.insert(0, ruta.name)

        btn_buscar = tk.Button(frame_img, text="Elegir...", command=buscar_imagen_modpack, bg="#333333", fg="white")
        btn_buscar.pack(side="left", padx=5)

        tk.Label(tab_modpacks, text="URL Descarga Zip (.zip):", fg="white", bg="#111111").pack(anchor="w", padx=20)
        e_url = tk.Entry(tab_modpacks, width=45)
        e_url.pack(padx=20, pady=2)

        def guardar_modpack():
            nombre_img = e_imagen.get().strip()

            if ruta_origen_img["path"]:
                carpeta_recursos = self.base_dir / "recursos"
                carpeta_recursos.mkdir(exist_ok=True)
                destino = carpeta_recursos / ruta_origen_img["path"].name
                shutil.copy(ruta_origen_img["path"], destino)

            nuevo = {
                "nombre": e_nombre.get().strip(),
                "version": e_version.get().strip(),
                "imagen": nombre_img,
                "url_zip": e_url.get().strip()
            }

            if not nuevo["nombre"] or not nuevo["url_zip"]:
                messagebox.showwarning("Incompleto", "Nombre y URL Zip son obligatorios", parent=ventana_admin)
                return

            ruta_local = self.base_dir / "recursos" / "instalaciones.json"
            self.obtener_instalaciones_remotas()
            self.lista_instalaciones_data.append(nuevo)

            datos_completos = {
                "instalaciones": self.lista_instalaciones_data,
                "fondos": self.lista_fondos_data
            }

            with open(ruta_local, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Éxito", "Modpack registrado localmente.", parent=ventana_admin)

        tk.Button(tab_modpacks, text="Guardar Modpack", command=guardar_modpack, bg="#A4C805", fg="white", font=("Arial", 11, "bold")).pack(pady=15)

        # --- PESTAÑA 2: FONDOS (SLIDESHOW) ---
        tk.Label(tab_fondos, text="Añadir Imagen de Fondo Global", font=("Arial", 12, "bold"), fg="white", bg="#111111").pack(pady=10)

        frame_bg_select = tk.Frame(tab_fondos, bg="#111111")
        frame_bg_select.pack(fill="x", padx=20, pady=10)

        e_fondo_path = tk.Entry(frame_bg_select, width=32)
        e_fondo_path.pack(side="left")

        ruta_origen_fondo = {"path": None}

        def buscar_imagen_fondo():
            archivo = filedialog.askopenfilename(
                parent=ventana_admin,
                title="Seleccionar Imagen de Fondo",
                filetypes=[("Imágenes HD", "*.png *.jpg *.jpeg *.webp")]
            )
            if archivo:
                ruta = Path(archivo)
                ruta_origen_fondo["path"] = ruta
                e_fondo_path.delete(0, tk.END)
                e_fondo_path.insert(0, ruta.name)

        tk.Button(frame_bg_select, text="Elegir Fondo...", command=buscar_imagen_fondo, bg="#333333", fg="white").pack(side="left", padx=5)

        def subir_guardar_fondo():
            if not ruta_origen_fondo["path"]:
                messagebox.showwarning("Atención", "Selecciona una imagen primero", parent=ventana_admin)
                return

            if Image is None:
                messagebox.showerror(
                    "Falta Pillow",
                    "Instala las dependencias con: python -m pip install -r requirements.txt",
                    parent=ventana_admin
                )
                return

            numero = next(
                (
                    i for i in range(1, 7)
                    if not (self.carpeta_fondos / f"fondo{i}.png").exists()
                ),
                None
            )
            if numero is None:
                messagebox.showwarning(
                    "Fondos completos",
                    "Ya existen los seis fondos. Reemplaza manualmente uno de fondo1.png a fondo6.png.",
                    parent=ventana_admin
                )
                return

            nombre_archivo = f"fondo{numero}.png"
            destino_fondo = self.carpeta_fondos / nombre_archivo
            try:
                with Image.open(ruta_origen_fondo["path"]) as imagen:
                    imagen.convert("RGB").save(destino_fondo, format="PNG")
            except OSError as error:
                messagebox.showerror(
                    "Error al guardar",
                    f"No se pudo procesar la imagen: {error}",
                    parent=ventana_admin
                )
                return

            ruta_local = self.base_dir / "recursos" / "instalaciones.json"
            self.obtener_instalaciones_remotas()

            if nombre_archivo not in self.lista_fondos_data:
                self.lista_fondos_data.append(nombre_archivo)

            datos_completos = {
                "instalaciones": self.lista_instalaciones_data,
                "fondos": self.lista_fondos_data
            }

            with open(ruta_local, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, indent=4, ensure_ascii=False)

            self.cargar_fondos()
            self.mostrar_fondo_actual()
            messagebox.showinfo(
                "Fondo Agregado",
                f"Imagen guardada como '{nombre_archivo}' y añadida a la rotación.\n\n"
                "Para que le aparezca a todos los usuarios, sube la imagen a la carpeta de tu servidor/GitHub "
                "y actualiza el archivo JSON remoto.",
                parent=ventana_admin
            )

        tk.Button(tab_fondos, text="Añadir a Fondos Rotativos", command=subir_guardar_fondo, bg="#A4C805", fg="white", font=("Arial", 11, "bold")).pack(pady=15)

    # --- MÉTODOS DE COMPONENTES DE INTERFAZ Y EVENTOS ---
    def arrastrar_ram(self, evento):
        x = max(self.x_min_ram, min(self.x_max_ram, evento.x))
        porcentaje = (x - self.x_min_ram) / (self.x_max_ram - self.x_min_ram)
        val = round(2 + porcentaje * (32 - 2))
        self.ram_asignada.set(val)
        self.actualizar_slider_ram()

    def actualizar_slider_ram(self):
        val = self.ram_asignada.get()
        self.lbl_ram_val.config(text=f"{val} GB")

        porcentaje = (val - 2) / (32 - 2)
        x = self.x_min_ram + porcentaje * (self.x_max_ram - self.x_min_ram)

        self.canvas_ram.coords(self.linea_activa, self.x_min_ram, 18, x, 18)

        if self.creeper_knob_img:
            self.canvas_ram.coords(self.handle_ram, x, 18)
        else:
            self.canvas_ram.coords(self.handle_ram, x - 8, 10, x + 8, 26)

    def alternar_ram(self):
        if self.ram_mostrada:
            self.ram_panel.place_forget()
            self.ram_mostrada = False
            return

        if self.instalaciones_mostradas:
            self.lista_instalaciones_frame.place_forget()
            self.instalaciones_mostradas = False

        self.ram_panel.place(relx=1.0, x=-85, rely=0.5, anchor="e")
        self.ram_mostrada = True
        self.actualizar_slider_ram()

    def actualizar_region_instalaciones(self, evento=None):
        self.canvas_instalaciones.configure(
            scrollregion=self.canvas_instalaciones.bbox("all")
        )

    def desplazar_instalaciones(self, evento):
        if evento.delta:
            unidades = -1 if evento.delta > 0 else 1
            self.canvas_instalaciones.yview_scroll(unidades, "units")
        elif evento.num == 4:
            self.canvas_instalaciones.yview_scroll(-1, "units")
        elif evento.num == 5:
            self.canvas_instalaciones.yview_scroll(1, "units")
        return "break"

    def vincular_rueda(self, widget):
        widget.bind("<MouseWheel>", self.desplazar_instalaciones)
        widget.bind("<Button-4>", self.desplazar_instalaciones)
        widget.bind("<Button-5>", self.desplazar_instalaciones)
        for hijo in widget.winfo_children():
            self.vincular_rueda(hijo)

    def alternar_instalaciones(self):
        if self.instalaciones_mostradas:
            self.lista_instalaciones_frame.place_forget()
            self.instalaciones_mostradas = False
            return

        if self.ram_mostrada:
            self.ram_panel.place_forget()
            self.ram_mostrada = False

        self.mostrar_instalaciones()
        self.lista_instalaciones_frame.place(
            x=15, rely=1.0, y=-80, anchor="sw", width=225, height=320
        )
        self.instalaciones_mostradas = True
        self.canvas_instalaciones.yview_moveto(0)

    def perder_tiempo(self):
        # Reinicia la visualización de la pantalla principal si se destruyeron widgets sobre el canvas
        self.bg_canvas.delete("all")
        self.bg_container_id = None
        self.crear_elementos_sobre_fondo()
        self.al_redimensionar_panel(type('Event', (), {'width': self.bg_canvas.winfo_width(), 'height': self.bg_canvas.winfo_height()})())


if sys.platform == "win32":
    set_app_id = ctypes.WinDLL("shell32", use_last_error=True).SetCurrentProcessExplicitAppUserModelID
    set_app_id.argtypes = [ctypes.c_wchar_p]
    set_app_id.restype = ctypes.c_long
    resultado = set_app_id("drako1023.PickeameLauncher")
    if resultado != 0:
        raise OSError(
            f"No se pudo establecer el identificador de la aplicación de Windows "
            f"(HRESULT 0x{resultado & 0xFFFFFFFF:08X})."
        )

root = tk.Tk()
app = pickeame(root)
root.mainloop()