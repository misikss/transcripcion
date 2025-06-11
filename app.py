import os
import base64
import streamlit as st
from CorteVideos import ProcesadorVideo
from Documento_Convertir import CrearDocumentos, vaciar_documento, vaciar_videos_audios
import io
from transcripcion_mp3 import transcribir_audio_mp3, segmentar_por_temas

def __main__():
    st.title("Transcripcion de Audios MP3 🎵", False)
    st.write("Esta aplicación permite transcribir archivos .mp3 a texto y segmentar por temas.")
    st.divider()
    
    st.header("1. Sube tu archivo MP3", False)
    vaciar_videos_audios()
    archivo = st.file_uploader("Arrastra o selecciona tu archivo .mp3", accept_multiple_files=False, type=["mp3"])  
    if archivo is not None:
        save_folder = "archivos_subidos"
        os.makedirs(save_folder, exist_ok=True)
        save_path = os.path.join(save_folder, archivo.name)
        with open(save_path, "wb") as f:
            f.write(archivo.getbuffer())
        destino = save_path
        st.success(f"Archivo guardado en: {destino}")
        st.audio(destino)
        st.divider()
        st.header("2. Transcripción y segmentación temática", False)
        with st.spinner("Transcribiendo y segmentando el audio..."):
            texto, timestamps = transcribir_audio_mp3(destino)
            secciones = segmentar_por_temas(texto)
        st.subheader("Transcripción completa con timestamps")
        st.code(timestamps)
        st.subheader("Segmentación temática")
        for idx, (tema, contenido) in enumerate(secciones.items(), 1):
            st.markdown(f"### Tema {idx}: {tema}")
            st.write(contenido)

if '__main__' == __name__:
    __main__()