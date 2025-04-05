from openai import OpenAI
import speech_recognition as sr
import pyttsx3

r = sr.Recognizer()
cliente=OpenAI(api_key="API_KEY de OpenRouter", base_url="https://openrouter.ai/api/v1")
engine = pyttsx3.init()

def hablar(texto):
    engine.say(texto)
    engine.runAndWait()

def enviar(contenido):
    try:
        chat = cliente.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {
                "role":"user",
                "content":contenido
                }
            ],
            extra_body={
                "reasonin":{
                    "effort": "high",
                    "exclude": True
                }
            }
        )
        print(chat.choices[0].message.content)
        hablar(str(chat.choices[0].message.content))
    except KeyboardInterrupt:
        engine.stop()
        return ""

def escuchar():
    with sr.Microphone() as source:
        print("Escuchando...")
        audio = r.listen(source)
        try:
            # Usar el reconocedor de Google (requiere internet)
            texto = r.recognize_google(audio, language='es-ES')
            if texto=="Salir" or texto=='salir':
                quit()
            print(f"Usuario: {texto}")
            enviar(str(texto))
        except sr.UnknownValueError:
            print("No se pudo entender el audio")
        except sr.RequestError as e:
            print(f"Error en el servicio: {e}")
        except KeyboardInterrupt:
            engine.stop()
            return ""

def main():
    hablar('Hola, en que puedo ayudarte?')
    while True:
        try:
            escuchar()
        except KeyboardInterrupt:
            engine.stop()
            escuchar()


if __name__=="__main__":
    main()
