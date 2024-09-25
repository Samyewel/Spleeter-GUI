import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import subprocess
import threading
import json
import importlib

SETTINGS_FILE = "settings.json"
LOG_FILE = "error_log.txt"
sys.stdout = open(LOG_FILE, "w")
sys.stderr = open(LOG_FILE, "w")

# load_settings:
# - Locates the settings file within the execution directory and loads them.
def load_settings():
	if os.path.exists(SETTINGS_FILE):
		with open(SETTINGS_FILE, 'r') as f:
			settings = json.load(f)
			return settings.get("output_folder", "")
	return ""

# save_settings:
# -
def save_settings(output_folder_path):
	with open(SETTINGS_FILE, 'w') as f:
		json.dump({"output_folder": output_folder_path}, f)

def run_spleeter():
	audio_file_path = entry_audio_file_path.get()
	output_folder_path = entry_output_folder_path.get()
	if not validate_inputs(audio_file_path, output_folder_path):
		return
	codec = output_format_var.get()
	command = build_command(audio_file_path, codec, output_folder_path)
	button_run.config(text="Splitting...", state=tk.DISABLED)
	run_conversion(command)

def validate_inputs(audio_file_path, output_folder_path):
	if not audio_file_path:
		messagebox.showerror("Error", "Please select an audio file.")
		return False
	if not os.path.isfile(audio_file_path):
		messagebox.showerror("Error", "The specified file does not exist.")
		return False
	if not output_folder_path:
		messagebox.showerror("Error", "Please select an output folder.")
		return False
	stem_count = stem_count_var.get()

	return True

def build_command(audio_file_path, codec, output_folder):
	stem_count = stem_count_var.get()
	codec_format = {
		'wav': 'wav', 'mp3': 'mp3', 'ogg': 'ogg',
		'm4a': 'm4a', 'wma': 'wma', 'flac': 'flac'
	}.get(codec, 'wav')
	command = [
		"spleeter", "separate", audio_file_path, "-p",
		f"spleeter:{stem_count}stems-16kHz", "-o",
		output_folder, "-c", codec_format,
		"-f", "{filename}/{filename}_{instrument}.{codec}"
	]
	if codec == 'mp3':
		command.extend(["-b", bitrate_var.get()])
	print(f"Running Spleeter command:\n{command}")
	return command

def run_conversion(command):
	def run_command():
		try:
			subprocess.run(command, check=True)
			messagebox.showinfo("Info", "Conversion completed successfully.")
		except subprocess.CalledProcessError:
			messagebox.showerror("Error", "An error occurred with Spleeter.")
		finally:
			button_run.config(text="Run Spleeter", state=tk.NORMAL)
			toggle_widgets_state(tk.NORMAL)
	toggle_widgets_state(tk.DISABLED)
	threading.Thread(target=run_command).start()

def browse_file():
	file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
	entry_audio_file_path.delete(0, tk.END)
	entry_audio_file_path.insert(0, file_path)

def browse_output_folder():
	folder_path = filedialog.askdirectory()
	entry_output_folder_path.delete(0, tk.END)
	entry_output_folder_path.insert(0, folder_path)

def update_bitrate_dropdown(*args):
	bitrate_menu.config(state=tk.NORMAL if output_format_var.get() == 'mp3' else tk.DISABLED)

def toggle_widgets_state(state):
	button_browse_audio.config(state=state)
	button_browse_output.config(state=state)
	button_run.config(state=state)
	output_format_menu.config(state=state)
	stem_count_menu.config(state=state)
	bitrate_menu.config(state=state)

def on_closing():
	output_folder_path = entry_output_folder_path.get()
	save_settings(output_folder_path)
	root.destroy()

def on_enter(event):
	event.widget.config(bg=BUTTON_HOVER_BG_COLOR, fg=BUTTON_HOVER_FG_COLOR)

def on_leave(event):
	event.widget.config(bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)

# Define color variables
BACKGROUND_COLOR = 'white'
FRAME_COLOR = 'white'
LABEL_COLOR = 'white'
TEXT_COLOR = 'black'
BUTTON_BG_COLOR = 'white'
BUTTON_FG_COLOR = 'black'
BUTTON_HOVER_BG_COLOR = 'whitesmoke'
BUTTON_HOVER_FG_COLOR = 'black'
RUN_BUTTON_COLOR = 'white'
BITRATE_COLOR = 'white'

script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "images", "spleeterlogo.png")

# Print debug information
print(f"Running Python version: \n{sys.version}")
print(f"Script directory: \n{script_dir}")
print(f"Logo path: \n{logo_path}")

root = tk.Tk()
root.title("Spleeter")
root.geometry("600x350")
root.resizable(False, False)
root.configure(bg=BACKGROUND_COLOR)

image_frame = tk.Frame(root, bg=FRAME_COLOR)
image_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

try:
	logo = Image.open(logo_path)
	logo = logo.resize((200,100), Image.LANCZOS)
	photo = ImageTk.PhotoImage(logo)
	# Keep reference to image
	image_label = tk.Label(image_frame, image=photo, bg=FRAME_COLOR)
	image_label.image = photo
	image_label.pack()
except FileNotFoundError:
	print(f"Spleeter logo not found at {logo_path}")

# Loads the saved output folder from settings.json
last_output_folder = load_settings()

# Audio File Path
tk.Label(root, text="Audio File Path:", bg=LABEL_COLOR, fg=TEXT_COLOR).grid(row=1, column=0, sticky="nsew")
entry_audio_file_path = tk.Entry(root, width=50, bg='white')
entry_audio_file_path.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
button_browse_audio = tk.Button(root, text="Browse", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, command=browse_file)
button_browse_audio.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
button_browse_audio.bind("<Enter>", on_enter)
button_browse_audio.bind("<Leave>", on_leave)

# Output Folder Path
tk.Label(root, text="Output Folder Path:", bg=LABEL_COLOR, fg=TEXT_COLOR).grid(row=2, column=0, sticky="nsew")
entry_output_folder_path = tk.Entry(root, width=50, bg='white')
entry_output_folder_path.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
entry_output_folder_path.insert(0, load_settings())
button_browse_output = tk.Button(root, text="Browse", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, command=browse_output_folder)
button_browse_output.grid(row=2, column=2, padx=5, pady=5, sticky="nsew")
button_browse_output.bind("<Enter>", on_enter)
button_browse_output.bind("<Leave>", on_leave)

# Stem Count
tk.Label(root, text="Stem Count:", bg=LABEL_COLOR, fg=TEXT_COLOR).grid(row=3, column=0, sticky="nsew")
stem_count_var = tk.StringVar(value='2')
stem_count_menu = tk.OptionMenu(root, stem_count_var, '2', '4', '5')
stem_count_menu.config(bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
stem_count_menu.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

# Output Format
tk.Label(root, text="Output Format:", bg=LABEL_COLOR, fg=TEXT_COLOR).grid(row=4, column=0, sticky="nsew")
output_format_var = tk.StringVar(value='wav')
output_format_menu = tk.OptionMenu(root, output_format_var, 'wav', 'mp3', 'ogg', 'm4a', 'wma', 'flac')
output_format_menu.config(bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
output_format_menu.grid(row=4, column=1, padx=5, pady=5, sticky="nsew")
output_format_var.trace_add("write", update_bitrate_dropdown)

# Bitrate for MP3
tk.Label(root, text="Bitrate (mp3):", bg=LABEL_COLOR, fg=TEXT_COLOR).grid(row=5, column=0, sticky="nsew")
bitrate_var = tk.StringVar(value="128k")
bitrate_menu = tk.OptionMenu(root, bitrate_var, "128k", "192k", "256k", "320k")
bitrate_menu.grid(row=5, column=1, padx=5, pady=5, sticky="nsew")
bitrate_menu.config(bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
bitrate_menu.config(state=tk.DISABLED)

# Run Button
button_run = tk.Button(root, text="Run Spleeter", bg=BUTTON_BG_COLOR, fg=TEXT_COLOR, command=run_spleeter)
button_run.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
button_run.bind("<Enter>", on_enter)
button_run.bind("<Leave>", on_leave)

# Configure grid to be expandable
for i in range(7):
	root.grid_rowconfigure(i, weight=1)
for i in range(3):
	root.grid_columnconfigure(i, weight=1)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()