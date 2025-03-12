import customtkinter as ctk
import pywinstyles
from PIL import Image
import cv2
import glob
import tkinter.messagebox as messagebox 
import os
from ultralytics import YOLO
import time 
import threading

# Obtiene el directorio base del script.
base_dir = os.pata.dirname(os.path.abspath(__file__))
resources_folder = os.path.join (base_dir, "resources")

user_media_folder = os.path.join (base_dir, "images and recordings")
if not os.path.exists (user_media_folder):
  os.makedirs (user_media_folder)

model_path = os.path.join ( resources_folder, "best.pt")
model = YOLO (model_path) 

def video_loop():
  global alarm_active
  cap = cv2.VideoCapture(0)
  if not cap.is0pened():
    print("No se pudo abrir la camara")
    return
   
   video_start_time = time.time()
   while True:
    ret, frame = cap.read()
    if not ret:
     break
     
    resultados = model(frame, conf=0.4)
    rendered_frame = resultados[0].plot()

    if time.time() - video_start_time >=1:
      detections = []
      if hasattr(resultados[0], "boxes") and resultados[0].boxes is not None:
                detections = resultados[0].boxes.data.tolist()
            if not alarm_active and any(det[4] >= 0.5 for det in detections)
                app.after(0, show_alarm)
    cv2.imshow('detención de arma - Video', rendered_frame) 
    if cv2.waitkey(5) & 0xFF == 27
     break

   cap.release()
   cv2.destroyAllWindows()

def star_video_thread():
  video_thread = threading.Thread(target=video_loop, daemon=True)
  video_thread.start()
  
def open_picture():
  top = ctk.CTKToplevel (app)
  top.title("selec image")
  top.geometry("400x200")
  ctk.set_appearance_mode("system")
  ctk.set_default_color_theme ("blue")            

  open_picture = cargar_imagen("abrir.png", (boton_ancho, boton_alto))
  exit_picture = cargar_imagen ("salir.png" , (boton_ancho, boton_alto))

  if not all ([open_picture, exit_picture]):
    print("Error: Una o más imágenes no se pudieron cargar. Verifica las rutas y nombres del archivo.") 
    top.destroy()
    return 

  image_files = glob.glob(os.path.join(user_media_folder, "*.png")) + \
                glob.glob(os.path.join(user_media_folder, "*.jpg"))
  if not image_files:
    messagebox.showerror("Error","No se encontraron imagenes en 'images and recordings'.")
    top.destroy()
    return

  selected_image =ctk.StringVar (value =image_files[0])
  option_menu = ctk.CTKOptionMenu(top, values= image_files, variable=selected_image)
  option_menu.pack(pady= 20)

  button_frame = ctk.CTKFrame (top)
  button_frame.pack (pady=10)

  def open_selection():
    path_image = selected_image.get()
    image = cv2.imread(path_image)
    if image is None: 
      messagebox.showerror("Error", "No se puedo cargar la imagen seleccionada")
      return

    results = model(imagen, conf=0.3)
    rendered image = resultados[0].plot()

    cv2.imshow('Detección de arma - imagen', imagen_renderizada)
    cv2.waitKey(0)
    cv2.destroyALLWindows()
    top.destroy()

app = ctk.CTk()
app.geometry("600x400")
app.title("SentinelAI")
pywinstyles.apply_style(window=app, style="aero")
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

title_img_path = os.path.join (resources_folder, "title.png")
img = Image.open (title_img_path)
title_image = ctk.CTKImage (light_image = img, dark_image =img, size=(600, 200))
title_label = ctk.CTKLaber (app, image=title_image, text ="")
title_label.pack (side= "top", pady=20)

def load_imagen(nombre_archivo, tamaño):
    path_image = os.path.join(resources_folder, nombre_archivo)
    if not os.path.exists(path_image):
        print(f"Advertencia: La imagen '{path_image}' no existe.")
        return None
    img = Image.open(path_image).resize(tamaño, Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=img, dark_image=img, size=tamaño)

# Tamaño de los botones
boton_ancho = 146
boton_alto = 48

# Carga de imágenes
video_image = load_image("camara.png", (boton_ancho, boton_alto))
imagen_image = load_image("imagen.png", (boton_ancho, boton_alto))
salir_image = load_image("salir.png", (boton_ancho, boton_alto))

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
