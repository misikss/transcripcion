import os
import streamlit as st
import google.auth
from CorteVideos import ProcesadorVideo
from Documento_Convertir import CrearDocumentos, vaciar_documento, vaciar_videos_audios
from transcripcion_mp3 import transcribir_audio_mp3, segmentar_por_temas
import base64

def verificar_credenciales():
    # Primero intentar usar el archivo local de credenciales
    if os.path.exists("secrets/clave.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/clave.json"
        st.success("✅ Usando credenciales locales desde clave.json")
        return
    
    # Si no hay archivo local, intentar obtener credenciales automáticas (App Engine)
    try:
        import google.auth
        credentials, project_id = google.auth.default()
        st.success(f"✅ Usando credenciales de App Engine (proyecto: {project_id})")
        return  # Si obtenemos las credenciales de App Engine, continuamos
    except Exception as e:
        st.error("❌ No se encontraron credenciales locales ni de App Engine")
        st.error(str(e))
        st.stop()
        
    # Solo llegamos aquí si no hay credenciales locales ni de App Engine
    st.error("❌ No se encontró ninguna credencial válida")
    st.stop()
def main_app():
    st.title("Transcripción de Audios MP3 🎵", False)
    st.write("Esta aplicación permite transcribir archivos .mp3 a texto y segmentar por temas.")
    st.divider()

    st.header("1. Sube tu archivo MP3", False)
    vaciar_videos_audios()
    archivo = st.file_uploader("Sube tu video o audio aqui", accept_multiple_files=False, type=["mp4", "avi", "mov", "mkv", "mp3"])  
    if archivo is not None:
        save_folder = "archivos_subidos"
        os.makedirs(save_folder, exist_ok=True)
        
        # Genera un nombre de archivo dinámico manteniendo la extensión original
        file_extension = os.path.splitext(archivo.name)[1]
        destino = os.path.join(save_folder, f"entrada{file_extension}")
        
        # Elimina el archivo existente si tiene la misma extensión
        if os.path.exists(destino):
            os.remove(destino)
        
        # Guarda el archivo en el disco
        with open(destino, "wb") as f:
            f.write(archivo.getbuffer())
        
        st.success(f"Archivo guardado en: {destino}")
        st.video(destino)
    st.divider()
    
    # Transcribir el video
    st.header("2. Segundo", False)
    st.write("Genera tu transcripcion aqui ✅.")
    if archivo is not None:
        if os.path.exists(destino):
                if st.button("Generar Transcripcion", icon= "📝"):
                    with st.chat_message("ai"):
                        spinner = st.spinner("Generando transcripcion...", show_time=True)
                        with spinner:
                            vaciar_documento()
                            procesador = ProcesadorVideo(destino)
                            procesador.procesar_y_subir()
                            texto = procesador.send_transcripcion_gemini()
                            CrearDocumentos(texto)
                        st.success("Video transcrito con exito! 💪🦁")
                        
                    # Mostrar documentos.
                    tab1, tab2, tab3= st.tabs(["📕 PDF", "📘 WORD", "📄 TEXTO"])

                    tab1.subheader("La transcripcion en formato PDF")
                    tab2.subheader("La transcripcion en formato WORD")
                    tab3.subheader("La transcripcion en formato TEXTO")
                    
                    # Leer el archivo PDF y codificarlo en base64
                    if os.path.exists("Transcripcion.md"):
                        documento_path = "Transcripcion.pdf"
                        with open(documento_path, "rb") as f:
                            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                        # Crear un iframe para mostrar el PDF
                        pdf_mostrar = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                        tab1.markdown(pdf_mostrar, unsafe_allow_html=True)
                    
                        with open("Transcripcion.docx", "rb") as file:
                            contenido = file.read()
                            tab2.download_button(
                                label="Descargar documento Word",
                                data=contenido,
                                file_name="Transcripcion.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        tab3.code(texto)

if __name__ == '__main__':
    verificar_credenciales()
    main_app()
