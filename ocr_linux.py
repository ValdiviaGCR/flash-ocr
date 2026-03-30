import tkinter as tk
from tkinter import font
import easyocr
from PIL import Image, ImageTk
import threading
import io
import os
import subprocess


class SnippingSurface(tk.Toplevel):
    def __init__(self, parent, image_path, on_snip_callback):
        super().__init__(parent)
        self.on_snip_callback = on_snip_callback

        # Cargar la captura previa para mostrarla en pantalla completa
        self.original_image = Image.open(image_path)
        self.tk_image = ImageTk.PhotoImage(self.original_image)

        self.attributes('-fullscreen', True)
        self.attributes('-topmost', True)
        self.overrideredirect(True)

        # El canvas ahora muestra la foto que acabamos de tomar
        self.canvas = tk.Canvas(self, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        # Capa oscurecida para que se vea dónde seleccionas
        self.canvas.create_rectangle(0, 0, self.winfo_screenwidth(), self.winfo_screenheight(),
                                     fill="black", stipple="gray50", state="disabled")

        self.start_x = self.start_y = self.rect = None
        self.canvas.bind("<ButtonPress-1>", self.start_rect)
        self.canvas.bind("<B1-Motion>", self.draw_rect)
        self.canvas.bind("<ButtonRelease-1>", self.end_rect)
        self.bind("<Escape>", lambda e: self.destroy())

    def start_rect(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1,
                                                 outline='#00ff00', width=2)

    def draw_rect(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def end_rect(self, event):
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)

        # Cortar la imagen original basándonos en la selección
        cropped_img = self.original_image.crop((x1, y1, x2, y2))
        self.on_snip_callback(cropped_img)
        self.destroy()


class ModernOCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flash OCR (Snapshot Method)")
        self.root.geometry("600x500")

        self.lbl_estado = tk.Label(root, text="Cargando motor...", fg="gray")
        self.lbl_estado.pack(pady=10)

        self.btn_snip = tk.Button(root, text="NUEVA CAPTURA", command=self.pre_capture,
                                  bg="#1a73e8", fg="white", padx=20, pady=10, state=tk.DISABLED)
        self.btn_snip.pack(pady=10)

        self.txt_out = tk.Text(root, font=("Consolas", 11), wrap=tk.WORD)
        self.txt_out.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        threading.Thread(target=self.cargar_motor, daemon=True).start()

    def cargar_motor(self):
        self.reader = easyocr.Reader(['es'], gpu=False)
        self.root.after(0, lambda: [self.lbl_estado.config(text="● Listo", fg="green"),
                                    self.btn_snip.config(state=tk.NORMAL)])

    def pre_capture(self):
        self.root.withdraw()  # Escondemos la app
        time.sleep(0.3)  # Esperamos a que desaparezca

        temp_file = "full_screen.png"
        # Tomamos la foto de TODO el escritorio
        subprocess.run(["scrot", temp_file], check=True)

        # Lanzamos el selector pasándole la foto
        SnippingSurface(self.root, temp_file, self.procesar_recorte)

        # Limpieza del archivo temporal
        if os.path.exists(temp_file):
            os.remove(temp_file)

    def procesar_recorte(self, img_obj):
        self.root.deiconify()
        self.lbl_estado.config(text="Leyendo texto...", fg="orange")

        def run():
            buf = io.BytesIO()
            img_obj.save(buf, format='PNG')
            results = self.reader.readtext(buf.getvalue(), detail=0)
            texto = "\n".join(results)
            self.root.after(0, lambda: self.mostrar(texto))

        threading.Thread(target=run, daemon=True).start()

    def mostrar(self, texto):
        self.txt_out.delete('1.0', tk.END)
        self.txt_out.insert(tk.END, texto)
        self.lbl_estado.config(text="● Completado", fg="green")


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernOCRApp(root)
    root.mainloop()