import streamlit as st
import librosa
import numpy as np
from pydub import AudioSegment
import openai  # Para generar letras
from elevenlabs import generate, set_api_key  # Para voz (instala elevenlabs)

# Configura APIs (reemplaza con tus claves)
openai.api_key = "tu_clave_openai"
set_api_key("tu_clave_elevenlabs")

def generar_letra(prompt, estructura="versos, coro, puente"):
    # Usa OpenAI para generar letra basada en prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Eres un letrista profesional. Crea una letra en español con estructura: {estructura}. Tema: {prompt}. Hazla emocional y catchy."}
        ]
    )
    return response['choices'][0]['message']['content']

def crear_base_instrumental(genero, sample_real=None):
    # Genera base simple o remixe sample
    if sample_real:
        # Carga sample real (ej. descarga de URL o archivo local)
        y, sr = librosa.load(sample_real)  # Asume archivo WAV/MP3
        # Remixe: cambia tempo, añade efectos
        y_remixed = librosa.effects.time_stretch(y, rate=1.1)  # Ejemplo: acelera
        librosa.output.write_wav("base.wav", y_remixed, sr)
    else:
        # Genera base desde cero (beats simples)
        duration = 180  # 3 minutos
        sr = 22050
        t = np.linspace(0, duration, int(sr * duration))
        # Beat básico: kick y snare
        kick = np.sin(2 * np.pi * 60 * t) * np.exp(-t / 2)  # Frecuencia baja
        snare = np.random.randn(len(t)) * 0.1  # Ruido para snare
        base = kick + snare
        librosa.output.write_wav("base.wav", base, sr)
    return "base.wav"

def sintetizar_voz(letra, intencion):
    # Sintetiza voz con emoción
    voice_id = "bella" if intencion == "feliz" else "adam"  # Elige voz basada en intención
    audio = generate(text=letra, voice=voice_id, model="eleven_monolingual_v1")
    with open("voz.wav", "wb") as f:
        f.write(audio)
    return "voz.wav"

def mezclar_y_masterizar(base_file, voz_file):
    # Mezcla usando pydub
    base = AudioSegment.from_wav(base_file)
    voz = AudioSegment.from_wav(voza_file)
    voz = voz - 10  # Baja volumen de voz
    mezclada = base.overlay(voz)
    mezclada.export("cancion_final.mp3", format="mp3")
    return "cancion_final.mp3"

# Interfaz Streamlit
st.title("SongCreator AI")
prompt = st.text_input("Describe tu canción (ej. 'pop sobre amor perdido')")
genero = st.selectbox("Género", ["pop", "reggaeton", "rock"])
intencion = st.selectbox("Intención emocional", ["feliz", "triste", "motivacional"])
usar_sample = st.checkbox("Usar canción real como base?")
sample_url = st.text_input("URL del sample (si aplica)") if usar_sample else None

if st.button("Crear Canción"):
    # Paso 1: Generar letra
    letra = generar_letra(prompt)
    st.write("Letra generada:", letra)
    
    # Paso 2: Crear base
    base_file = crear_base_instrumental(genero, sample_url if usar_sample else None)
    st.audio(base_file, format="audio/wav")
    
    # Paso 3: Sintetizar voz
    voz_file = sintetizar_voz(letra, intencion)
    st.audio(voz_file, format="audio/wav")
    
    # Paso 4: Mezclar
    final_file = mezclar_y_masterizar(base_file, voz_file)
    st.audio(final_file, format="audio/mp3")
    
    # Descargas
    st.download_button("Descargar Letra", letra, file_name="letra.txt")
    st.download_button("Descargar Base", base_file, file_name="base.wav")
    st.download_button("Descargar Voz", voz_file, file_name="voz.wav")
    st.download_button("Descargar Canción Final", final_file, file_name="cancion.mp3")
