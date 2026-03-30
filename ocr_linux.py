import tkinter as tk
import easyocr
from PIL import Image, ImageTk
import subprocess
import os
import time

# --- CONFIGURACIÓN DEL MOTOR ---
# Esto descarga el modelo la primera vez (pesa unos 150MB)
reader = easyocr.Reader(['es'], gpu=False)


def realizar_ocr(img_recortada):
    # Guardar recorte temporal para que easyocr lo lea
    img_recortada.save("crop.png")
    resultados = reader.readtext("crop.png", detail=0)
    texto = "\n".join(resultados)

    # Mostrar en la ventana principal
    txt_output.delete("1.0", tk.END)
    txt_output.insert(tk.END, texto)
    os.remove("crop.png")
    root.deiconify()  # Regresar la ventana principal


def iniciar_captura():
    root.withdraw()  # Esconder la ventana para que no salga en la foto
    time.sleep(0.5)  # Pausa para que desaparezca

    # 1. Tomar captura de pantalla completa
    subprocess.run(["scrot", "temp.png"], check=True)

    # 2. Crear ventana de selección sobre la foto
    ventana_sel = tk.Toplevel()
    ventana_sel.attributes("-fullscreen", True)

    img_full = Image.open("temp.png")
    img_tk = ImageTk.PhotoImage(img_full)

    canvas = tk.Canvas(ventana_sel, cursor="cross", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=img_tk)
    canvas.image = img_tk  # Mantener referencia

    coords = {"x": 0, "y": 0, "rect": None}

    def start_rect(e):
        coords["x"], coords["y"] = e.x, e.y
        coords["rect"] = canvas.create_rectangle(e.x, e.y, e.x, e.y, outline="green", width=2)

    def draw_rect(e):
        canvas.coords(coords["rect"], coords["x"], coords["y"], e.x, e.y)

    def end_rect(e):
        x1, y1 = min(coords["x"], e.x), min(coords["y"], e.y)
        x2, y2 = max(coords["x"], e.x), max(coords["y"], e.y)

        recorte = img_full.crop((x1, y1, x2, y2))
        ventana_sel.destroy()
        os.remove("temp.png")
        realizar_ocr(recorte)

    canvas.bind("<ButtonPress-1>", start_rect)
    canvas.bind("<B1-Motion>", draw_rect)
    canvas.bind("<ButtonRelease-1>", end_rect)
    ventana_sel.bind("<Escape>", lambda e: [ventana_sel.destroy(), root.deiconify()])


# --- VENTANA PRINCIPAL ---
root = tk.Tk()
root.title("OCR Simple Ubuntu")
root.geometry("400x400")

btn = tk.Button(root, text="CAPTURAR PANTALLA", command=iniciar_captura,
                bg="blue", fg="white", font=("Arial", 12, "bold"), pady=10)
btn.pack(pady=20)

txt_output = tk.Text(root, font=("Arial", 11))
txt_output.pack(padx=10, pady=10, fill="both", expand=True)

root.mainloop()