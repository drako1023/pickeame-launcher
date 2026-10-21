
import tkinter as tk
from pathlib import Path
from tkinter import ttk


class pickeame:
    def __init__(self, root):
        self.root = root
        self.root.title("Fyham Launcher")
        self.root.geometry("1920x1080")
        self.root.minsize(700, 450)

        # Obtener la ruta de la carpeta del programa
        base_dir = Path(__file__).resolve().parent

        # Panel principal
        self.principal_panel = tk.Frame(
            self.root,
            bg="#010B3B"
        )
        self.principal_panel.pack(
            side="top",
            fill="both",
            expand=True
        )

        # Barra inferior
        self.sidebar = tk.Frame(
            self.root,
            bg="#000000",
            height=200
        )
        self.sidebar.pack(
            side="bottom",
            fill="x"
        )
        self.sidebar.pack_propagate(False)

        # Contenedor para centrar los botones
        self.botones_frame = tk.Frame(
            self.sidebar,
            bg="#000000"
        )
        self.botones_frame.pack(expand=True)

        # Cargar imagen del título
        ruta_imagen = base_dir / "recursos" / "titulo.png"

        self.title_img = tk.PhotoImage(
            master=self.root,
            file=str(ruta_imagen)
        )
        self.title_img = self.title_img.subsample(2, 2)

        # Mostrar imagen del título
        self.title_label = tk.Label(
            self.principal_panel,
            image=self.title_img,
            bg="#010B3B"
        )
        self.title_label.pack(pady=5)

        # Botón para perder el tiempo
        self.boton_jugar = tk.Button(
            self.botones_frame,
            text="Perder el tiempo",
            command=self.perder_tiempo,
            bg="#A4C805",
            fg="#FFFFFF",
            font=("Arial", 16, "bold"),
            activebackground="#0A8C2D",
            activeforeground="white",
            width=15,
            height=2,
            cursor="hand2"
        )
        self.boton_jugar.pack(
            side="left",
            padx=15,
            pady=30
        )

        # Botón para instalar el modpack
        self.boton_mod_pack = tk.Button(
            self.botones_frame,
            text="Instalar modpack",
            command=self.instalar_mod_pack,
            bg="#DE0433",
            fg="#FFFFFF",
            font=("Arial", 16, "bold"),
            activebackground="#0A8C2D",
            activeforeground="white",
            width=15,
            height=2,
            cursor="hand2"
        )
        self.boton_mod_pack.pack(
            side="left",
            padx=15,
            pady=30
        )

    # Acción del primer botón
    def perder_tiempo(self):
        print("¡Perdiendo el tiempo!")

    # Abrir la ventana de instalación
    def instalar_mod_pack(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Instalación del modpack de turno")
        ventana.geometry("400x200")
        ventana.configure(bg="#010B3B")
        ventana.resizable(False, False)

        # Título de la ventana
        titulo = tk.Label(
            ventana,
            text="Instalación del modpack",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#010B3B"
        )
        titulo.pack(pady=10)

        # Mensaje de estado
        mensaje = tk.Label(
            ventana,
            text="Preparado para instalar",
            fg="white",
            bg="#010B3B",
            font=("Arial", 11)
        )
        mensaje.pack(pady=5)


        progreso = ttk.Progressbar(
            ventana,
            orient="horizontal",
            length=301,
            mode="determinate",
            maximum=100
        )
        progreso.pack(pady=10)


        porcentaje = tk.Label(
            ventana,
            text="0%",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#FAEE09", 
        )
        porcentaje.pack()

        avance = {"valor": 0}

        def avanzar():
            if avance["valor"] < 100:
                avance["valor"] += 1
                progreso["value"] = avance["valor"]
                porcentaje.config(
                    text=f"{avance['valor']}%"
                )
                ventana.after(50, avanzar)
            else:
                mensaje.config(text="Instalación completada ahora puedes ir a jugar tu mierda")

        def comenzar():
            boton.config(state="disabled")
            mensaje.config(text="Instalando...")
            avanzar()

        # Botón de instalación
        boton = tk.Button(
            ventana,
            text="Instalar",
            command=comenzar,
            bg="#DE0433",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2"
        )
        boton.pack(pady=10)


root = tk.Tk()
app = pickeame(root)
root.mainloop()
