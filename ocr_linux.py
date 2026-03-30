import tkinter as tk
from tkinter import messagebox, font
import easyocr
import subprocess
import os
import threading
import time

# --- CONFIGURACIÓN DE COLORES Y ESTILOS ---
# Tonos inspirados en GNOME/Adwaita
BG_COLOR = "#f6f6f6"  # Gris muy claro de fondo
HEADER_COLOR = "#ffffff"  # Blanco puro para la cabecera
TEXT_COLOR = "#2e3436"  # Gris oscuro para el texto principal
ACCENT_BLUE = "#3584e4"  # Azul vibrante moderno (Botón Capturar)
ACCENT_GREEN = "#2ec27e"  # Verde moderno (Botón Copiar)
FONT_NAME = "DejaVu Sans"  # Fuente nativa de Ubuntu


class FlashOCRFancy:
    def __init__(self, root):
        self.root = root
        self.root.title("Flash OCR")
        self.root.geometry("750x650")
        self.root.configure(bg=BG_COLOR)

        # Definir Fuentes Personalizadas
        self.title_font = font.Font(family=FONT_NAME, size=16, weight="bold")
        self.normal_font = font.Font(family=FONT_NAME, size=10)
        self.button_font = font.Font(family=FONT_NAME, size=11, weight="bold")
        self.code_font = font.Font(family="Consolas", size=12)  # Para el texto extraído

        # --- CABECERA (HEADER) ---
        self.header_frame = tk.Frame(root, bg=HEADER_COLOR, height=70, relief="flat")
        self.header_frame.pack(fill=tk.X, side=tk.TOP)
        self.header_frame.pack_propagate(False)  # Forzar altura

        # Título con icono simulado
        tk.Label(self.header_frame, text="⚡", font=("Arial", 20), bg=HEADER_COLOR, fg=ACCENT_BLUE).pack(side=tk.LEFT,
                                                                                                        padx=(20, 5))
        tk.Label(self.header_frame, text="Flash OCR", font=self.title_font, bg=HEADER_COLOR, fg=TEXT_COLOR).pack(
            side=tk.LEFT, padx=0)

        # Indicador de estado visual
        self.status_frame = tk.Frame(self.header_frame, bg=HEADER_COLOR)
        self.status_frame.pack(side=tk.RIGHT, padx=20)

        self.lbl_dot = tk.Label(self.status_frame, text="●", font=("Arial", 12), bg=HEADER_COLOR, fg="gray")
        self.lbl_dot.pack(side=tk.LEFT, padx=5)
        self.lbl_status = tk.Label(self.status_frame, text="Cargando motor...", font=self.normal_font, bg=HEADER_COLOR,
                                   fg="gray")
        self.lbl_status.pack(side=tk.LEFT, padx=0)

        # --- PANEL DE CONTROL (BOTONES) ---
        self.ctrl_frame = tk.Frame(root, bg=BG_COLOR)
        self.ctrl_frame.pack(pady=25, fill=tk.X)

        # Botón Capturar Area (Azul)
        # pady y padx internos simulan el redondeado y espaciado moderno
        self.btn_snip = tk.Button(self.ctrl_frame, text="SELECCIONAR ÁREA", command=self.iniciar_ocr_nativo,
                                  bg=ACCENT_BLUE, fg="white", font=self.button_font,
                                  activebackground="#62a0ea", activeforeground="white",
                                  padx=25, pady=12, borderwidth=0, cursor="hand2", state=tk.DISABLED)
        self.btn_snip.pack(side=tk.LEFT, padx=(30, 10))

        # Botón Copiar (Verde)
        self.btn_copy = tk.Button(self.ctrl_frame, text="COPIAR TEXTO", command=self.copiar_texto,
                                  bg=ACCENT_GREEN, fg="white", font=self.button_font,
                                  activebackground="#57e389", activeforeground="white",
                                  padx=25, pady=12, borderwidth=0, cursor="hand2", state=tk.DISABLED)
        self.btn_copy.pack(side=tk.LEFT, padx=10)

        # Botón Limpiar (Gris suave)
        self.btn_clear = tk.Button(self.ctrl_frame, text="LIMPIAR", command=self.limpiar_todo,
                                   bg="#dadada", fg=TEXT_COLOR, font=("DejaVu Sans", 9),
                                   padx=15, pady=8, borderwidth=0, cursor="hand2")
        self.btn_clear.pack(side=tk.RIGHT, padx=(10, 30))

        # --- ÁREA DE TEXTO EXTRAÍDO ---
        self.text_container = tk.Frame(root, bg=BG_COLOR)
        self.text_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))

        # Scrollbar moderno (flaco)
        self.scrollbar = tk.Scrollbar(self.text_container, width=10)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Texto widget con bordes planos y espaciado interno (padding)
        self.txt_out = tk.Text(self.text_container, font=self.code_font, wrap=tk.WORD,
                               bg="#ffffff", fg=TEXT_COLOR, bd=0, relief="flat",
                               padx=20, pady=20, yscrollcommand=self.scrollbar.set)
        self.txt_out.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.txt_out.yview)

        # Iniciar carga del motor en segundo plano para no congelar la UI
        threading.Thread(target=self.cargar_motor_async, daemon=True).start()

    def set_status(self, text, color):
        self.lbl_dot.config(fg=color)
        self.lbl_status.config(text=text)

    def cargar_motor_async(self):
        # Mantenemos la lógica de carga asíncrona
        try:
            self.reader = easyocr.Reader(['es'], gpu=False)
            self.root.after(0, lambda: [
                self.set_status("● Listo", ACCENT_GREEN),
                self.btn_snip.config(state=tk.NORMAL)
            ])
        except Exception:
            self.root.after(0, lambda: self.set_status("Error motor", "red"))

    def iniciar_ocr_nativo(self):
        # --- MISMA LÓGICA DE ANTES ---
        temp_file = os.path.expanduser("~/screenshot_fancy_temp.png")
        try:
            self.root.withdraw()
            time.sleep(0.3)

            subprocess.run(["gnome-screenshot", "-a", "-f", temp_file], check=True)

            if os.path.exists(temp_file):
                self.set_status("● Procesando OCR...", "#f5c211")
                self.root.deiconify()

                # Ejecutar OCR en hilo para no colgar la UI
                threading.Thread(target=self.run_ocr_async, args=(temp_file,), daemon=True).start()
            else:
                self.root.deiconify()
                self.set_status("● Captura cancelada", "#f66")

        except Exception as e:
            self.root.deiconify()
            messagebox.showerror("Error", f"Instala gnome-screenshot:\nsudo apt install gnome-screenshot\n\n{e}")

    def run_ocr_async(self, file_path):
        # Mantenemos la lectura y limpieza de archivo
        try:
            resultados = self.reader.readtext(file_path, detail=0)
            texto_final = "\n\n".join(resultados)

            if os.path.exists(file_path): os.remove(file_path)

            self.root.after(0, lambda: self.mostrar_resultado(texto_final))
        except:
            self.root.after(0, lambda: self.set_status("Error OCR", "red"))

    def mostrar_resultado(self, texto):
        self.txt_out.delete('1.0', tk.END)
        self.txt_out.insert(tk.END, texto)
        self.set_status("● Escaneo completado", ACCENT_GREEN)
        self.btn_copy.config(state=tk.NORMAL)

    def copiar_texto(self):
        texto = self.txt_out.get('1.0', tk.END).strip()
        if texto:
            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            self.set_status("● ¡Texto copiado!", ACCENT_BLUE)
            # Volver a poner el estado "Listo" después de 2 segundos
            self.root.after(2000, lambda: self.set_status("● Listo", ACCENT_GREEN))

    def limpiar_todo(self):
        self.txt_out.delete('1.0', tk.END)
        self.btn_copy.config(state=tk.DISABLED)
        self.set_status("● Listo", ACCENT_GREEN)


if __name__ == "__main__":
    root = tk.Tk()
    # Usar fuente nativa para que se vea bien en Ubuntu
    root.option_add('*Font', 'DejaVu Sans 10')
    app = FlashOCRFancy(root)
    root.mainloop()