import os
import numpy as np
import cv2
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from registro.models import ColetaFaces, Treinamento
from tempfile import gettempdir

class Command(BaseCommand):
    help = "Treina o classficador Eigen para reconhecimento facial"

    def handle(self, *args, **kwargs):
       self.treinamento_face()

    def treinamento_face(self):
        self.stdout.write(self.style.WARNING("Iniciando Treinamento"))
        print(cv2.__version__)

        eigenFace = cv2.face.EigenFaceRecognizer_create(num_components=50, threshold=0)

        faces, labels = [], []
        erro_count = 0

        for coleta in ColetaFaces.objects.all():
            image_file = coleta.image.url.replace('/media/roi/', '')
            image_path = os.path.join(settings.MEDIA_ROOT, 'roi', image_file)

            if not os.path.exists(image_path):
                print(f"Caminho não encontrado: {image_path}")
                erro_count += 1
                continue

            image = cv2.imread(image_path)
            if image is None:
                print(f"Erro ao carregar a imagem: {image_path}")
                erro_count += 1
                continue

            imagemFace = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            imagemFace = cv2.resize(imagemFace, (220, 220))
            faces.append(imagemFace)
            labels.append(coleta.funcionario.id)

        if not faces:
            print("Nenhuma face encontrada para treinamento.")
            return
        
        try:
            eigenFace.train(np.array(faces), np.array(labels))
            print(f"len{faces}")

            temp_dir = gettempdir()
            model_filename = os.path.join(temp_dir, 'classificadorEigen.yml')
            eigenFace.write(model_filename)

            with open(model_filename, 'rb') as f:
                treinamento, created = Treinamento.objects.get_or_create()
                treinamento.modelo.save('classificadorEigen.yml', File(f))

            os.remove(model_filename)
            self.stdout.write(self.style.ERROR(f"Imagens com erro no carregamento: {erro_count}"))
            self.stdout.write(self.style.SUCCESS("Treinamento EFETUADO"))
        
        except Exception as e:
            print(f"Erro durante o treinamento: {e}")