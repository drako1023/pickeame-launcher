import json
import os
import shutil
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import urllib.request


class pickeame:
    def __init__(self, root):
        self.root = root
        self.root.title("Fyham Launcher")
        self.root.geometry("1920x1080")
        self.root.minsize(700, 450)

        self.base_dir = Path(__file__).resolve().parent

        self.URL_INSTALACIONES_JSON = "https://raw.githubusercontent.com/TU_USUARIO/TU_REPO/main/instalaciones.json"
        self.ADMIN_PASSWORD = os.environ.get("PICKEAME_ADMIN_PASSWORD", "")


        self.lista_instalaciones_data = []


        self.ram_asignada = tk.IntVar(master=self.root, value=4)
        self.ram_mostrada = False

        self.principal_panel = tk.Frame(self.root, bg="#010B3B")
        self.principal_panel.pack(
            side="top",
            fill="both",
            expand=True
        )


        self.sidebar = tk.Frame(
            self.root,
            bg="#000000",
            height=100
        )
        self.sidebar.pack(side="bottom", fill="x")
        self.sidebar.pack_propagate(False)

        self.instalaciones_frame = tk.Frame(
            self.sidebar,
            bg="#000000",
            width=225,
            height=60
        )
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

        self.ram_button_frame = tk.Frame(
            self.sidebar,
            bg="#000000",
            width=60,
            height=60
        )
        self.ram_button_frame.place(relx=1.0, x=-15, rely=0.5, anchor="e", width=60, height=60)

        ruta_creeper = self.base_dir / "recursos" / "creeper.png"
        try:
            img_creeper_original = tk.PhotoImage(
                master=self.root,
                file=str(ruta_creeper)
            )
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
            self.handle_ram = self.canvas_ram.create_image(
                self.x_min_ram, 18, image=self.creeper_knob_img
            )
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
        self.canvas_instalaciones.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.tarjetas_instalaciones = tk.Frame(
            self.canvas_instalaciones,
            bg="#000000"
        )
        self.canvas_instalaciones.create_window(
            (0, 0),
            window=self.tarjetas_instalaciones,
            anchor="nw"
        )

        self.tarjetas_instalaciones.bind(
            "<Configure>",
            self.actualizar_region_instalaciones
        )


        self.botones_frame = tk.Frame(self.sidebar, bg="#000000")
        self.botones_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        ruta_imagen = self.base_dir / "recursos" / "tittulo.png"
        try:
            self.title_img = tk.PhotoImage(
                master=self.root,
                file=str(ruta_imagen)
            )
            self.title_label = tk.Label(
                self.principal_panel,
                image=self.title_img,
                bg="#010B3B"
            )
        except tk.TclError:
            self.title_img = None
            self.title_label = tk.Label(
                self.principal_panel,
                text="PICKEAME LAUNCHER",
                font=("Arial", 32, "bold"),
                fg="#A4C805",
                bg="#010B3B"
            )
        self.title_label.pack(pady=20)


        self.title_label.bind("<Double-Button-1>", lambda e: self.abrir_login_admin())

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

        self.instalacion_seleccionada = tk.StringVar(
            master=self.root,
            value=""
        )
        self.instalacion_imgs = []
        self.instalaciones_mostradas = False

    def obtener_instalaciones_remotas(self):
        """Descarga la lista de modpacks en JSON desde la nube o lee un fallback local"""
        ruta_local = self.base_dir / "recursos" / "instalaciones.json"

        try:
            req = urllib.request.Request(
                self.URL_INSTALACIONES_JSON,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                datos = json.loads(response.read().decode())
                self.lista_instalaciones_data = datos
                return
        except Exception:
            pass

        if ruta_local.exists():
            try:
                with open(ruta_local, "r", encoding="utf-8") as f:
                    self.lista_instalaciones_data = json.load(f)
                    return
            except Exception:
                pass

        self.lista_instalaciones_data = []

    def mostrar_instalaciones(self):
        """Genera las tarjetas dinámicamente según la información descargada"""
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
                    tarjeta,
                    text="Sin Imagen",
                    width=20,
                    height=2,
                    fg="white",
                    bg="#303030"
                ).pack(pady=(0, 2))

            tk.Label(
                tarjeta,
                text=instalacion.get("nombre", "Modpack"),
                font=("Arial", 10, "bold"),
                fg="white",
                bg="#202020"
            ).pack(pady=1)

            tk.Label(
                tarjeta,
                text=instalacion.get("version", "1.20.1"),
                font=("Arial", 8),
                fg="#BBBBBB",
                bg="#202020"
            ).pack()

            tk.Radiobutton(
                tarjeta,
                text="Seleccionar",
                variable=self.instalacion_seleccionada,
                value=instalacion.get("nombre", ""),
                fg="white",
                bg="#202020",
                selectcolor="#010B3B",
                activebackground="#202020",
                activeforeground="white"
            ).pack()

        self.root.update_idletasks()
        self.actualizar_region_instalaciones()
        self.vincular_rueda(self.lista_instalaciones_frame)


    def abrir_login_admin(self):
        ventana_pass = tk.Toplevel(self.root)
        ventana_pass.title("Acceso Creador")
        ventana_pass.geometry("300x150")
        ventana_pass.configure(bg="#010B3B")
        ventana_pass.resizable(False, False)

        tk.Label(
            ventana_pass, text="Contraseña Admin:", fg="white", bg="#010B3B", font=("Arial", 11)
        ).pack(pady=10)

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
        ventana_admin.title("Publicar Nuevo Modpack")
        ventana_admin.geometry("450x420")
        ventana_admin.configure(bg="#000000")

        tk.Label(
            ventana_admin,
            text="Añadir Modpack a la Nube",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#000000"
        ).pack(pady=10)

        tk.Label(ventana_admin, text="Nombre del Modpack:", fg="white", bg="#000000").pack(anchor="w", padx=20)
        e_nombre = tk.Entry(ventana_admin, width=45)
        e_nombre.pack(padx=20, pady=2)

        tk.Label(ventana_admin, text="Versión (ej: Forge 1.20.1):", fg="white", bg="#000000").pack(anchor="w", padx=20)
        e_version = tk.Entry(ventana_admin, width=45)
        e_version.pack(padx=20, pady=2)

        tk.Label(ventana_admin, text="Imagen de la tarjeta:", fg="white", bg="#000000").pack(anchor="w", padx=20)
        frame_img = tk.Frame(ventana_admin, bg="#000000")
        frame_img.pack(fill="x", padx=20, pady=2)

        e_imagen = tk.Entry(frame_img, width=30)
        e_imagen.pack(side="left")

        ruta_origen_img = {"path": None}

        def buscar_imagen():
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

        btn_buscar = tk.Button(
            frame_img,
            text="Elegir foto...",
            command=buscar_imagen,
            bg="#333333",
            fg="white",
            cursor="hand2"
        )
        btn_buscar.pack(side="left", padx=5)

        tk.Label(ventana_admin, text="URL Descarga Zip (.zip):", fg="white", bg="#000000").pack(anchor="w", padx=20)
        e_url = tk.Entry(ventana_admin, width=45)
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

            with open(ruta_local, "w", encoding="utf-8") as f:
                json.dump(self.lista_instalaciones_data, f, indent=4, ensure_ascii=False)

            messagebox.showinfo(
                "Éxito",
                "Modpack registrado con éxito.\nRecuerda subir el JSON y los archivos ZIP/imágenes a tu servidor.",
                parent=ventana_admin
            )
            ventana_admin.destroy()

        tk.Button(
            ventana_admin,
            text="Guardar y Publicar",
            command=guardar_modpack,
            bg="#A4C805",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        ).pack(pady=20)

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

        self.ram_panel.place(
            relx=1.0,
            x=-85,
            rely=0.5,
            anchor="e"
        )
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
            x=15,
            rely=1.0,
            y=-80,
            anchor="sw",
            width=225,
            height=320
        )
        self.instalaciones_mostradas = True
        self.canvas_instalaciones.yview_moveto(0)

    def perder_tiempo(self):
        for elemento in self.principal_panel.winfo_children():
            elemento.destroy()

        if self.title_img:
            self.title_label = tk.Label(
                self.principal_panel,
                image=self.title_img,
                bg="#010B3B"
            )
        else:
            self.title_label = tk.Label(
                self.principal_panel,
                text="PICKEAME LAUNCHER",
                font=("Arial", 32, "bold"),
                fg="#A4C805",
                bg="#010B3B"
            )
        self.title_label.pack(pady=20)
        self.title_label.bind("<Double-Button-1>", lambda e: self.abrir_login_admin())


root = tk.Tk()
app = pickeame(root)
root.mainloop()
