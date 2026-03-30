import tkinter as tk
import easyocr
import subprocess
import os
import time

# 1. Cargar el motor (Español)
reader = easyocr.Reader(['es'], gpu=False)


def capturar():
    # Archivo temporal en tu carpeta personal
    temp_file = os.path.expanduser("~/captura.png")

    root.withdraw()  # Esconder ventana
    time.sleep(0.3)

    try:
        # Usar la herramienta nativa de Ubuntu para seleccionar área
        subprocess.run(["gnome-screenshot", "-a", "-f", temp_file], check=True)

        if os.path.exists(temp_file):
            # Procesar la imagen
            res = reader.readtext(temp_file, detail=0)
            texto = "\n\n".join(res)

            # Mostrar resultado
            txt.delete("1.0", tk.END)
            txt.insert(tk.END, texto)
            os.remove(temp_file)
    except:
        pass

    root.deiconify()  # Regresar ventana


def copiar():
    root.clipboard_clear()
    root.clipboard_append(txt.get("1.0", tk.END).strip())


# --- Interfaz Simple ---
root = tk.Tk()
root.title("Flash OCR")
root.geometry("500x550")
root.configure(bg="#f0f0f0")

# Botón Principal (Azul)
btn_frame = tk.Frame(root, bg="#f0f0f0")
btn_frame.pack(pady=20)

tk.Button(btn_frame, text=" ✂️ CAPTURAR ", command=capturar, bg="#3584e4", fg="white",
          font=("Arial", 12, "bold"), padx=15, pady=8, bd=0).pack(side=tk.LEFT, padx=5)

tk.Button(btn_frame, text=" 📋 COPIAR ", command=copiar, bg="#2ec27e", fg="white",
          font=("Arial", 12, "bold"), padx=15, pady=8, bd=0).pack(side=tk.LEFT, padx=5)

# Área de Texto
txt = tk.Text(root, font=("Arial", 11), padx=10, pady=10, bd=0)
txt.pack(fill="both", expand=True, padx=20, pady=10)

root.mainloop()