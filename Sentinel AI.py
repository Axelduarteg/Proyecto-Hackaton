import customtkinter as ctk
import pywinstyles
from PIL import Image, ImageSequence
import os 

base_dir = os.pata.dirname(os.path.abspath(__file__))
resources_folder = os.path.join (base_dir, "resources")

app = ctk.CTk()
app.geometry("600x400")
app.title("SentinelAI")
pywinstyles.apply_style(window=app, style="aero")
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")
