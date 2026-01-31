import cv2
import face_recognition
import pickle

# ================================
# 📌 Carregar encodings treinados
# ================================
print("[INFO] Carregando encodings...")
with open("encodings.pickle", "rb") as f:
    data = pickle.load(f)

# ================================
# 📷 Iniciar webcam
# ================================
video = cv2.VideoCapture(0)

if not video.isOpened():
    print("Erro: não foi possível acessar a webcam.")
    exit()

print("[INFO] Webcam iniciada. Pressione 'q' para sair.")

while True:
    ret, frame = video.read()
    if not ret:
        print("Erro ao capturar frame.")
        break

    # Reduz imagem para acelerar o processamento
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # ================================
    # 🔍 Detectar rostos na imagem
    # ================================
    face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    names = []

    # ================================
    # 🧠 Comparar embeddings
    # ================================
    for encoding in face_encodings:
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Desconhecido"

        # Calcular distâncias
        face_distances = face_recognition.face_distance(data["encodings"], encoding)

        # Melhor correspondência
        if len(face_distances) > 0:
            best_match = face_distances.argmin()
            if matches[best_match]:
                name = data["names"][best_match]

        names.append(name)

    # ================================
    # 🖼️ Mostrar resultados na tela
    # ================================
    for ((top, right, bottom, left), name) in zip(face_locations, names):
        # Reverter escala 0.5 → 1.0
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(
            frame,
            name,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    cv2.imshow("Reconhecimento Facial", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video.release()
cv2.destroyAllWindows()