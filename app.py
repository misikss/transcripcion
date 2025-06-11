import os
import streamlit as st
from CorteVideos import ProcesadorVideo
from Documento_Convertir import CrearDocumentos, vaciar_documento, vaciar_videos_audios
from transcripcion_mp3 import transcribir_audio_mp3, segmentar_por_temas

def verificar_credenciales():
    cred_path = os.path.abspath("credenciales.json")
    if not os.path.exists(cred_path):
        st.error(f"❌ No se encontró el archivo de credenciales en: {cred_path}")
        st.stop()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path

    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or not os.path.exists(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]):
        st.error("❌ No se pudo establecer la variable de entorno GOOGLE_APPLICATION_CREDENTIALS correctamente.")
        st.stop()
    
    st.success("✅ Credenciales encontradas y variable de entorno establecida correctamente.")
def main_app():
    st.title("Transcripción de Audios MP3 🎵", False)
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

def run_app():
    verificar_credenciales()
    main_app()

if __name__ == '__main__':
    run_app()
