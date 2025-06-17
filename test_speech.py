from google.cloud import speech_v1p1beta1 as speech
import os
import google.auth

# Intentar usar primero el archivo local de credenciales
try:
    if os.path.exists("secrets/clave.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/clave.json"
        credentials = speech.SpeechClient.from_service_account_file("secrets/clave.json")
    else:
        # Si no hay archivo local, intentar obtener credenciales automáticas
        credentials, _ = google.auth.default()
    print("✅ Credenciales obtenidas correctamente")
except Exception as e:
    print(f"❌ No se pudieron obtener credenciales: {str(e)}")
    raise

def test_google_speech():
    client = speech.SpeechClient()
    print("✅ Cliente inicializado correctamente")
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="es-ES",
    )
    audio = speech.RecognitionAudio(uri="gs://cloud-samples-data/speech/brooklyn_bridge.raw")
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        print("🎤 Transcripción:", result.alternatives[0].transcript)

test_google_speech()
