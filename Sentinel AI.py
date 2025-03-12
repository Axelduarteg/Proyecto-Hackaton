import customtkinter as ctk
import pywinstyles
from PIL import Image, ImageSequence
import cv2
from ultralytics import YOLO
import glob
import tkinter.messagebox as messagebox 
import os
import time
import threading
import pyautogui
import numpy as np
from datetime import datetime

# Variables globales para el control de la alarma
alarm_active = False
last_alarm_time = 0

# Definir la ruta base del proyecto
base_dir = os.path.dirname(os.path.abspath(__file__))

# Carpeta de recursos para el programa (contendrá best.pt, title.png, alarm.gif, etc.)
recursos_folder = os.path.join(base_dir, "resources")

# Carpeta donde el usuario colocará imágenes y grabaciones
user_media_folder = os.path.join(base_dir, "imagenes y grabaciones")
if not os.path.exists(user_media_folder):
    os.makedirs(user_media_folder)

# Cargar el modelo desde el archivo best.pt ubicado en la carpeta de recursos
model_path = os.path.join(recursos_folder, "best.pt")
model = YOLO(model_path)

def show_alarm():
    global alarm_active, last_alarm_time
    current_time = time.time()
    # Si la alarma ya está activa o si no ha pasado el tiempo de espera, salir
    if alarm_active or (current_time - last_alarm_time < 1):
        return

    alarm_active = True
    last_alarm_time = current_time

    # Función para grabar la pantalla mientras la alarma esté activa
    def record_screen():
        try:
            # Obtener dimensiones de la pantalla
            screen_size = pyautogui.size()
            
            # Crear nombre de archivo con fecha y hora
            timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            video_path = os.path.join(user_media_folder, f"screen_recording_{timestamp}.mp4")
            
            # Configurar grabación
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = 10.0  # Puedes ajustar los frames por segundo
            out = cv2.VideoWriter(video_path, fourcc, fps, screen_size)
            
            print("Iniciando grabación de pantalla en:", video_path)
            
            while alarm_active:
                img = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                out.write(frame)
                time.sleep(1 / fps)
            
            out.release()
            print("Grabación de pantalla finalizada.")
            
        except Exception as e:
            print("Error durante la grabación de pantalla:", e)

    # Iniciar la grabación en un hilo separado
    screen_thread = threading.Thread(target=record_screen, daemon=True)
    screen_thread.start()

    # Construir la ruta completa al GIF de alarma
    gif_path = os.path.join(recursos_folder, "alarm.gif")
    print("Buscando GIF en:", gif_path)
    
    if not os.path.exists(gif_path):
        print("No se encontró el archivo:", gif_path)
        alarm_active = False
        return
    
    try:
        im = Image.open(gif_path)
    except Exception as e:
        print("Error al cargar el GIF de alarma:", e)
        alarm_active = False
        return

    # Dimensiones para el pop up de la alarma
    win_width, win_height = 500, 275
    # Extraer los frames y convertirlos a CTkImage
    frames = []
    try:
        for frame in ImageSequence.Iterator(im):
            frame_copy = frame.copy().resize((win_width, win_height))
            ctk_img = ctk.CTkImage(light_image=frame_copy, dark_image=frame_copy, size=(win_width, win_height))
            frames.append(ctk_img)
    except Exception as e:
        print("Error al procesar los frames del GIF:", e)
        alarm_active = False
        return

    if not frames:
        print("No se pudieron obtener frames del GIF.")
        alarm_active = False
        return

    # Iniciar reproducción del audio de alarma
    mp3_path = os.path.join(recursos_folder, "alarm.mp3")
    print("Buscando audio en:", mp3_path)
    if not os.path.exists(mp3_path):
        print("No se encontró el archivo de audio:", mp3_path)
    else:
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(mp3_path)
            pygame.mixer.music.play(loops=-1)  # loops=-1 para reproducir en bucle
        except Exception as e:
            print("Error al reproducir el audio de alarma:", e)

    # Crear una ventana emergente (pop up) sin padre para mostrar el GIF
    alarm_window = ctk.CTkToplevel()
    alarm_window.overrideredirect(True)
    alarm_window.title("¡ALARMA!")
    
    # Centrar la ventana en la pantalla
    screen_width = alarm_window.winfo_screenwidth()
    screen_height = alarm_window.winfo_screenheight()
    x = (screen_width - win_width) // 2
    y = (screen_height - win_height) // 2
    alarm_window.geometry(f"{win_width}x{win_height}+{x}+{y}")
    
    # Crear una etiqueta que mostrará el GIF, iniciando con el primer frame
    gif_label = ctk.CTkLabel(alarm_window, image=frames[0], text="")
    gif_label.pack(expand=True, fill="both")
    
    # Función para animar el GIF
    def animate(ind=0):
        gif_label.configure(image=frames[ind])
        ind = (ind + 1) % len(frames)
        alarm_window.after(100, animate, ind)
    
    animate(0)
    
    # Función para cerrar la alarma, detener el audio y la grabación, y destruir la ventana
    def close_alarm(event=None):
        global alarm_active
        alarm_active = False
        try:
            import pygame
            pygame.mixer.music.stop()  # Detener la reproducción del audio
        except Exception as e:
            print("Error al detener el audio de alarma:", e)
        alarm_window.destroy()
    
    # Cerrar la alarma al detectar clic en cualquier parte del pop up
    alarm_window.bind("<Button>", close_alarm)
    # Cerrar el pop up automáticamente después de 30 segundos
    alarm_window.after(30000, close_alarm)

def video_loop():
    global alarm_active
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return

    # Tiempo de inicio para el countdown inicial (30 segundos de estabilización)
    video_start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Realizar la detección en el frame con un umbral de confianza del 0.3
        resultados = model(frame, conf=0.4)
        rendered_frame = resultados[0].plot()
        
        # Después de 30 segundos, revisar si hay detecciones con confianza >= 0.50
        if time.time() - video_start_time >= 1:
            detections = []
            if hasattr(resultados[0], "boxes") and resultados[0].boxes is not None:
                detections = resultados[0].boxes.data.tolist()
            # Se asume que la confianza está en el índice 4
            if not alarm_active and any(det[4] >= 0.5 for det in detections):
                # Agenda la activación de la alarma en el hilo principal
                app.after(0, show_alarm)

        cv2.imshow('Detección de arma - Video', rendered_frame)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

def start_video_thread():
    video_thread = threading.Thread(target=video_loop, daemon=True)
    video_thread.start()

def abrir_imagen():
    top = ctk.CTkToplevel(app)
    top.title("Seleccionar imagen")
    top.geometry("400x200")
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    # Carga de imágenes para los botones
    abrir_image = cargar_imagen("abrir.png", (boton_ancho, boton_alto))
    salir_image = cargar_imagen("salir.png", (boton_ancho, boton_alto))

    # Verifica que las imágenes se hayan cargado correctamente
    if not all([abrir_image, salir_image]):
        print("Error: Una o más imágenes no se pudieron cargar. Verifica las rutas y nombres de archivo.")
        top.destroy()
        return

    image_files = glob.glob(os.path.join(user_media_folder, "*.png")) + \
                  glob.glob(os.path.join(user_media_folder, "*.jpg"))
    if not image_files:
        messagebox.showerror("Error", "No se encontraron imágenes en 'imagenes y grabaciones'.")
        top.destroy()
        return

    selected_image = ctk.StringVar(value=image_files[0])
    option_menu = ctk.CTkOptionMenu(top, values=image_files, variable=selected_image)
    option_menu.pack(pady=20)

    button_frame = ctk.CTkFrame(top)
    button_frame.pack(pady=10)

    def abrir_seleccion():
        ruta_imagen = selected_image.get()
        imagen = cv2.imread(ruta_imagen)
        if imagen is None:
            messagebox.showerror("Error", "No se pudo cargar la imagen seleccionada.")
            return

        resultados = model(imagen, conf=0.3)
        imagen_renderizada = resultados[0].plot()

        cv2.imshow('Detección de arma - Imagen', imagen_renderizada)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        top.destroy()

    # Botón para Abrir
    btn_abrir = ctk.CTkButton(
        button_frame,
        image=abrir_image,
        text="",
        command=abrir_seleccion,
        width=boton_ancho,
        height=boton_alto,
        fg_color=None  # Hace transparente el fondo del botón
    )
    btn_abrir.pack(side="left", padx=10)

    # Botón para Salir
    btn_salir = ctk.CTkButton(
        button_frame,
        image=salir_image,
        text="",
        command=top.destroy,
        width=boton_ancho,
        height=boton_alto,
        fg_color=None
    )
    btn_salir.pack(side="left", padx=10)

def salir_app():
    app.destroy()

# Configuración de la ventana principal
app = ctk.CTk()
app.geometry("600x400")
app.title("SentinelAI")
pywinstyles.apply_style(window=app, style="aero")
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

title_img_path = os.path.join(recursos_folder, "title.png")
img = Image.open(title_img_path)
title_image = ctk.CTkImage(light_image=img, dark_image=img, size=(600, 200))
title_label = ctk.CTkLabel(app, image=title_image, text="")
title_label.pack(side="top", pady=20)

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
    command=start_video_thread,
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
    command=abrir_imagen,
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
    command=salir_app,
    width=boton_ancho,
    height=boton_alto,
    fg_color=None
)
btn_salir.grid(row=0, column=2, padx=10)

app.mainloop()
