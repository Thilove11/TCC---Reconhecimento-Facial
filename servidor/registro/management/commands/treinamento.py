import os
import numpy as np
import cv2
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from registro.models import ColetaFaces, Treinamento
from tempfile import gettempdir

class Command(BaseCommand):
    help = "Treina o classificador EigenFaces para reconhecimento facial"

    def handle(self, *args, **kwargs):
        self.treinar_eigenfaces()

    def treinar_eigenfaces(self):
        self.stdout.write(self.style.WARNING("🚀 Iniciando Treinamento EigenFaces..."))
        print(f"OpenCV versão: {cv2.__version__}")

        # Criar o modelo EigenFaces
        eigenFace = cv2.face.EigenFaceRecognizer_create(
            num_components=80,    # mais componentes melhora separação
            threshold=0           # threshold é ignorado
        )

        faces = []
        labels = []
        erro_count = 0

        pessoas = {}  # agrupar imagens por pessoa

        # ---------------------------
        # 1. COLETA E PRÉ-PROCESSAMENTO
        # ---------------------------
        for coleta in ColetaFaces.objects.all():

            try:
                image_file = coleta.image.url.replace('/media/roi/', '')
                image_path = os.path.join(settings.MEDIA_ROOT, 'roi', image_file)

                if not os.path.exists(image_path):
                    print(f"⚠ Caminho não encontrado: {image_path}")
                    erro_count += 1
                    continue

                image = cv2.imread(image_path)
                if image is None:
                    print(f"⚠ Erro ao carregar: {image_path}")
                    erro_count += 1
                    continue

                # Pré-processamento
                img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                img_gray = cv2.resize(img_gray, (220, 220))

                # NORMALIZAÇÃO → extremamente importante!
                img_gray = cv2.equalizeHist(img_gray)  

                funcionario_id = coleta.funcionario.id

                if funcionario_id not in pessoas:
                    pessoas[funcionario_id] = []

                pessoas[funcionario_id].append(img_gray)

            except Exception as e:
                print(f"Erro ao processar imagem: {e}")
                erro_count += 1

        # ---------------------------
        # 2. VERIFICAR SE HÁ MÍNIMO DE IMAGENS POR PESSOA
        # ---------------------------
        for pessoa_id, imgs in pessoas.items():
            if len(imgs) < 29:
                print(f"❌ Funcionário {pessoa_id} IGNORADO: mínimo 5 imagens exigido (possui {len(imgs)})")
                continue

            for img in imgs:
                faces.append(img.astype("float32"))  # recomendado
                labels.append(pessoa_id)

        if len(faces) == 0:
            print("❌ Nenhuma face válida para treinamento.")
            return

        # Converter para matriz
        faces_np = np.array(faces, dtype="float32")
        labels_np = np.array(labels)

        print(f"Total de imagens para treinamento: {len(faces_np)}")
        print(f"Total de pessoas: {len(set(labels_np))}")

        # ---------------------------
        # 3. TREINAMENTO
        # ---------------------------
        try:
            eigenFace.train(faces_np, labels_np)

            temp_dir = gettempdir()
            model_filename = os.path.join(temp_dir, 'classificadorEigen.yml')
            eigenFace.write(model_filename)

            # salvar no banco
            with open(model_filename, 'rb') as f:
                treinamento, created = Treinamento.objects.get_or_create()
                treinamento.modelo.save('classificadorEigen.yml', File(f))

            os.remove(model_filename)

            self.stdout.write(self.style.ERROR(f"⚠ Imagens com erro: {erro_count}"))
            self.stdout.write(self.style.SUCCESS("🎉 Treinamento FINALIZADO com sucesso!"))

        except Exception as e:
            print(f"❌ Erro durante o treinamento: {e}")