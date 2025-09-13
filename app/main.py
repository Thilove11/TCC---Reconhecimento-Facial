import cv2  
import tempfile
import requests
import os
from datetime import datetime

from kivymd.app import MDApp, App
from kivy.lang import Builder
from kivy.uix.image import Image 
from kivy.graphics.texture import Texture 
from kivy.clock import Clock 
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from kivymd.uix.boxlayout import MDBoxLayout  
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen 
 
Window.size = (480, 720)  

class CameraScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recognition_enabled = False
        self.cap = None

        # Preparação do reconhecimento facial
        tmp_dir = "./tmp"
        os.makedirs(tmp_dir, exist_ok=True)

        # Classificador e modelo
        self.face_cascade = cv2.CascadeClassifier("./lib/haarcascade_frontalface_default.xml")
        self.reconhecedor = cv2.face.EigenFaceRecognizer_create()

        treinamento = requests.get("http://127.0.0.1:8000/api/treinamento/").json()
        model_url = treinamento[0]['modelo']
        tmp_path = os.path.join(tmp_dir, "modelo.xml")
        with open(tmp_path, "wb") as temp_file:
            temp_file.write(requests.get(model_url).content)
            self.reconhecedor.read(temp_file.name)

    # Inicia a câmera
    def open_camera_for_recognition(self):
        # Pega a referência do widget da KV
        self.image = self.ids.camera_feed_full
        
        self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            print("Câmera aberta")
            Clock.schedule_interval(self.load_video, 1.0 / 60.0)
            Clock.schedule_once(self.start_recognition, 6)
        else:
            print("Falha ao abrir a câmera")

    # Captura e exibe o vídeo
    def load_video(self, *args):
        ret, frame = self.cap.read()
        if not ret:
            print("Falha ao capturar o frame")
            return

        # Desenha a elipse central
        altura, largura, _ = frame.shape
        centro_x, centro_y = int(largura / 2), int(altura / 2)
        a, b = 140, 180
        x1, y1 = centro_x - a, centro_y - b
        x2, y2 = centro_x + a, centro_y + b
        cv2.ellipse(frame, (centro_x, centro_y), (a, b), 0, 0, 360, (144, 238, 144), 6)

        # Atualiza textura
        buffer = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
        self.image.texture = texture

        if not self.recognition_enabled:
            return

        # ROI e reconhecimento facial
        roi = frame[y1:y2, x1:x2]
        imagemCinza = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        facesDetectadas = self.face_cascade.detectMultiScale(imagemCinza, 1.1, 5, minSize=(30, 30))

        for (x, y, w, h) in facesDetectadas:
            imagemFace = cv2.resize(imagemCinza[y:y+h, x:x+w], (220, 220))
            label, confianca = self.reconhecedor.predict(imagemFace)
            print(f"ID reconhecido: {label}")

            if label:
                response = requests.get(f"http://127.0.0.1:8000/api/funcionarios/{label}/")
                if response.status_code == 200:
                    funcionario = response.json()
                    self.show_recognized_user(funcionario)

                Clock.unschedule(self.load_video)
                self.reset_camera()
            break

    # Habilita o reconhecimento após 5s
    def start_recognition(self, *args):
        self.recognition_enabled = True

    # Libera a câmera
    def reset_camera(self):
        if self.cap:
            self.cap.release()
        self.image.texture = None
        self.recognition_enabled = False

    # Vai para a tela do usuário reconhecido
    def show_recognized_user(self, funcionario):
        self.manager.current = 'usuario'
        usuario_screen = self.manager.get_screen('usuario')
        usuario_screen.ids.foto.source = funcionario["foto"]
        usuario_screen.ids.nome.text = f"Nome: {funcionario['nome']}"
        usuario_screen.ids.cpf.text = f"CPF: {funcionario['cpf']}"
        usuario_screen.ids.curso.text = f"Curso: {funcionario['curso']}"
        usuario_screen.ids.aula.text = f"Aula: {funcionario['aula']}"
        usuario_screen.ids.matricula.text = f"Matrícula: {funcionario['matricula']}"
        usuario_screen.ids.data_hora.text = f"Data e Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M')}"

        usuario_screen.funcionario_id = funcionario["id"]
        usuario_screen.data_hora = datetime.now().isoformat()
        usuario_screen.ids.card.opacity = 1
        App.get_running_app().funcionario = funcionario


class UsuarioScreen(MDScreen):
    def confirmar_registro(self):
        if not self.funcionario_id:
            print("Funcionário não definido.")
            return
        
        funcionario = {
            "funcionario": self.funcionario_id, # Envia o ID para API
            "data_hora": self.data_hora # Data
        } 
        print(funcionario)
        
        url_api = "http://127.0.0.1:8000/api/registros/"

        try:
            response = requests.post(url_api, json=funcionario)
            
            if response.status_code == 201:
                print("Registro salvo com sucesso!") 
                
                comprovante_screen = self.manager.get_screen('comprovante') 
                 
                mensagem = f"Matricula: {self.funcionario_id}\n{self.ids.data_hora.text}\n\nRegistro salvo com sucesso!\n"
                
                comprovante_screen.ids.comprovante_label.text = mensagem
                
                
                
                # Navegar para a tela de comprovante
                self.manager.current = 'comprovante'
                
            else:
                print("Erro ao salvar registro:", response.json())
                
        except Exception as e:
            print("Erro na conexão com a API:", e)


class ComprovanteScreen(MDScreen):
    def set_dados(self, funcionario):
        self.ids.nome_comprovante.text = f"Nome: {funcionario['nome']}"
        self.ids.curso_comprovante.text = f"Curso: {funcionario['curso']}"
        self.ids.aula_comprovante.text = f"Aula: {funcionario['aula']}"
        self.ids.matricula_comprovante.text = f"Matrícula: {funcionario['matricula']}"
        self.ids.data_hora_comprovante.text = f"Data e Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M')}"

class MainScreen(MDScreen):
    pass

class ScreenManagerApp(ScreenManager):
    def open_camera_for_recognition(self):
        self.current = 'camera'
        camera_screen = self.get_screen('camera')
        print(">>> Abrindo câmera...")
        camera_screen.open_camera_for_recognition()


class MainApp(MDApp):
    funcionario = {}
    def show_comprovante(self, funcionario):
        comprovante_screen = self.root.get_screen('comprovante')
        comprovante_screen.ids.nome_comprovante.text = f"Nome: {funcionario['nome']}"
        comprovante_screen.ids.curso_comprovante.text = f"Curso: {funcionario['curso']}"
        comprovante_screen.ids.aula_comprovante.text = f"Aula: {funcionario['aula']}"
        comprovante_screen.ids.matricula_comprovante.text = f"Matrícula: {funcionario['matricula']}"
        comprovante_screen.ids.data_hora_comprovante.text = f"Data e Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M')}"

        self.root.current = 'comprovante'
    def build(self):
        return Builder.load_string("""
ScreenManagerApp:  
    MainScreen:
    CameraScreen:
    UsuarioScreen:
    ComprovanteScreen:  
    
<MainScreen>:
    name: "main"
    MDScreen:
        md_bg_color: 0.96, 0.96, 0.98, 1
        
        MDTopAppBar: 
            title: "Sistema de Presença Inteligente" 
            specific_text_color: 1, 1, 1, 1
            anchor_title: "center"
            md_bg_color: 0.192, 0.043, 0.282, 1
            elevation: 3
            pos_hint: {"top": 1}
        
        MDBoxLayout:
            orientation: "vertical"
            spacing: "20dp"
            padding: "30dp"
            pos_hint: {"center_x": 0.5, "center_y": 0.45}
            adaptive_size: True
            
            # Hero Section
            MDBoxLayout:
                orientation: "vertical"
                spacing: "25dp"             
                adaptive_size: True
                pos_hint: {"center_x": 0.5}
                size_hint_y: None
                                                               
                # Ícone principal grande
                MDIcon:
                    icon: "face-recognition"
                    font_size: "86dp"
                    theme_icon_color: "Custom"
                    icon_color: 0.1, 0.4, 0.7, 1
                    pos_hint: {"center_x": 0.5}
                    adaptive_size: True
                
                # Título principal
                MDLabel:
                    text: "Reconhecimento Facial"
                    font_style: "H4"
                    theme_text_color: "Primary"
                    halign: "center"
                    adaptive_size: True
                    pos_hint: {"center_x": 0.5}
                    bold: True
                
                # Subtítulo
                MDLabel:
                    text: "Sistema automatizado de registro de presença"
                    font_style: "H6"
                    size_hint_y: None
                    theme_text_color: "Secondary"
                    halign: "center"
                    adaptive_size: True
                    pos_hint: {"center_x": 0.5}
            
            # Card de instruções
            MDCard:
                size_hint: None, None
                size: "380dp", "200dp"
                pos_hint: {"center_x": 0.5}
                md_bg_color: 1, 1, 1, 1
                padding: "25dp"
                
                MDBoxLayout:
                    orientation: "vertical"
                    spacing: "20dp"
                    
                    MDLabel:
                        text: "Como funciona:"
                        font_style: "Subtitle1"
                        theme_text_color: "Primary"
                        halign: "left"
                        adaptive_height: True
                        bold: True
                    
                    # Instruções passo a passo
                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "12dp"
                        
                        MDBoxLayout:
                            orientation: "horizontal"
                            spacing: "15dp"
                            adaptive_height: True
                            
                            MDIcon:
                                icon: "numeric-1-circle"
                                font_size: "24dp"
                                theme_icon_color: "Custom"
                                icon_color: 0.1, 0.4, 0.7, 1
                                adaptive_size: True
                            
                            MDLabel:
                                text: "Clique no botão para iniciar a câmera"
                                font_style: "Body1"
                                theme_text_color: "Secondary"
                                adaptive_height: True
                        
                        MDBoxLayout:
                            orientation: "horizontal"
                            spacing: "15dp"
                            adaptive_height: True
                            
                            MDIcon:
                                icon: "numeric-2-circle"
                                font_size: "24dp"
                                theme_icon_color: "Custom"
                                icon_color: 0.1, 0.4, 0.7, 1
                                adaptive_size: True
                            
                            MDLabel:
                                text: "Posicione seu rosto de frente para a câmera"
                                font_style: "Body1"
                                theme_text_color: "Secondary"
                                adaptive_height: True
                        
                        MDBoxLayout:
                            orientation: "horizontal"
                            spacing: "15dp"
                            adaptive_height: True
                            
                            MDIcon:
                                icon: "numeric-3-circle"
                                font_size: "24dp"
                                theme_icon_color: "Custom"
                                icon_color: 0.1, 0.4, 0.7, 1
                                adaptive_size: True
                            
                            MDLabel:
                                text: "Aguarde o reconhecimento e confirme seus dados"
                                font_style: "Body1"
                                theme_text_color: "Secondary"
                                adaptive_height: True
            
            # Cards de recursos
            MDBoxLayout:
                orientation: "horizontal"
                spacing: "15dp"
                adaptive_height: True
                size_hint_x: None          # <-- desativa expansão horizontal
                width: self.minimum_width
                pos_hint: {"center_x": 0.5}
                
                MDCard:
                    size_hint: None, None
                    size: "110dp", "100dp"
                    md_bg_color: 0.9, 0.95, 1, 1
                    padding: "15dp"
                    
                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "8dp"
                        
                        MDIcon:
                            icon: "shield-check"
                            font_size: "32dp"
                            theme_icon_color: "Custom"
                            icon_color: 0.2, 0.7, 0.3, 1
                            pos_hint: {"center_x": 0.5}
                            adaptive_size: True
                        
                        MDLabel:
                            text: "Seguro"
                            font_style: "Caption"
                            theme_text_color: "Primary"
                            halign: "center"
                            adaptive_height: True
                            bold: True
                
                MDCard:
                    size_hint: None, None
                    size: "110dp", "100dp"
                    md_bg_color: 0.95, 1, 0.9, 1
                    padding: "15dp"
                    pos_hint: {"center_x": 0.5}  # <--- centraliza o card no eixo X
                    
                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "8dp"
                        
                        MDIcon:
                            icon: "lightning-bolt"
                            font_size: "32dp"
                            theme_icon_color: "Custom"
                            icon_color: 0.9, 0.6, 0.1, 1
                            pos_hint: {"center_x": 0.5}
                            adaptive_size: True
                        
                        MDLabel:
                            text: "Rápido"
                            font_style: "Caption"
                            theme_text_color: "Primary"
                            halign: "center"
                            adaptive_height: True
                            bold: True
                
                MDCard:
                    size_hint: None, None
                    size: "110dp", "100dp"
                    md_bg_color: 1, 0.95, 0.9, 1
                    padding: "15dp"
                    
                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "8dp"
                        
                        MDIcon:
                            icon: "brain"
                            font_size: "32dp"
                            theme_icon_color: "Custom"
                            icon_color: 0.7, 0.3, 0.8, 1
                            pos_hint: {"center_x": 0.5}
                            adaptive_size: True
                        
                        MDLabel:
                            text: "Inteligente"
                            font_style: "Caption"
                            theme_text_color: "Primary"
                            halign: "center"
                            adaptive_height: True
                            bold: True

            # Botão principal
            MDRaisedButton:
                text: 'INICIAR RECONHECIMENTO'
                font_size: '18sp'
                pos_hint: {'center_x': 0.5}
                md_bg_color: 0.145, 0.02, 0.18, 1
                size_hint: (0.85, None)
                height: "56dp"
                on_press: 
                    app.root.open_camera_for_recognition()
            
            # Texto de rodapé
            MDLabel:
                text: "Tecnologia de reconhecimento facial segura e confiável"
                font_style: "Caption"
                theme_text_color: "Hint"
                halign: "center"
                adaptive_height: True
                pos_hint: {"center_x": 0.5}
                                   
<CameraScreen>:
    name: "camera"
    MDScreen:
        md_bg_color: 0.96, 0.96, 0.98, 1
        
        # Container principal com padding
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(20)
            
            # Header com título
            MDBoxLayout:
                size_hint_y: None
                height: dp(60)
                
                MDLabel:
                    text: "Centrelize seu rosto na área da câmera"
                    theme_text_color: "Primary"
                    font_style: "H5"
                    halign: "center"
                    text_color: 1, 1, 1, 1
            
            # Container da câmera com borda
            MDCard:
                md_bg_color: 0.1, 0.1, 0.1, 1
                elevation: 8
                padding: dp(10)
                
                Image:
                    id: camera_feed_full
                    allow_stretch: True
                    keep_ratio: True
                                   
<UsuarioScreen>:
    name: "usuario"
    MDScreen: 
        md_bg_color: 0.98, 0.98, 0.98, 1
        
        MDTopAppBar: 
            title: "Confirmação de Dados" 
            specific_text_color: 1, 1, 1, 1
            anchor_title: "center"
            md_bg_color: 0.145, 0.02, 0.18, 1
            elevation: 3
            pos_hint: {"top": 1}
        
        # Espaçamento do topo
        MDBoxLayout:
            orientation: "vertical"
            spacing: "0dp"
            padding: "0dp"
            
            # Espaço em branco para afastar do header
            Widget:
                size_hint: 1, None
                height: "80dp"
            
            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    spacing: "25dp"
                    padding: "20dp"
                    adaptive_height: True
                    
                    # Card principal com dados do usuário
                    MDCard:
                        id: card
                        size_hint: 1, None
                        height: "500dp"
                        md_bg_color: 1, 1, 1, 1
                        opacity: 0
                        padding: "20dp"
                        
                        MDBoxLayout:
                            orientation: "vertical"
                            spacing: "20dp"
                            
                            # Header do card
                            MDBoxLayout:
                                orientation: "horizontal"
                                spacing: "15dp"
                                adaptive_height: True
                                
                                AsyncImage:
                                    id: foto
                                    size_hint: None, None
                                    size: "80dp", "80dp"
                                    
                                MDBoxLayout:
                                    orientation: "vertical"
                                    spacing: "5dp"
                                    
                                    MDLabel:
                                        text: "Usuário Identificado"
                                        font_style: "H6"
                                        theme_text_color: "Primary"
                                        adaptive_height: True
                                        
                                    MDIcon:
                                        icon: "check-circle"
                                        theme_icon_color: "Custom"
                                        icon_color: 0.2, 0.7, 0.3, 1
                                        font_size: "24dp"
                                        adaptive_size: True
                            
                            MDSeparator:
                                height: "2dp"
                            
                            # Dados do usuário
                            MDBoxLayout:
                                orientation: "vertical"
                                spacing: "15dp"
                                
                                MDBoxLayout:
                                    orientation: "horizontal"
                                    spacing: "10dp"
                                    adaptive_height: True
                                    md_bg_color: 0.95, 0.95, 0.95, 1
                                    padding: "15dp"
                                    
                                    MDIcon:
                                        icon: "account"
                                        font_size: "20dp"
                                        theme_icon_color: "Custom"
                                        icon_color: 0.1, 0.4, 0.7, 1
                                        adaptive_size: True
                                    
                                    MDLabel:
                                        id: nome
                                        theme_text_color: "Primary"
                                        font_style: "Subtitle1"
                                        adaptive_height: True
                                
                                MDBoxLayout:
                                    orientation: "horizontal"
                                    spacing: "10dp"
                                    adaptive_height: True
                                    md_bg_color: 0.95, 0.95, 0.95, 1
                                    padding: "15dp"
                                    
                                    MDIcon:
                                        icon: "card-account-details"
                                        font_size: "20dp"
                                        theme_icon_color: "Custom"
                                        icon_color: 0.1, 0.4, 0.7, 1
                                        adaptive_size: True
                                    
                                    MDLabel:
                                        id: cpf
                                        theme_text_color: "Secondary"
                                        font_style: "Body1"
                                        adaptive_height: True
                                
                                MDBoxLayout:
                                    orientation: "horizontal"
                                    spacing: "10dp"
                                    adaptive_height: True
                                    md_bg_color: 0.95, 0.95, 0.95, 1
                                    padding: "15dp"
                                    
                                    MDIcon:
                                        icon: "school"
                                        font_size: "20dp"
                                        theme_icon_color: "Custom"
                                        icon_color: 0.1, 0.4, 0.7, 1
                                        adaptive_size: True
                                    
                                    MDLabel:
                                        id: curso
                                        theme_text_color: "Secondary"
                                        font_style: "Body1"
                                        adaptive_height: True
                                
                                MDBoxLayout:
                                    orientation: "horizontal"
                                    spacing: "10dp"
                                    adaptive_height: True
                                    md_bg_color: 0.95, 0.95, 0.95, 1
                                    padding: "15dp"
                                    
                                    MDIcon:
                                        icon: "book-open"
                                        font_size: "20dp"
                                        theme_icon_color: "Custom"
                                        icon_color: 0.1, 0.4, 0.7, 1
                                        adaptive_size: True
                                    
                                    MDLabel:
                                        id: aula
                                        theme_text_color: "Secondary"
                                        font_style: "Body1"
                                        adaptive_height: True
                                
                                MDBoxLayout:
                                    orientation: "horizontal"
                                    spacing: "10dp"
                                    adaptive_height: True
                                    md_bg_color: 0.95, 0.95, 0.95, 1
                                    padding: "15dp"
                                    
                                    MDIcon:
                                        icon: "badge-account"
                                        font_size: "20dp"
                                        theme_icon_color: "Custom"
                                        icon_color: 0.1, 0.4, 0.7, 1
                                        adaptive_size: True
                                    
                                    MDLabel:
                                        id: matricula
                                        theme_text_color: "Secondary"
                                        font_style: "Body1"
                                        adaptive_height: True
                                
                                MDBoxLayout:
                                    orientation: "horizontal"
                                    spacing: "10dp"
                                    adaptive_height: True
                                    md_bg_color: 0.91, 0.85, 0.96, 0.5
                                    padding: "15dp"
                                    
                                    MDIcon:
                                        icon: "clock"
                                        font_size: "20dp"
                                        theme_icon_color: "Custom"
                                        icon_color: 0.7, 0.4, 0.1, 1
                                        adaptive_size: True
                                    
                                    MDLabel:
                                        id: data_hora
                                        theme_text_color: "Primary"
                                        font_style: "Subtitle2"
                                        adaptive_height: True
                    
                    # Botões de ação
                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: "15dp"
                        adaptive_height: True
                        size_hint: 1, None
                        height: "48dp"
                        
                        MDRaisedButton:
                            text: 'CONFIRMAR'
                            font_size: '14sp'
                            size_hint: 0.6, 1
                            md_bg_color: 0.192, 0.043, 0.282, 1
                            on_press: app.show_comprovante(app.funcionario)
                        
                        MDRaisedButton:
                            text: 'CANCELAR'
                            font_size: '14sp'
                            size_hint: 0.4, 1
                            md_bg_color: 0.706, 0.706, 0.706, 1
                            on_press: 
                                root.manager.get_screen('camera').reset_camera()
                                root.manager.current = 'main'
                                
                
<ComprovanteScreen>:
    name: "comprovante"
    MDScreen: 
        md_bg_color: 0.98, 0.98, 0.98, 1
        
        MDTopAppBar: 
            title: "Comprovante de Presença" 
            specific_text_color: 1, 1, 1, 1
            anchor_title: "center"
            md_bg_color: 0.2, 0.7, 0.3, 1
            elevation: 3
            pos_hint: {"top": 1}
        
        MDBoxLayout:
            orientation: "vertical"
            spacing: "30dp"
            padding: "20dp"
            pos_hint: {"center_x": 0.5, "center_y": 0.45}
            adaptive_size: True
            
            # Ícone de sucesso
            MDIcon:
                icon: "check-circle-outline"
                font_size: "72dp"
                theme_icon_color: "Custom"
                icon_color: 0.2, 0.7, 0.3, 1
                pos_hint: {"center_x": 0.5}
                adaptive_size: True
            
            # Card do comprovante
            MDCard:
                id: card_comprovante
                size_hint: None, None
                size: "350dp", "450dp"
                md_bg_color: 1, 1, 1, 1
                pos_hint: {"center_x": 0.5}
                padding: "25dp"
                
                MDBoxLayout:
                    orientation: "vertical"
                    spacing: "20dp"
                    
                    # Header do comprovante
                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "10dp"
                        adaptive_height: True
                        
                        MDLabel:
                            text: "✓ PRESENÇA CONFIRMADA"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0.2, 0.7, 0.3, 1
                            font_style: "H6"
                            bold: True
                            adaptive_height: True
                        
                        MDLabel:
                            text: "Seu registro foi salvo com sucesso"
                            halign: "center"
                            theme_text_color: "Secondary"
                            font_style: "Body2"
                            adaptive_height: True
                    
                    MDSeparator:
                        height: "2dp"
                        color: 0.9, 0.9, 0.9, 1
                    
                    # Dados do comprovante
                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "15dp"
                        
                        MDBoxLayout:
                            orientation: "horizontal"
                            spacing: "10dp"
                            adaptive_height: True
                            md_bg_color: 0.98, 0.98, 0.98, 1
                            padding: "10dp"
                            
                            MDIcon:
                                icon: "account"
                                font_size: "20dp"
                                theme_icon_color: "Custom"
                                icon_color: 0.1, 0.4, 0.7, 1
                                adaptive_size: True
                            
                            MDLabel:
                                id: nome_comprovante
                                text: "Nome: "
                                theme_text_color: "Primary"
                                font_style: "Body1"
                                adaptive_height: True
                        
                        MDBoxLayout:
                            orientation: "horizontal"
                            spacing: "10dp"
                            adaptive_height: True
                            md_bg_color: 0.98, 0.98, 0.98, 1
                            padding: "10dp"
                            
                            MDIcon:
                                icon: "school"
                                font_size: "20dp"
                                theme_icon_color: "Custom"
                                icon_color: 0.1, 0.4, 0.7, 1
                                adaptive_size: True
                            
                            MDLabel:
                                id: curso_comprovante
                                text: "Curso: "
                                theme_text_color: "Primary"
                                font_style: "Body1"
                                adaptive_height: True

                        MDBoxLayout:
                            orientation: "horizontal"
                            spacing: "10dp"
                            adaptive_height: True
                            md_bg_color: 0.98, 0.98, 0.98, 1
                            padding: "10dp"
                            
                            MDIcon:
                                icon: "book-open"
                                font_size: "20dp"
                                theme_icon_color: "Custom"
                                icon_color: 0.1, 0.4, 0.7, 1
                                adaptive_size: True
                            
                            MDLabel:
                                id: aula_comprovante
                                text: "Aula: "
                                theme_text_color: "Primary"
                                font_style: "Body1"
                                adaptive_height: True

                        MDBoxLayout:
                            orientation: "horizontal"
                            spacing: "10dp"
                            adaptive_height: True
                            md_bg_color: 0.98, 0.98, 0.98, 1
                            padding: "10dp"
                            
                            MDIcon:
                                icon: "badge-account"
                                font_size: "20dp"
                                theme_icon_color: "Custom"
                                icon_color: 0.1, 0.4, 0.7, 1
                                adaptive_size: True
                            
                            MDLabel:
                                id: matricula_comprovante
                                text: "Matrícula: "
                                theme_text_color: "Primary"
                                font_style: "Body1"
                                adaptive_height: True
                        
                        MDSeparator:
                            height: "1dp"
                            color: 0.95, 0.95, 0.95, 1
                        
                        MDBoxLayout:
                            orientation: "horizontal"
                            spacing: "10dp"
                            adaptive_height: True
                            md_bg_color: 0.91, 0.85, 0.96, 0.5
                            padding: "10dp"
                            
                            MDIcon:
                                icon: "clock"
                                font_size: "20dp"
                                theme_icon_color: "Custom"
                                icon_color: 0.7, 0.4, 0.1, 1
                                adaptive_size: True
                            
                            MDLabel:
                                id: data_hora_comprovante
                                text: "Data e Hora: "
                                theme_text_color: "Primary"
                                font_style: "Subtitle2"
                                bold: True
                                adaptive_height: True
            
            # Botão finalizar
            MDRaisedButton:
                text: 'FINALIZAR'
                font_size: '16sp'
                pos_hint: {'center_x': 0.5}
                md_bg_color: 0.192, 0.043, 0.282, 1
                size_hint: (0.8, None)
                height: "48dp"
                on_press:
                    root.manager.get_screen('camera').reset_camera()
                    root.manager.current = 'main'
""")

if __name__ == '__main__':
    MainApp().run()