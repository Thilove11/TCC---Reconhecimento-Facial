import cv2
import os
import face_recognition
import pickle
from imutils import paths

# Caminho para a pasta com subpastas das pessoas
DATASET_DIR = "dataset"

# Onde salvar os encodings
OUTPUT_FILE = "encodings.pickle"

print("[INFO] Carregando imagens do dataset...")
image_paths = list(paths.list_images(DATASET_DIR))

known_encodings = []
known_names = []

# Loop em todas imagens
for image_path in image_paths:
    print(f"[INFO] Processando: {image_path}")

    # Nome da pessoa = nome da pasta
    name = image_path.split(os.path.sep)[-2]

    # Carrega a imagem
    image = cv2.imread(image_path)
    if image is None:
        print(f"[AVISO] Erro ao carregar imagem: {image_path}")
        continue

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Detecta rosto(s) na imagem
    boxes = face_recognition.face_locations(rgb, model="hog")

    # Extrai embeddings dos rostos encontrados
    encodings = face_recognition.face_encodings(rgb, boxes)

    for encoding in encodings:
        known_encodings.append(encoding)
        known_names.append(name)

print(f"[INFO] Total de rostos processados: {len(known_encodings)}")

# Salva tudo no pickle
print(f"[INFO] Salvando encodings em {OUTPUT_FILE}...")
data = {"encodings": known_encodings, "names": known_names}

with open(OUTPUT_FILE, "wb") as f:
    pickle.dump(data, f)

print("[INFO] Finalizado!")