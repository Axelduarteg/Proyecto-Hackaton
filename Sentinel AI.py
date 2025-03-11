import customtkinter as ctk
import pywinstyles
from PIL import Image, ImageSequence
import cv2
import glob 
import tkinter.messagebox as messgebox
from ultralytics import YOLO
import os 

base_dir = os.pata.dirname(os.path.abspath(__file__))
resources_folder = os.path.join (base_dir, "resources")

user_media_folder = os.path.join (base_dir, "images and recordings")
if not os.path.exists (user_media_folder):
  os.makedirs (user_media_folder)

model_path = os.path.join ( resources_folder, "best.pt")
model = YOLO (model_path) 

def open_picture():
  top = ctk.CTKToplevel (app)
  top.title("selec image")
  top.geometry("400x200")
  ctk.set_appearance_mode("system")
  ctk.set_default_color_theme ("blue")


open_picture = load_image("abrir.png", (boton_ancho, boton_alto))
exit_picture = load_image ("salir.png", (boton_ancho, boton_alto))

if not all ([open_picture, exit_picture]):
  print("Error: Una o más imágenes no se pudieron cargar. Verifica las rutas y nombres del archivo.") 
  top.destroy()
  return 

image_files = glob.glob(os.path.join(user_media_folder, "*.png")) + \
              glob.glob(os.path.join(user_media_flder, "*.jpg"))
if not image_files:
  messagebox.showerror("Error","No se encontraron imagenes en 'images and recordings'.")
  top.destroy()
  return

selected_image =ctk.StringVar (value =iamge_files[0])
option_menu = CTK.CTKOptionMenu(top, values=image_files, variable =selccted_image)
option_menu.pack(pady=20)



app = ctk.CTk()
app.geometry("600x400")
app.title("SentinelAI")
pywinstyles.apply_style(window=app, style="aero")
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

title_img_path = os.path.join (resources_folder, "title.png")
img = Image.open (title_img_path)
title_image = ctk.CTKImage (light_image = img, dark_image =img, size=(600, 200))
title_label = ctk:CTKLaber (app, image=title_image, text ="")
title_label.pack (side= "top", pady=20)

def cargar_imagen(nombre_archivo, tamaño):
    ruta_imagen = os.path.join(recursos_folder, nombre_archivo)
    if not os.path.exists(ruta_imagen):
        print(f"Advertencia: La imagen '{ruta_imagen}' no existe.")
        return None
    img = Image.open(ruta_imagen).resize(tamaño, Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=img, dark_image=img, size=tamaño)

# Tamaño de los botones
boton_ancho = 146
boton_alto = 48

# Carga de imágenes
video_image = cargar_imagen("camara.png", (boton_ancho, boton_alto))
imagen_image = cargar_imagen("imagen.png", (boton_ancho, boton_alto))
salir_image = cargar_imagen("salir.png", (boton_ancho, boton_alto))

# Verifica que las imágenes se hayan cargado correctamente
if not all([video_image, imagen_image, salir_image]):
    print("Error: Una o más imágenes no se pudieron cargar. Verifica las rutas y nombres de archivo.")
    app.quit()

# Crea el frame para los botones
bottom_frame = ctk.CTkFrame(app)
bottom_frame.pack(side="bottom", fill="x", pady=10)
bottom_frame.columnconfigure([0, 1, 2], weight=1)

# Botón para Video
btn_video = ctk.CTkButton(
    bottom_frame,
    image=video_image,
    text="",
    command=,
    width=boton_ancho,
    height=boton_alto,
    fg_color=None  # Hace transparente el fondo del botón
)
btn_video.grid(row=0, column=0, padx=10)

# Botón para Imagen
btn_imagen = ctk.CTkButton(
    bottom_frame,
    image=imagen_image,
    text="",
    command=,
    width=boton_ancho,
    height=boton_alto,
    fg_color=None
)
btn_imagen.grid(row=0, column=1, padx=10)

# Botón para Salir
btn_salir = ctk.CTkButton(
    bottom_frame,
    image=salir_image,
    text="",
    command=,
    width=boton_ancho,
    height=boton_alto,
    fg_color=None
)
btn_salir.grid(row=0, column=2, padx=10)

app.mainloop()
                      
