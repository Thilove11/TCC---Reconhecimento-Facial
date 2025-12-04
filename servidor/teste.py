import cv2
import os

def extrair_amostras(num_amostras=30, largura=220, altura=220, pasta="amostras", nome="usuario"):
    # Carrega o classificador Haarcascade
    detector_face = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # Cria a pasta se não existir
    os.makedirs(pasta, exist_ok=True)

    camera = cv2.VideoCapture(0)
    contador = 0

    print("[INFO] Iniciando captura...")

    while contador < num_amostras:
        ret, frame = camera.read()
        if not ret:
            print("Erro ao acessar a câmera")
            break

        # Converte pra cinza
        cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detecta rosto
        faces = detector_face.detectMultiScale(cinza, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            # Recorta o rosto
            face_img = frame[y:y+h, x:x+w]

            # Redimensiona
            face_img = cv2.resize(face_img, (largura, altura))

            # Salva a imagem
            contador += 1
            caminho = os.path.join(pasta, f"{nome}_{contador}.jpg")
            cv2.imwrite(caminho, face_img)

            print(f"[OK] Amostra {contador}/{num_amostras} salva em {caminho}")

            # Mostra o rosto capturado
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

        cv2.imshow("Capturando Faces...", frame)

        if cv2.waitKey(1) == 27:  # ESC para sair
            break

    camera.release()
    cv2.destroyAllWindows()
    print("[INFO] Captura finalizada.")

if __name__ == "__main__":
    extrair_amostras(
        num_amostras=30,
        largura=220,
        altura=220,
        pasta="amostras_face",
        nome="funcionario"
    )