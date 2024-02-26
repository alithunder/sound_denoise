from pedalboard.io import AudioFile
from pedalboard import *
import numpy as np
import soundfile as sf
import noisereduce as nr

def apply_algorithm(audio, sr):
    reduced_noise = nr.reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=0.75) #reducing noise
    return reduced_noise

# Load audio file
audio, sr = sf.read('audios/audio4.wav')

# Reduce noise using noisereduce
reduced_noise = nr.reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=0.75)

# Apply Pedalboard effects (adjust parameters as needed)
board = Pedalboard([
    NoiseGate(threshold_db=-30, ratio=1.5, release_ms=250),
    Compressor(threshold_db=-16, ratio=2.5),
    LowShelfFilter(cutoff_frequency_hz=400, gain_db=10, q=1),
    Gain(gain_db=10)
])

effected = board(reduced_noise, sr)

# Write the processed audio to a new file
sf.write('audios/audio4_enhanced.wav', effected, sr)
