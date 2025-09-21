# 1. Importação das bibliotecas necessárias
import speech_recognition as sr
from gtts import gTTS
import os
import playsound
from datetime import datetime
import webbrowser
import wikipedia
import platform  # Para verificar o sistema operacional
import re        # Para expressões regulares (extração de texto inteligente)

# 2. Função para o assistente "falar" (Text-to-Speech)
def speak(text):
    """Converte texto em áudio e o reproduz de forma segura."""
    tts = gTTS(text=text, lang='pt-br')
    filename = "voice.mp3"
    
    try:
        tts.save(filename)
        playsound.playsound(filename)
    except Exception as e:
        print(f"Erro ao tentar falar: {e}")
    finally:
        # --- MELHORIA: Garante que o arquivo seja removido mesmo se ocorrer um erro ---
        if os.path.exists(filename):
            os.remove(filename)

# 3. Função para "ouvir" o usuário (Speech-to-Text)
def get_audio():
    """Ouve o áudio do microfone e o converte em texto."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Ouvindo...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        said = ""

        try:
            print("Reconhecendo...")
            said = r.recognize_google(audio, language='pt-BR')
            print(f"Você disse: {said}")
        # --- MELHORIA: Tratamento de erro para microfone não encontrado ---
        except sr.RequestError:
            speak("Desculpe, estou com problemas de conexão no momento.")
        except Exception as e:
            speak("Desculpe, não entendi o que você disse.")
            print(f"Erro de reconhecimento: {e}")
            
    return said.lower()

# 4. Função para extrair o termo de pesquisa da Wikipedia
def extrair_termo_wikipedia(text):
    """Extrai o termo de pesquisa de forma mais inteligente usando regex."""
    # Procura por padrões como "pesquisar por [termo]", "o que é [termo]" ou "quem foi [termo]"
    match = re.search(r'(pesquisar por|o que é|quem foi)\s(.+)', text)
    if match:
        return match.group(2) # Retorna o segundo grupo capturado (o termo)
    return ""

# 5. Função para executar os comandos
def respond(text):
    """Executa ações com base no texto recebido."""
    
    # Abrir sites
    if 'abrir mercadolivre' in text:
        speak("Abrindo o Mercado Livre.")
        webbrowser.open("https://www.mercadolivre.com.br")
    elif 'abrir whatsapp' in text:
        speak("Abrindo o WhatsApp Web.")
        webbrowser.open("https://web.whatsapp.com/")

    # Abrir Calculadora (compatível com Windows, Mac e Linux)
    elif 'abrir calculadora' in text:
        speak("Abrindo a calculadora.")
        # --- MELHORIA: Compatibilidade com diferentes sistemas operacionais ---
        system = platform.system()
        if system == "Windows":
            os.system('calc')
        elif system == "Darwin": # macOS
            os.system('open -a Calculator')
        elif system == "Linux":
            os.system('gnome-calculator') # Pode variar dependendo da distro
        else:
            speak("Não sei como abrir a calculadora no seu sistema.")

    # Pesquisar na Wikipedia
    elif any(keyword in text for keyword in ['pesquisar por', 'o que é', 'quem foi']):
        termo = extrair_termo_wikipedia(text)
        if termo:
            try:
                wikipedia.set_lang("pt")
                speak(f"Pesquisando por {termo} na Wikipedia.")
                result = wikipedia.summary(termo, sentences=2)
                speak("De acordo com a Wikipedia:")
                print(result)
                speak(result)
            except wikipedia.exceptions.PageError:
                speak(f"Desculpe, não encontrei a página para {termo}.")
            except wikipedia.exceptions.DisambiguationError:
                speak(f"Existem muitos resultados para {termo}. Por favor, seja mais específico.")
        else:
            speak("Não entendi o que você quer pesquisar.")
    
    # Informar as horas
    elif 'que horas são' in text:
        strTime = datetime.now().strftime("%H:%M")
        speak(f"Agora são {strTime}.")
        
    # Encerrar o programa
    elif 'desligar' in text or 'encerrar' in text or 'fechar' in text or 'sair' in text:
        speak("Até logo!")
        return False
    
    return True

# 6. Loop principal do assistente
if __name__ == "__main__":

    speak("Olá! Como posso ajudar?")
    
    running = True
    while running:
        text = get_audio()
        if text:
            running = respond(text)