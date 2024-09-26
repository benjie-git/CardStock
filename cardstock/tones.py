# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2024
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import numpy as np

fade_time = 0.005

# Convert note name to frequency
def note_frequency(note):
    note = note.upper()
    A4_FREQ = 440  # Frequency of A4 in Hz
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    octave = 4
    if note[-1].isdigit():
        octave = int(note[-1])
        note = note[:-1]

    note_index = NOTES.index(note)
    half_steps_from_A4 = note_index - NOTES.index('A') + (octave - 4) * 12
    frequency = A4_FREQ * 2 ** (half_steps_from_A4 / 12)
    return frequency


# get a 1-channel byte stream of 0.25 volume sine wave at the given frequency for duration in seconds
def get_tone_data(frequency, duration):
    volume = 0.25  # range [0.0, 1.0]
    scale = volume * 2**16
    fs = 44100  # sampling rate, Hz, must be integer
    fade_length = int(fs*fade_time)

    # round duration to nearest whole wavelength
    wl = 1.0/frequency
    duration = wl * round(duration/wl)

    # generate samples, note conversion to float32 array
    samples = (np.sin(2 * np.pi * np.arange(fs * duration) * frequency / fs) * scale).astype(np.int16)
    fade_in = np.linspace(0, 1, fade_length)
    fade_out = np.linspace(1, 0, fade_length)
    samples[:fade_length] = samples[:fade_length] * fade_in
    samples[-fade_length:] = samples[-fade_length:] * fade_out

    return samples.tobytes()
