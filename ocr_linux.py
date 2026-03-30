import tkinter as tk
from tkinter import font, messagebox
import easyocr
from PIL import Image, ImageTk
import threading
import io
import os
import subprocess
import time  # <--- IMPORTADO CORRECTAMENTE AHORA


class SnippingSurface(tk.Toplevel):
    def __init__(self, parent, image_path, on_snip_callback):
        super().__init__(parent)
        self.on_snip_callback = on_snip_callback

        # Cargar la captura previa
        self.original_image = Image.open(image_path)
        self.tk_image = ImageTk.PhotoImage(self.original_image)

        self.attributes('-fullscreen', True)
        self.attributes('-topmost', True)
        self.overrideredirect(True)

        self.canvas = tk.Canvas(self, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        # Efecto de oscurecimiento (simulado con un rectángulo semi-transparente si el sistema lo permite)
        # En Linux, a veces el stipple falla, así que usamos un borde verde chillón para la selección.
        self.start_x = self.start_y = self.rect = None
        self.canvas.bind("<ButtonPress-1>", self.start_rect)
        self.canvas.bind("<B1-Motion>", self.draw_rect)
        self.canvas.bind("<ButtonRelease-1>", self.end_rect)
        self.bind("<Escape>", lambda e: self.destroy())

    def start_rect(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1,
                                                 outline='#00ff00', width=3)

    def draw_rect(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def end_rect(self, event):
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)

        # Extraer el área de la imagen original
        cropped_img = self.original_image.crop((x1, y1, x2, y2))
        self.on_snip_callback(cropped_img)
        self.destroy()


class ModernOCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flash OCR Linux (Snapshot Mode)")
        self.root.geometry("700x600")
        self.root.configure(bg="#f0f2f5")

        self.main_font = font.Font(family="DejaVu Sans", size=10)
        self.title_font = font.Font(family="DejaVu Sans", size=14, weight="bold")

        # Header
        header = tk.Frame(root, bg="#ffffff", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        tk.Label(header, text="⚡ Flash OCR Linux", font=self.title_font, bg="#ffffff", fg="#1a73e8").pack(pady=15,
                                                                                                          padx=20,
                                                                                                          side=tk.LEFT)
        self.lbl_estado = tk.Label(header, text="Iniciando...", font=self.main_font, bg="#ffffff", fg="#5f6368")
        self.lbl_estado.pack(pady=15, padx=20, side=tk.RIGHT)

        # Botones
        ctrl_frame = tk.Frame(root, bg="#f0f2f5")
        ctrl_frame.pack(pady=20)

        self.btn_snip = tk.Button(ctrl_frame, text="NUEVA CAPTURA", command=self.pre_capture,
                                  bg="#1a73e8", fg="white", font=self.main_font, padx=20, pady=10,
                                  borderwidth=0, state=tk.DISABLED)
        self.btn_snip.pack(side=tk.LEFT, padx=10)

        self.btn_copy = tk.Button(ctrl_frame, text="COPIAR TEXTO", command=self.copiar_texto,
                                  bg="#34a853", fg="white", font=self.main_font, padx=20, pady=10,
                                  borderwidth=0, state=tk.DISABLED)
        self.btn_copy.pack(side=tk.LEFT, padx=10)

        # Área de Texto
        self.txt_out = tk.Text(root, font=("Consolas", 11), wrap=tk.WORD, bg="#ffffff", padx=15, pady=15)
        self.txt_out.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        threading.Thread(target=self.cargar_motor, daemon=True).start()

    def cargar_motor(self):
        try:
            self.reader = easyocr.Reader(['es'], gpu=False)
            self.root.after(0, lambda: [self.lbl_estado.config(text="● Motor Listo", fg="#34a853"),
                                        self.btn_snip.config(state=tk.NORMAL)])
        except:
            self.root.after(0, lambda: self.lbl_estado.config(text="Error Motor", fg="red"))

    def pre_capture(self):
        self.root.withdraw()
        time.sleep(0.4)  # Tiempo para que la ventana desaparezca

        temp_file = "full_screen_temp.png"
        try:
            # Captura con scrot
            subprocess.run(["scrot", temp_file], check=True)
            # Abrir selector
            SnippingSurface(self.root, temp_file, self.procesar_recorte)
        except Exception as e:
            messagebox.showerror("Error", f"Asegúrate de tener 'scrot' instalado:\nsudo apt install scrot\n\n{e}")
            self.root.deiconify()
        finally:
            # Borrar temporal después de un momento
            self.root.after(1000, lambda: os.remove(temp_file) if os.path.exists(temp_file) else None)

    def procesar_recorte(self, img_obj):
        self.root.deiconify()
        self.lbl_estado.config(text="Procesando OCR...", fg="#fbbc04")

        def run():
            try:
                buf = io.BytesIO()
                img_obj.save(buf, format='PNG')
                results = self.reader.readtext(buf.getvalue(), detail=0)
                texto = "\n\n".join(results)
                self.root.after(0, lambda: self.mostrar_resultado(texto))
            except Exception as e:
                self.root.after(0, lambda: self.lbl_estado.config(text="Error OCR", fg="red"))

        threading.Thread(target=run, daemon=True).start()

    def mostrar_resultado(self, texto):
        self.txt_out.delete('1.0', tk.END)
        self.txt_out.insert(tk.END, texto)
        self.lbl_estado.config(text="● Escaneo listo", fg="#34a853")
        self.btn_copy.config(state=tk.NORMAL)

    def copiar_texto(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.txt_out.get('1.0', tk.END).strip())
        self.lbl_estado.config(text="● ¡Copiado al portapapeles!", fg="#1a73e8")