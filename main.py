import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pedalboard.io import AudioFile
from pedalboard import *
import os
from pydub import AudioSegment
from pydub.playback import play
import threading
import pyaudio
import wave
import numpy as np
from audio1 import apply_algorithm as apply_algorithm_1
from audio2 import apply_algorithm as apply_algorithm_2
from crowd import apply_algorithm as apply_algorithm_3
from crowd2 import apply_algorithm as apply_algorithm_4

# Initialize PyAudio
audio = pyaudio.PyAudio()

def start_stop_recording():
    global is_recording, frames
    if not is_recording:
        is_recording = True
        frames = []
        recording_button.config(text="Stop Recording", command=stop_recording)
        threading.Thread(target=record_audio).start()
    else:
        is_recording = False

def record_audio():
    global frames
    while is_recording:
        if stream.is_stopped():
            break
        data = stream.read(1024)
        frames.append(data)

    # Reset the recording button after stopping recording
    recording_button.config(text="Start Recording", command=start_stop_recording)

def stop_recording():
    global frames, selected_file_path
    stream.stop_stream()
    stream.close()
    audio.terminate()

    sound_file = wave.open("my.wav" , "wb")
    sound_file.setnchannels(1)
    sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    sound_file.setframerate(44100)
    sound_file.writeframes(b''.join(frames))
    sound_file.close()

    selected_file_path = "my.wav"
    frames = []

    # Reset the recording button after stopping recording
    recording_button.config(text="Start Recording", command=start_stop_recording)

def save_denoised():
    algo_num = algo_choice.current() + 1
    if selected_file_path and selected_output_folder:
        file_name = file_name_entry.get()
        if not file_name:
            messagebox.showerror("Error", "Please enter a file name.")
            return
        output_file = os.path.join(selected_output_folder, f"{file_name}_denoised_{algo_num}.wav")
        process_audio(selected_file_path, algo_num, output_file)

def play_denoised():
    def _apply_denoise():
        algo_num = algo_choice.current() + 1
        if selected_file_path:
            audio = AudioSegment.from_file(selected_file_path)
            sr = audio.frame_rate
            algo_function = None
            if algo_num == 1:
                algo_function = apply_algorithm_1
            elif algo_num == 2:
                algo_function = apply_algorithm_2
            elif algo_num == 3:
                algo_function = apply_algorithm_3
            elif algo_num == 4:
                algo_function = apply_algorithm_4

            if algo_function:
                try:
                    samples = np.array(audio.get_array_of_samples())
                    reduced_noise = algo_function(samples, sr)
                    denoised_audio = AudioSegment(
                        reduced_noise.tobytes(), 
                        frame_rate=sr, 
                        sample_width=audio.sample_width, 
                        channels=audio.channels
                    )
                    play(denoised_audio)
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    thread = threading.Thread(target=_apply_denoise)
    thread.start()

def play_original():
    def _play():
        if selected_file_path:
            audio = AudioSegment.from_file(selected_file_path)
            play(audio)

    thread = threading.Thread(target=_play)
    thread.start()

def process_audio(file_path, algo_num, output_file):
    sr = 44100
    with AudioFile(file_path).resampled_to(sr) as f:
        audio = f.read(f.frames)

    algo_function = None
    if algo_num == 1:
        algo_function = apply_algorithm_1
    elif algo_num == 2:
        algo_function = apply_algorithm_2
    elif algo_num == 3:
        algo_function = apply_algorithm_3
    elif algo_num == 4:
        algo_function = apply_algorithm_4

    if algo_function:
        try:
            # Call the apply_algorithm function from the respective algorithm file
            reduced_noise = algo_function(audio, sr)

            board = Pedalboard([
                NoiseGate(threshold_db=-30, ratio=1.5, release_ms=250),
                Compressor(threshold_db=-16, ratio=2.5),
                LowShelfFilter(cutoff_frequency_hz=400, gain_db=10, q=1),
                Gain(gain_db=10)
            ])

            effected = board(reduced_noise, sr)

            with AudioFile(output_file, 'w', sr, effected.shape[0]) as f:
                f.write(effected)
            messagebox.showinfo("Success", "Audio enhanced and saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def select_output_folder():
    global selected_output_folder
    selected_output_folder = filedialog.askdirectory()
    if not selected_output_folder:
        messagebox.showerror("Error", "No output folder selected.")

def save_file():
    algo_num = algo_choice.current() + 1
    if selected_file_path and selected_output_folder:
        file_name = file_name_entry.get()
        if not file_name:
            messagebox.showerror("Error", "Please enter a file name.")
            return
        output_file = os.path.join(selected_output_folder, f"{file_name}.wav")
        process_audio(selected_file_path, algo_num, output_file)

def select_file():
    global selected_file_path
    selected_file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if not selected_file_path:
        messagebox.showerror("Error", "No file selected.")

root = tk.Tk() #creates the main window for the GUI application. 
root.title("Audio Enhancement")

style = ttk.Style() #configure the styles for the widgets in the GUI
style.configure('TButton', font=('Helvetica', 12))
style.configure('TLabel', font=('Helvetica', 12))

mainframe = ttk.Frame(root, padding="30 15") #contain the main elements of the GUI
mainframe.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

algo_label = ttk.Label(mainframe, text="Select Algorithm:")
algo_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

algo_choice = ttk.Combobox(mainframe, values=["Noisy sound", "Echo", "Crowd", "Crowd 2"], state="readonly")
algo_choice.current(0)
algo_choice.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

file_button = ttk.Button(mainframe, text="Select File", command=select_file)
file_button.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

output_button = ttk.Button(mainframe, text="Select Output Folder", command=select_output_folder)
output_button.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

file_name_label = ttk.Label(mainframe, text="Enter File Name:")
file_name_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

file_name_entry = ttk.Entry(mainframe)
file_name_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

save_button = ttk.Button(mainframe, text="Save", command=save_file)
save_button.grid(row=3, column=0, columnspan=2, pady=10)
play_original_button = ttk.Button(mainframe, text="Play Original", command=play_original)
play_original_button.grid(row=3, column=0, columnspan=2, pady=10)

play_denoised_button = ttk.Button(mainframe, text="Play Denoised", command=play_denoised)
play_denoised_button.grid(row=4, column=0, columnspan=2, pady=10)

save_denoised_button = ttk.Button(mainframe, text="Save Denoised", command=save_denoised)
save_denoised_button.grid(row=5, column=0, columnspan=2, pady=10)

recording_button = ttk.Button(mainframe, text="Start Recording", command=start_stop_recording)
recording_button.grid(row=6, column=0, columnspan=2, pady=10)

# Variables
is_recording = False
frames = []
selected_file_path = None
selected_output_folder = None

# PyAudio stream for recording
stream = audio.open(format=pyaudio.paInt16 , channels=1 , rate=44100 , input=True , frames_per_buffer=1024)

root.mainloop()
