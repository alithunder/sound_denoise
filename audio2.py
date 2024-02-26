from pedalboard.io import AudioFile
from pedalboard import *
import numpy as np
import soundfile as sf
import noisereduce as nr

def apply_algorithm(audio, sr):
    echo_decay = 0.8
    echo_suppressed = audio.copy()
    for i in range(1, len(audio)):
        echo_suppressed[i] = audio[i] + audio[i - 1] * echo_decay
    reduced_noise = nr.reduce_noise(y=echo_suppressed, sr=sr, stationary=True, prop_decrease=0.75)
    return reduced_noise

sr = 44100
with AudioFile('audios/audio2.wav').resampled_to(sr) as f:
    audio = f.read(f.frames)

# Reduce noise
reduced_noise = nr.reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=0.75)

# Apply echo suppression algorithm with increased decay
echo_decay = 0.8  # Adjust the echo decay factor as needed
echo_suppressed = reduced_noise.copy()
for i in range(1, len(reduced_noise)):
    echo_suppressed[i] = reduced_noise[i] + reduced_noise[i - 1] * echo_decay

# Apply pedalboard effects
board = Pedalboard([
    NoiseGate(threshold_db=-30, ratio=1.5, release_ms=250),
    Compressor(threshold_db=-16, ratio=2.5),
    LowShelfFilter(cutoff_frequency_hz=400, gain_db=10, q=1),
    Gain(gain_db=10)
])

effected = board(echo_suppressed, sr)

# Write the processed audio to a new file
with AudioFile('audios/audio2_enhanced.wav', 'w', sr, effected.shape[0]) as f:
    f.write(effected)
