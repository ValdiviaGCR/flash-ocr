import tkinter as tk
from tkinter import messagebox
import easyocr
import subprocess
import os
import time

# 1. Cargar el motor (Español)
try:
    reader = easyocr.Reader(['es'], gpu=False)
except:
    print("Error al cargar el motor de OCR.")


def capturar():
    temp_file = os.path.expanduser("~/captura.png")

    # Ocultar ventana principal
    root.withdraw()
    time.sleep(0.3)

    try:
        # Intentar ejecutar la captura nativa de Ubuntu
        subprocess.run(["gnome-screenshot", "-a", "-f", temp_file], check=True)

        if os.path.exists(temp_file):
            res = reader.readtext(temp_file, detail=0)
            texto = "\n\n".join(res)

            txt.delete("1.0", tk.END)
            txt.insert(tk.END, texto)
            os.remove(temp_file)

    except FileNotFoundError:
        # SI NO ESTÁ INSTALADO, AVISAR AQUÍ:
        messagebox.showerror("Error de Sistema",
                             "No se encontró 'gnome-screenshot'.\n\n"
                             "Por favor, instálalo ejecutando esto en tu terminal:\n"
                             "sudo apt install gnome-screenshot")
    except Exception as e:
        print(f"Error inesperado: {e}")

    root.deiconify()  # Regresar la ventana pase lo que pase


def copiar():
    root.clipboard_clear()
    root.clipboard_append(txt.get("1.0", tk.END).strip())


# --- Interfaz Simple ---
root = tk.Tk()
root.title("Flash OCR")
root.geometry("500x550")
root.configure(bg="#f0f0f0")

btn_frame = tk.Frame(root, bg="#f0f0f0")
btn_frame.pack(pady=20)

tk.Button(btn_frame, text=" ✂️ CAPTURAR ", command=capturar, bg="#3584e4", fg="white",
          font=("Arial", 11, "bold"), padx=15, pady=8, bd=0, cursor="hand2").pack(side=tk.LEFT, padx=5)

tk.Button(btn_frame, text=" 📋 COPIAR ", command=copiar, bg="#2ec27e", fg="white",
          font=("Arial", 11, "bold"), padx=15, pady=8, bd=0, cursor="hand2").pack(side=tk.LEFT, padx=5)

txt = tk.Text(root, font=("Arial", 11), padx=10, pady=10, bd=0)
txt.pack(fill="both", expand=True, padx=20, pady=(0, 20))

root.mainloop()