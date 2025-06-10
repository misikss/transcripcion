import os
from pdf2docx import parse
from markdown_pdf import MarkdownPdf, Section

def vaciar_videos_audios():
        if os.path.exists("audio_segments/video.mp4_part_1.mp3"):
            print("🗑️ Eliminando archivos videos temporales...")
            os.remove("./archivos_subidos/video.mp4")
            carpeta = "audio_segments"
            num_archivos = len([f for f in os.listdir(carpeta) if os.path.isfile(os.path.join(carpeta, f))])
            for i in range(num_archivos):
                os.remove(f"{carpeta}/video.mp4_part_{i+1}.mp3")
            print("🗑️ Archivos temporales eliminados.")
        else:
            print("🗑️ No hay archivos temporales para videos.")

def vaciar_documento():
    if os.path.exists("Transcripcion.md"):
        print("🗑️ Eliminando archivos temporales...")
        os.remove("Transcripcion.md")
        os.remove("Transcripcion.docx")
        os.remove("Transcripcion.pdf")
    else:
        print("🗑️ No hay documentos temporales para eliminar.")

def CrearDocumentos(texto_md:str):
    with open("Transcripcion.md", "w", encoding="utf-8") as f:
        f.write(texto_md)
    ("✅ MD generado exitosamente.")
    
    # Crear una instancia de MarkdownPdf
    pdf = MarkdownPdf(toc_level=2, optimize=True)

    # Leer el contenido del archivo Markdown
    with open("Transcripcion.md", "r", encoding="utf-8") as f:
        contenido = f.read()

    # Agregar el contenido como una sección al PDF
    pdf.add_section(Section(contenido))

    # Guardar el PDF resultante
    pdf.save("Transcripcion.pdf")
    print("✅ PDF generado exitosamente.")
    
    # Rutas de los archivos
    pdf_file = 'Transcripcion.pdf'
    docx_file = 'Transcripcion.docx'
    
    # Conversión
    parse(pdf_file, docx_file)
    print("✅ DOCX generado exitosamente.")