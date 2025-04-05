from openai import OpenAI
import speech_recognition as sr
import pyttsx3
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading

# Configuración inicial
r = sr.Recognizer()
cliente = OpenAI(api_key="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", 
                base_url="https://openrouter.ai/api/v1")
engine = pyttsx3.init()

class InterfazApp:
    def __init__(self, ventana):
        self.ventana = ventana
        self.hablando = False
        self.idioma = "es-ES"  
        self.ultima_respuesta = ""  
        
        ventana.title("Solvin AI")
        ventana.geometry("650x420")
        
        self.crear_menu()
        
        ventana.grid_columnconfigure(0, weight=1)
        ventana.grid_rowconfigure(0, weight=1)
        
        self.chat_area = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, state='disabled')
        self.chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.entrada_texto = ttk.Entry(ventana, width=50)
        self.entrada_texto.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.entrada_texto.bind("<Return>", lambda event: self.enviar_texto())
        
        botones_frame = ttk.Frame(ventana)
        botones_frame.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        
        self.btn_enviar = ttk.Button(botones_frame, text="Enviar", command=self.enviar_texto)
        self.btn_enviar.pack(side=tk.LEFT, padx=5)
        
        self.btn_escuchar = ttk.Button(botones_frame, text="🎤 Escuchar", command=self.iniciar_escucha)
        self.btn_escuchar.pack(side=tk.LEFT, padx=5)
        
        self.btn_detener = ttk.Button(botones_frame, text="⏹ Detener", command=self.detener_habla)
        self.btn_detener.pack(side=tk.LEFT, padx=5)
        self.btn_detener.config(state=tk.DISABLED)
        
        self.btn_reanudar = ttk.Button(botones_frame, text="▶ Reanudar", command=self.reanudar_lectura)
        self.btn_reanudar.pack(side=tk.LEFT, padx=5)
        self.btn_reanudar.config(state=tk.DISABLED)
        
        self.mostrar_mensaje("AI: Hola, ¿en qué puedo ayudarte?", "ai")
        self.iniciar_habla("Hola, ¿en qué puedo ayudarte?")
        
    def crear_menu(self):
        menubar = tk.Menu(self.ventana)

        menu_idioma = tk.Menu(menubar, tearoff=0)
        menu_idioma.add_command(label="Español (ES)", command=lambda: self.cambiar_idioma("es-ES"))
        menu_idioma.add_command(label="Inglés (US)", command=lambda: self.cambiar_idioma("en-US"))
        menubar.add_cascade(label="Idioma", menu=menu_idioma)
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menu_ayuda.add_command(label="Acerca de...", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        self.ventana.config(menu=menubar)
        
    def cambiar_idioma(self, nuevo_idioma):
        self.idioma = nuevo_idioma
        mensaje = f"Idioma cambiado a {'Español' if nuevo_idioma == 'es-ES' else 'Inglés'}"
        self.mostrar_mensaje(f"System: {mensaje}", "system")
        self.hablar(mensaje)
        
    def mostrar_mensaje(self, mensaje, sender):
        self.chat_area.configure(state='normal')
        tag = sender
        self.chat_area.insert(tk.END, f"{mensaje}\n\n", tag)
        self.chat_area.configure(state='disabled')
        self.chat_area.see(tk.END)
        
    def iniciar_habla(self, texto):
        self.hablando = True
        self.ultima_respuesta = texto
        self.btn_detener.config(state=tk.NORMAL)
        self.btn_reanudar.config(state=tk.DISABLED)
        threading.Thread(target=self.hablar, args=(texto,), daemon=True).start()
        
    def hablar(self, texto):
        engine.say(texto)
        engine.runAndWait()
        self.hablando = False
        self.ventana.after(0, self.btn_detener.config, {'state': tk.DISABLED})
        self.ventana.after(0, self.btn_reanudar.config, {'state': tk.NORMAL})
        
    def detener_habla(self):
        if self.hablando:
            engine.stop()
            self.hablando = False
            self.btn_detener.config(state=tk.DISABLED)
            self.btn_reanudar.config(state=tk.NORMAL)
            self.mostrar_mensaje("System: Reproducción detenida", "system")
            
    def reanudar_lectura(self):
        if self.ultima_respuesta:
            self.iniciar_habla(self.ultima_respuesta)
            self.btn_reanudar.config(state=tk.DISABLED)
            
    def enviar_texto(self):
        texto = self.entrada_texto.get()
        if texto:
            self.mostrar_mensaje(f"Tú: {texto}", "user")
            self.entrada_texto.delete(0, tk.END)
            threading.Thread(target=self.procesar_solicitud, args=(texto,), daemon=True).start()
            
    def procesar_solicitud(self, contenido):
        try:
            respuesta = self.enviar_a_ai(contenido)
            self.ventana.after(0, self.mostrar_mensaje, f"AI: {respuesta}", "ai")
            self.ventana.after(0, self.iniciar_habla, respuesta)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
            
    def enviar_a_ai(self, contenido):
        try:
            chat = cliente.chat.completions.create(
                model="deepseek/deepseek-r1:free",
                messages=[{"role": "user", "content": contenido}],
                extra_body={"reasonin": {"effort": "high", "exclude": True}}
            )
            return chat.choices[0].message.content
        except Exception as e:
            return f"Error al procesar la solicitud: {str(e)}"
            
    def iniciar_escucha(self):
        self.btn_escuchar.config(state=tk.DISABLED, text="Escuchando...")
        threading.Thread(target=self.procesar_voz, daemon=True).start()
        
    def procesar_voz(self):
        try:
            with sr.Microphone() as source:
                audio = r.listen(source)
                texto = r.recognize_google(audio, language=self.idioma)
                if texto.lower() in ['salir', 'exit']:
                    self.ventana.quit()
                self.ventana.after(0, self.mostrar_mensaje, f"Tú (voz): {texto}", "user")
                self.ventana.after(0, self.procesar_respuesta_voz, texto)
        except sr.UnknownValueError:
            self.ventana.after(0, messagebox.showwarning, "Advertencia", "No se pudo entender el audio")
        except sr.RequestError as e:
            self.ventana.after(0, messagebox.showerror, "Error", f"Error en el servicio: {e}")
        finally:
            self.ventana.after(0, self.btn_escuchar.config, {"state": tk.NORMAL, "text": "🎤 Escuchar"})
            
    def procesar_respuesta_voz(self, texto):
        respuesta = self.enviar_a_ai(texto)
        self.mostrar_mensaje(f"AI: {respuesta}", "ai")
        self.iniciar_habla(respuesta)
    
    def mostrar_acerca_de(self):
        acerca_ventana = tk.Toplevel(self.ventana)
        acerca_ventana.title("Acerca de Solvin AI")
        acerca_ventana.resizable(False, False)
        
        frame = ttk.Frame(acerca_ventana, padding=20)
        frame.pack(fill='both', expand=True)
        
        info_texto = f"""
        Solvin AI - Versión 1.0
        
        Desarrollado por: InfernoidPl4y
        Contacto: infernoidpl4y@gmail.com
        GitHub: https://github.com/infernoidpl4y
        Licencia: GPLv3
        
        Tecnologías utilizadas:
        - OpenAI API
        - SpeechRecognition
        - Pyttsx3
        - Tkinter
        """
        
        ttk.Label(frame, text=info_texto, justify=tk.LEFT, font=('Consolas', 10)).pack(pady=10)
        ttk.Button(frame, text="Cerrar", command=acerca_ventana.destroy).pack(pady=10)

if __name__ == "__main__":
    ventana = tk.Tk()
    ventana.tk_setPalette(background='#f0f0f0', foreground='black')
    style = ttk.Style()
    style.configure("TButton", padding=6, relief="flat")
    style.map("TButton", background=[('active', '#e0e0e0')])
    
    chat_style = {
        "user": {"foreground": "blue", "font": ('Arial', 10, 'bold')},
        "ai": {"foreground": "green", "font": ('Arial', 10)},
        "system": {"foreground": "gray", "font": ('Arial', 8, 'italic')}
    }
    
    app = InterfazApp(ventana)
    for tag, options in chat_style.items():
        app.chat_area.tag_configure(tag, **options)
    
    ventana.mainloop()