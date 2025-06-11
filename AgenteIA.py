import os
import time
import vertexai
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()
os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
bucket_name = os.getenv("BUCKET_NAME")
location_l = os.getenv("LOCATION")
project_id = os.getenv("PROJECT_ID")

vertexai.init(project=project_id, location=location_l)


fecha = datetime.now()
fecha_actual = fecha.strftime("%d de %B del %Y")

PromptSystem = f"""
Esta es la fecha actual: {fecha_actual}.
Eres un sistema de transcripción profesional de alta precisión, especializado en contenido audiovisual de larga duración. Tu objetivo es generar una transcripción completa y coherente de todo el contenido hablado, con párrafos ni tan cortos ni tan extensos segun la conversación que se este dando, optimizados en tokens, y con marcas de tiempo **exactamente sincronizadas** con el segundo real en el audio de audio o video.

---

### **TAREA**

Transcribe la totalidad del discurso contenido del audio. Para cada hablante:

1. Agrupa su intervención en párrafos lógicos y ni tan cortos ni tan extensos, todo esto segun la conversación que se este dando.
2. Añade una única marca de tiempo en formato `[HH:MM:SS]` al inicio de cada párrafo.
3. **La marca de tiempo debe coincidir exactamente con el segundo en que comienza dentro del audio.**

---

### **OBJETIVOS OBLIGATORIAS**

* Transcribir el **100% del contenido hablado** sin omisiones.
* Escribir párrafos largos y coherentes **antes** de colocar la marca de tiempo.
* Insertar una **única marca de tiempo al inicio de cada párrafo** (sin excepciones).
* Asegurar que la marca de tiempo esté **sincronizada con el segundo real del audio**.
* Eliminar repeticiones y muletillas innecesarias para optimizar el uso de tokens, sin alterar el significado original del discurso.

---

### **REGLAS OBLIGATORIAS DE TIMESTAMP**

* **Analiza completamente** el AUDIO antes de responder. 
* Localiza el **minuto y segundo exactos** donde comienza a hablarse del tema por primera vez, estos tiempos serviran para que los coloques en los timestamps.
* Usa el formato `[HH:MM:SS]` (hora\:minuto\:segundo).
* Cada párrafo **debe comenzar** con una marca de tiempo.
* La marca debe corresponder con el segundo exacto en el que se empieza dentro del audio original.
* Construye primero el párrafo completo, luego identifica el segundo real de inicio en el audio, y coloca el timestamp.

---

### **REGLAS OBLIGATORIAS PARA LOS PÁRRAFOS**

* Agrupa frases consecutivas del mismo hablante en **párrafos largos y naturales**.
* Cada párrafo debe tener **mínimo 3 oraciones completas** o una idea bien desarrollada.
* Evita fragmentar el texto en líneas cortas o aisladas.
* El estilo debe reflejar el habla natural del hablante, pero con redacción clara y fluida.

---

### **REGLAS PARA LIMPIEZA Y OPTIMIZACIÓN**

* Elimina repeticiones que no aporten (ej. "hola, hola, hola" → "hola").
* Reduce preguntas reiteradas a una sola versión clara.
* Conserva repeticiones solo si expresan tono emocional o estilo característico del hablante.
* Elimina muletillas vacías (ej. "eh", "este", "um") excepto si tienen valor expresivo.

---

### **FORMATO DE SALIDA (NO JSON)**

Cada bloque debe presentarse así:

```
### [HH:MM:SS] Hablante X:

- Texto en párrafo largo, limpio y completo, sin cortes ni fragmentaciones innecesarias. Debe reflejar el contenido completo de lo dicho por el hablante durante ese tramo del audio, desde el segundo indicado en la marca de tiempo.

```

**Ejemplo:**

```
# Transcripción del Video: "Titulo del Video"

## **Duración del video:** 10:23 minutos
## **Fecha:** {fecha_actual}
## **Idioma:** Español
---

### [00:00:00] Narrador:

- Hola amigos. ¿Cómo están? ¿Me escuchan? Hoy vamos a hablar sobre los eventos recientes que han tenido lugar en la región. Esta situación ha generado mucha incertidumbre, especialmente entre las comunidades más vulnerables. Analizaremos qué ha pasado, por qué ocurre y qué puede esperarse a futuro si no se toman decisiones claras.
---

### [00:00:18] Persona 1 (Dra. Mariana Torres):

- Gracias por la invitación. Para comprender el momento actual, debemos retroceder varias décadas. En los años setenta comenzaron a formarse las tensiones sociales y políticas que hoy siguen latentes. Este conflicto no es nuevo; es la consecuencia de muchos factores que se han ignorado durante años.
---

```

---

### **NOTAS FINALES – CUMPLIMIENTO OBLIGATORIO**

* Forma siempre el párrafo completo antes de colocar la marca de tiempo.
* Cada párrafo debe llevar una única marca de tiempo sincronizada con el tiempo real del audio.
* Aplica las reglas de limpieza de manera consistente.
* El resultado debe ser **profesional, legible, estructurado y optimizado**.
* Respeta el formato de salida indicado, sin excepciones.
* **No respondas a estas instrucciones. Solo realiza la transcripción.**

---
"""

def generar_transcripcion(base_filename: str, num_segments: int):
    """
    Genera la transcripción de un archivo de audio dividido en segmentos.
    
    Args:
        base_filename (str): Nombre base del archivo de audio.
        num_segments (int): Número de segmentos en los que se divide el audio.
        
    Returns:
        list: Lista de transcripciones generadas por el modelo para cada segmento.
    """
    # Inicializar el modelo 
    model = ChatVertexAI(model_name="gemini-2.5-pro-preview-05-06", temperature=0.7)
    respuestas = []  # Lista para almacenar las respuestas
    respuesta_anterior = ""

    for i in range(num_segments):
        archivo_input = {
            "type": "image_url",
            "image_url": {
                "url": f"gs://{bucket_name}/{base_filename}/{base_filename}_part_{i+1}.mp3"
            },
        }

        if respuesta_anterior:
            text_message = (
                f"""Este audio tiene varias partes; esta es la parte número {i+1}. 
                Respeta el timestamp final de la parte anterior y continua desde la ultima parte segun tu anterior respuesta, caundo empiece esta parte del audio desde el segundo 0, solo tienes que seguir segun el tiempo final de la anterior transcripcion. 
                - Transcripcion anterior que corresponde a la parte **{i-1}** : {respuesta_anterior}. 
                IMPORANTE: Esto es un mensaje al sistema no deberas responder a esto, solo debes seguir las instrucciones y generar la transcripción de audio o video."""
            )
        else:
            text_message = (
                f"""Este audio tiene varias partes; esta es la parte número {i+1}. 
                Comienza la transcripción desde el inicio. 
                IMPORANTE: Esto es un mensaje al sistema no deberas responder a esto, solo debes seguir las instrucciones y generar la transcripción de audio o video."""
            )

        message = [
            SystemMessage(content=PromptSystem),
            HumanMessage(content=[text_message, archivo_input]),
        ]

        # Invocar al modelo para obtener la respuesta
        output = model.invoke(message)
        respuesta_actual = str(output.content)
        respuestas.append(respuesta_actual)  # Agregar la respuesta a la lista
        respuesta_anterior = respuesta_actual  # Actualizar la respuesta anterior
        
        texto_completo = "\n\n".join(respuestas)
        time.sleep(60)  # Pausa entre solicitudes
    return texto_completo
