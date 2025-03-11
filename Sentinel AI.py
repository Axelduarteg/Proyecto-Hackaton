import customtkinter as ctk
import pywinstyles
from PIL import Image, ImageSequence
import os 

base_dir = os.pata.dirname(os.path.abspath(__file__))
resources_folder = os.path.join (base_dir, "resources")

user_media_folder = os.path.join (base_dir, "images and recordings")
if not os.path.exists (user_media_folder):
  os.makedirs (user_media_folder)
      
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

app.mainloop()
                      
