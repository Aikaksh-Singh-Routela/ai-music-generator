import streamlit as st
import numpy as np
import io
import base64
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="AI Music Generator",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 AI Music Generator")
st.markdown("*Generate simple melodies using AI-powered sound synthesis*")

# ============================================
# SIDEBAR: PARAMETERS
# ============================================
with st.sidebar:
    st.header("🎛️ Parameters")
    
    # Music parameters
    duration = st.slider("Duration (seconds)", 1, 10, 3)
    tempo = st.slider("Tempo (BPM)", 60, 180, 120)
    scale = st.selectbox(
        "Scale",
        ["C Major", "G Major", "A Minor", "E Minor", "Pentatonic"]
    )
    
    st.markdown("---")
    st.markdown("### 🎹 Notes")
    num_notes = st.slider("Number of Notes", 5, 30, 16)
    note_length = st.slider("Note Length (seconds)", 0.1, 0.5, 0.2)
    
    st.markdown("---")
    st.markdown("### 🔊 Effects")
    add_reverb = st.checkbox("Add Reverb", value=True)
    add_echo = st.checkbox("Add Echo", value=False)

# ============================================
# MUSIC GENERATION FUNCTIONS
# ============================================
def note_to_frequency(note_name):
    """Convert note name to frequency in Hz"""
    note_map = {
        'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
        'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
        'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
    }
    return note_map.get(note_name, 440.0)

def generate_scale(root_note, scale_type):
    """Generate a scale based on root note and scale type"""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Scale patterns (intervals in semitones)
    patterns = {
        'C Major': [0, 2, 4, 5, 7, 9, 11, 12],
        'G Major': [0, 2, 4, 5, 7, 9, 11, 12],
        'A Minor': [0, 2, 3, 5, 7, 8, 10, 12],
        'E Minor': [0, 2, 3, 5, 7, 8, 10, 12],
        'Pentatonic': [0, 2, 4, 7, 9]
    }
    
    intervals = patterns.get(scale_type, patterns['C Major'])
    root_index = notes.index(root_note)
    
    scale_notes = []
    for interval in intervals:
        note_index = (root_index + interval) % 12
        scale_notes.append(notes[note_index])
    
    return scale_notes

def generate_melody(scale_notes, num_notes, note_length, sample_rate=44100):
    """Generate a melody from a scale"""
    melody = np.array([])
    
    for i in range(num_notes):
        # Pick a random note from the scale
        note = np.random.choice(scale_notes)
        frequency = note_to_frequency(note)
        
        # Generate a single note
        t = np.linspace(0, note_length, int(sample_rate * note_length))
        note_wave = np.sin(2 * np.pi * frequency * t)
        
        # Add some variation to amplitude
        envelope = np.exp(-2 * t / note_length)  # Simple decay
        note_wave = note_wave * envelope
        
        melody = np.append(melody, note_wave)
    
    return melody

def add_reverb(signal, sample_rate, reverb_amount=0.3):
    """Simple reverb effect"""
    delay_samples = int(0.1 * sample_rate)  # 100ms delay
    reverb_signal = np.copy(signal)
    
    # Add delayed and attenuated copies
    for i in range(1, 4):
        delay = delay_samples * i
        if delay < len(signal):
            reverb_signal[delay:] += signal[:-delay] * (reverb_amount ** i)
    
    return reverb_signal

def add_echo(signal, sample_rate, echo_amount=0.5):
    """Simple echo effect"""
    delay_samples = int(0.3 * sample_rate)  # 300ms delay
    echo_signal = np.copy(signal)
    
    if delay_samples < len(signal):
        echo_signal[delay_samples:] += signal[:-delay_samples] * echo_amount
    
    return echo_signal

# ============================================
# GENERATE MUSIC
# ============================================
if st.button("🎶 Generate Music"):
    with st.spinner("Generating your melody..."):
        
        # Get root note from scale
        root_map = {
            'C Major': 'C', 'G Major': 'G',
            'A Minor': 'A', 'E Minor': 'E',
            'Pentatonic': 'C'
        }
        root_note = root_map.get(scale, 'C')
        
        # Generate scale and melody
        scale_notes = generate_scale(root_note, scale)
        sample_rate = 44100
        melody = generate_melody(scale_notes, num_notes, note_length, sample_rate)
        
        # Apply effects
        if add_reverb:
            melody = add_reverb(melody, sample_rate)
        if add_echo:
            melody = add_echo(melody, sample_rate)
        
        # Normalize to 16-bit
        melody = melody / np.max(np.abs(melody))
        melody_int16 = (melody * 32767).astype(np.int16)
        
        # Create WAV file
        wav_buffer = io.BytesIO()
        write(wav_buffer, sample_rate, melody_int16)
        wav_buffer.seek(0)
        
        # Display audio player
        st.audio(wav_buffer, format='audio/wav')
        
        # Download button
        st.download_button(
            "⬇️ Download WAV",
            wav_buffer,
            file_name="generated_melody.wav",
            mime="audio/wav"
        )
        
        # Show waveform
        st.markdown("### 📊 Waveform")
        fig, ax = plt.subplots(figsize=(10, 2))
        time_axis = np.linspace(0, len(melody) / sample_rate, min(len(melody), 10000))
        ax.plot(time_axis, melody[:len(time_axis)])
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Amplitude")
        ax.set_title("Waveform of Generated Melody")
        st.pyplot(fig)
        
        # Show melody info
        st.markdown("### 🎼 Melody Info")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Scale", scale)
        with col2:
            st.metric("Notes", num_notes)
        with col3:
            st.metric("Duration", f"{len(melody)/sample_rate:.1f}s")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption("🎵 AI Music Generator - Create simple melodies with AI-powered sound synthesis")