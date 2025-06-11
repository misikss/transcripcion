import os
import base64
import streamlit as st
from CorteVideos import ProcesadorVideo
from Documento_Convertir import CrearDocumentos, vaciar_documento, vaciar_videos_audios

def __main__():
    st.title("Transcripcion de Videos 📼", False)
    st.write("Esta aplicación permite transcribir videos a texto.")
    st.divider()
    
    # Subir el archivo de video
    st.header("1. Primero", False)
    vaciar_videos_audios()
    archivo = st.file_uploader("Sube tu video aqui", accept_multiple_files=False, type=["mp4", "avi", "mov", "mkv"])  
    if archivo is not None:
        # Especifica la carpeta donde deseas guardar el archivo
        save_folder = "archivos_subidos"
        os.makedirs(save_folder, exist_ok=True)
        save_path = os.path.join(save_folder, archivo.name)
        # Guarda el archivo en el disco
        with open(save_path, "wb") as f:
            f.write(archivo.getbuffer())
        destino = "archivos_subidos/video.mp4"
        if os.path.exists(destino):
            os.remove(destino)
        os.rename(save_path, destino)
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

if '__main__' == __name__:
    __main__()