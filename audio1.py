from pedalboard.io import AudioFile
from pedalboard import *
import noisereduce as nr

def apply_algorithm(audio, sr):
    reduced_noise = nr.reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=0.75)
    return reduced_noise

sr=44100
with AudioFile('audios/audio1.wav').resampled_to(sr) as f:
    audio = f.read(f.frames)

reduced_noise = nr.reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=0.75)

board = Pedalboard([
    NoiseGate(threshold_db=-30, ratio=1.5, release_ms=250), #Reduces audio signal below a certain threshold.
    Compressor(threshold_db=-16, ratio=2.5), #Reduces dynamic range, making quiet sounds louder and loud sounds quieter
    LowShelfFilter(cutoff_frequency_hz=400, gain_db=10, q=1), #Boosts or cuts frequencies below a certain cutoff frequency.
    Gain(gain_db=10) #Adjusts the overall volume of the audio.
])

effected = board(reduced_noise, sr)


with AudioFile('audios/audio1_enhenced.wav', 'w', sr, effected.shape[0]) as f:
  f.write(effected)
