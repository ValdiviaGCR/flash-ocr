import tkinter as tk
from tkinter import messagebox, font
import easyocr
from PIL import ImageGrab
import threading
import io
import time


class SnippingSurface(tk.Toplevel):
    def __init__(self, parent, on_snip_callback):
        super().__init__(parent)
        self.parent = parent
        self.on_snip_callback = on_snip_callback
        self.attributes('-alpha', 0.25)  # Un poco más transparente para ver mejor
        self.attributes('-fullscreen', True)
        self.attributes('-topmost', True)
        self.overrideredirect(True)
        self.canvas = tk.Canvas(self, cursor="cross", bg="#333333")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.start_x = self.start_y = self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.start_rect)
        self.canvas.bind("<B1-Motion>", self.draw_rect)
        self.canvas.bind("<ButtonRelease-1>", self.end_rect)
        self.bind("<Escape>", lambda e: self.destroy())

    def start_rect(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='#00ff00', width=2)

    def draw_rect(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def end_rect(self, event):
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
        self.on_snip_callback(x1, y1, x2, y2)
        self.destroy()


class ModernOCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flash OCR Pro")
        self.root.geometry("700x650")
        self.root.configure(bg="#f0f2f5")  # Gris claro moderno

        # Fuentes personalizadas
        self.title_font = font.Font(family="Segoe UI", size=14, weight="bold")
        self.button_font = font.Font(family="Segoe UI", size=10, weight="bold")
        self.text_font = font.Font(family="Consolas", size=11)

        # --- Header ---
        header = tk.Frame(root, bg="#ffffff", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        tk.Label(header, text="⚡ Flash OCR", font=self.title_font, bg="#ffffff", fg="#1a73e8").pack(pady=15, padx=20,
                                                                                                    side=tk.LEFT)

        self.lbl_estado = tk.Label(header, text="Iniciando...", font=("Segoe UI", 9), bg="#ffffff", fg="#5f6368")
        self.lbl_estado.pack(pady=15, padx=20, side=tk.RIGHT)

        # --- Panel de Control ---
        ctrl_frame = tk.Frame(root, bg="#f0f2f5")
        ctrl_frame.pack(pady=20)

        # Botón Capturar
        self.btn_snip = tk.Button(ctrl_frame, text="✂️ NUEVA CAPTURA", command=self.lanzar_selector,
                                  bg="#1a73e8", fg="white", font=self.button_font,
                                  padx=20, pady=10, borderwidth=0, cursor="hand2")
        self.btn_snip.pack(side=tk.LEFT, padx=10)

        # Botón Copiar
        self.btn_copy = tk.Button(ctrl_frame, text="📋 COPIAR", command=self.copiar_texto,
                                  bg="#34a853", fg="white", font=self.button_font,
                                  padx=20, pady=10, borderwidth=0, cursor="hand2", state=tk.DISABLED)
        self.btn_copy.pack(side=tk.LEFT, padx=10)

        # Botón Limpiar
        self.btn_clear = tk.Button(ctrl_frame, text="🗑️ LIMPIAR", command=self.limpiar_todo,
                                   bg="#ea4335", fg="white", font=self.button_font,
                                   padx=15, pady=10, borderwidth=0, cursor="hand2")
        self.btn_clear.pack(side=tk.LEFT, padx=10)

        # --- Área de Texto ---
        text_container = tk.Frame(root, bg="#f0f2f5")
        text_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Scrollbar y Text widget
        scrollbar = tk.Scrollbar(text_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.txt_out = tk.Text(text_container, font=self.text_font, wrap=tk.WORD,
                               bg="#ffffff", fg="#202124", borderwidth=1, relief="flat",
                               padx=15, pady=15, yscrollcommand=scrollbar.set)
        self.txt_out.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.txt_out.yview)

        # Iniciar motor en segundo plano
        threading.Thread(target=self.cargar_motor, daemon=True).start()

    def cargar_motor(self):
        try:
            self.reader = easyocr.Reader(['es'], gpu=False)
            self.root.after(0, lambda: self.lbl_estado.config(text="● Motor Listo", fg="#34a853"))
        except Exception as e:
            self.root.after(0, lambda: self.lbl_estado.config(text="Error al cargar motor", fg="red"))

    def lanzar_selector(self):
        self.root.withdraw()
        time.sleep(0.2)
        SnippingSurface(self.root, self.procesar)

    def procesar(self, x1, y1, x2, y2):
        self.root.deiconify()
        if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
            self.lbl_estado.config(text="Captura cancelada", fg="#ea4335")
            return

        self.lbl_estado.config(text="Procesando...", fg="#fbbc04")
        threading.Thread(target=self.run_ocr, args=((x1, y1, x2, y2),)).start()

    def run_ocr(self, bbox):
        try:
            img = ImageGrab.grab(bbox=bbox)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            results = self.reader.readtext(buf.getvalue(), detail=0)
            texto_final = "\n\n".join(results)
            self.root.after(0, self.mostrar_resultado, texto_final)
        except Exception as e:
            self.root.after(0, self.lbl_estado.config, {"text": "Error en OCR", "fg": "red"})

    def mostrar_resultado(self, texto):
        self.txt_out.delete('1.0', tk.END)
        self.txt_out.insert(tk.END, texto)
        self.lbl_estado.config(text="● Escaneo completado", fg="#34a853")
        self.btn_copy.config(state=tk.NORMAL)

    def copiar_texto(self):
        texto = self.txt_out.get('1.0', tk.END).strip()
        if texto:
            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            # Feedback visual en el botón
            original_text = self.btn_copy.cget("text")
            self.btn_copy.config(text="✅ ¡COPIADO!", bg="#1e7e34")
            self.root.after(1500, lambda: self.btn_copy.config(text=original_text, bg="#34a853"))

    def limpiar_todo(self):
        self.txt_out.delete('1.0', tk.END)
        self.btn_copy.config(state=tk.DISABLED)
        self.lbl_estado.config(text="Listo.", fg="#5f6368")


if __name__ == "__main__":
    root = tk.Tk()
    # Icono genérico para que no se vea el de Python (opcional)
    app = ModernOCRApp(root)
    root.mainloop()