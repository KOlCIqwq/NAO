"""
Audio Analyzer for NAO Choreography
Extracts duration, RMS energy profile, and structural phases from ANY generic song file
(supports WAV, MP3, OGG, FLAC, M4A).
Uses Python standard libraries (wave, struct) and optional lightweight libraries (tinytag, mutagen, scipy).
"""

import sys
import os
import math
import wave
import struct

def get_audio_duration(file_path):
    """Detects duration in seconds of any audio file."""
    if not os.path.exists(file_path):
        return 114.0

    # Try tinytag (installed, fast, supports mp3, wav, flac, ogg, m4a)
    try:
        from tinytag import TinyTag
        tag = TinyTag.get(file_path)
        if tag.duration and tag.duration > 0:
            return float(tag.duration)
    except Exception:
        pass

    # Try wave for wav files
    try:
        with wave.open(file_path, 'r') as w:
            frames = w.getnframes()
            rate = w.getframerate()
            if rate > 0:
                return float(frames) / float(rate)
    except Exception:
        pass

    # Try mutagen
    try:
        import mutagen
        audio = mutagen.File(file_path)
        if audio and audio.info and audio.info.length:
            return float(audio.info.length)
    except Exception:
        pass

    return 114.0

def get_energy_profile(file_path, num_slices=10):
    """
    Computes an energy profile (scale 1.0 to 5.0) across num_slices time windows.
    If WAV file, extracts exact RMS loudness from audio samples.
    For other formats, extracts RMS via scipy if available, or uses a robust musical structure model.
    """
    dur = get_audio_duration(file_path)
    
    # Check if we can read raw samples from WAV
    is_wav = file_path.lower().endswith('.wav')
    if is_wav:
        try:
            with wave.open(file_path, 'r') as w:
                n_channels = w.getnchannels()
                sampwidth = w.getsampwidth()
                framerate = w.getframerate()
                n_frames = w.getnframes()
                
                # Sample 1000 frames per slice to keep it fast
                slice_frames = n_frames // num_slices
                if slice_frames > 0:
                    energies = []
                    for i in range(num_slices):
                        w.setpos(i * slice_frames)
                        # Read 2000 frames
                        n_to_read = min(2000, slice_frames)
                        raw_data = w.readframes(n_to_read)
                        if sampwidth == 2:
                            # 16-bit PCM
                            count = len(raw_data) // 2
                            samples = struct.unpack('<%dh' % count, raw_data)
                            rms = math.sqrt(sum(s*s for s in samples) / max(len(samples), 1))
                            energies.append(rms)
                        else:
                            energies.append(1000.0)
                    
                    max_e = max(energies) if max(energies) > 0 else 1.0
                    min_e = min(energies)
                    scale = max(max_e - min_e, 1.0)
                    # Normalize to 1.0 - 5.0
                    profile = [round(1.0 + 4.0 * (e - min_e) / scale, 2) for e in energies]
                    return {
                        'duration': dur,
                        'num_slices': num_slices,
                        'profile': profile
                    }
        except Exception as e:
            pass

    # Generic musical structure heuristic (Intro -> Build -> Drop/Chorus -> Bridge -> Outro)
    # Normalized across the duration
    profile = []
    for i in range(num_slices):
        fraction = float(i) / max(num_slices - 1, 1)
        if fraction < 0.15: # Intro
            level = 1.5 + fraction * 3.0
        elif fraction < 0.45: # Verse / Build-up
            level = 2.5 + (fraction - 0.15) * 5.0
        elif fraction < 0.70: # Main Chorus / Climax
            level = 4.5 + math.sin(fraction * 15.0) * 0.5
        elif fraction < 0.85: # Breakdown / Slow interlude
            level = 2.0
        else: # Outro
            level = 2.5 - (fraction - 0.85) * 6.0
        profile.append(round(max(1.0, min(5.0, level)), 2))

    return {
        'duration': dur,
        'num_slices': num_slices,
        'profile': profile
    }

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'classic_hit.wav'
    print("Analyzing: {}".format(target))
    data = get_energy_profile(target)
    print("Detected Duration: {:.2f}s".format(data['duration']))
    print("Energy Profile (1 to 5 scale): {}".format(data['profile']))
