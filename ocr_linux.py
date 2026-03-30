import tkinter as tk
from tkinter import messagebox
import easyocr
import subprocess
import os
import time

# Cargamos el motor una sola vez
reader = easyocr.Reader(['es'], gpu=False)


def iniciar_ocr_nativo():
    # 1. Definimos el nombre del archivo temporal
    temp_file = os.path.expanduser("~/screenshot_temp.png")

    # 2. Llamamos al capturador nativo de GNOME
    # -a abre el selector de área directamente
    # -f guarda el resultado en el archivo
    try:
        root.withdraw()  # Escondemos nuestra ventana

        # Este comando abre la interfaz nativa de Ubuntu para seleccionar área
        subprocess.run(["gnome-screenshot", "-a", "-f", temp_file], check=True)

        if os.path.exists(temp_file):
            # 3. Procesamos la imagen que el sistema nos entregó
            lbl_status.config(text="Leyendo texto...", fg="orange")
            root.deiconify()

            resultados = reader.readtext(temp_file, detail=0)
            texto_final = "\n".join(resultados)

            txt_output.delete("1.0", tk.END)
            txt_output.insert(tk.END, texto_final)

            # Limpiar
            os.remove(temp_file)
            lbl_status.config(text="● Listo", fg="green")
        else:
            root.deiconify()
            lbl_status.config(text="Captura cancelada", fg="red")

    except Exception as e:
        root.deiconify()
        messagebox.showerror("Error",
                             "Asegúrate de tener gnome-screenshot instalado:\nsudo apt install gnome-screenshot")


# --- INTERFAZ ---
root = tk.Tk()
root.title("Flash OCR Portal")
root.geometry("500x500")

lbl_status = tk.Label(root, text="● Motor Cargado", fg="green", font=("Arial", 10))
lbl_status.pack(pady=5)

btn = tk.Button(root, text="SELECCIONAR ÁREA", command=iniciar_ocr_nativo,
                bg="#1a73e8", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10)
btn.pack(pady=20)

txt_output = tk.Text(root, font=("Consolas", 11), padx=10, pady=10)
txt_output.pack(fill="both", expand=True, padx=15, pady=15)

root.mainloop()