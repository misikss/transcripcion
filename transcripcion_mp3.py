import os
from google.cloud import speech_v1p1beta1 as speech
import io
from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI

def transcribir_audio_mp3(ruta_mp3):
    """
    Transcribe un archivo mp3 usando Google Speech-to-Text y devuelve el texto y los timestamps.
    """
    load_dotenv()
    client = speech.SpeechClient()
    with io.open(ruta_mp3, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=44100,
        language_code="es-ES",
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
        model="default"
    )
    response = client.recognize(config=config, audio=audio)
    texto = ""
    timestamps = ""
    for result in response.results:
        alternative = result.alternatives[0]
        texto += alternative.transcript + "\n"
        for word_info in alternative.words:
            start = word_info.start_time
            segundos = int(start.seconds)
            minutos = segundos // 60
            horas = minutos // 60
            tiempo = f"[{horas:02}:{minutos%60:02}:{segundos%60:02}]"
            timestamps += f"{tiempo} {word_info.word} "
        timestamps += "\n"
    return texto.strip(), timestamps.strip()

def segmentar_por_temas(texto):
    """
    Usa un modelo de lenguaje para segmentar el texto por temas detectados.
    Devuelve un diccionario {tema: contenido}
    """
    prompt = f"""
    Analiza el siguiente texto transcrito de un audio y segmenta el contenido en secciones temáticas. Para cada tema detectado, proporciona un título breve y el texto correspondiente. Devuelve el resultado como un diccionario Python, donde la clave es el nombre del tema y el valor es el texto de esa sección. Texto:\n{texto}\n"""
    model = ChatVertexAI(model_name="gemini-2.5-pro-preview-05-06", temperature=0.3)
    response = model.invoke(prompt)
    # Intentar evaluar la respuesta como dict
    try:
        import ast
        secciones = ast.literal_eval(response.content)
        if isinstance(secciones, dict):
            return secciones
    except Exception:
        # Si no es un dict, devolver todo como un solo tema
        return {"Transcripción completa": texto}
    return {"Transcripción completa": texto}
