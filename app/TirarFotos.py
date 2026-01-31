import cv2
import os
import time

# -------- CONFIGURAÇÕES --------
FOTOS_POR_POSE = 50
RESOLUCAO = (640, 480)
INTERVALO_CAPTURA = 0.1  # 100 ms entre fotos

POSES = [
    "Olhe PARA FRENTE",
    "Incline a cabeça PARA A DIREITA",
    "Incline a cabeça PARA A ESQUERDA",
    "Olhe PARA CIMA",
    "Olhe PARA BAIXO",
    "Gire um pouco o rosto para a DIREITA",
    "Gire um pouco o rosto para a ESQUERDA"
]

# -------- EXECUÇÃO --------

def coletar_fotos(nome_pessoa):
    pasta = f"dataset/{nome_pessoa}"

    if not os.path.exists(pasta):
        os.makedirs(pasta)

    cap = cv2.VideoCapture(0)
    cap.set(3, RESOLUCAO[0])
    cap.set(4, RESOLUCAO[1])

    print("\n===== COLETOR DE FOTOS DE TREINAMENTO =====")
    print(f"Pessoa: {nome_pessoa}")
    print("Pressione ENTER para iniciar...")
    input()

    contador_total = 0

    for pose in POSES:
        print(f"\n📸 Nova pose: {pose}")
        print("Posicione-se e mantenha firme... capturando em 3 segundos...")
        time.sleep(2)

        fotos_pose = 0

        while fotos_pose < FOTOS_POR_POSE:
            ret, frame = cap.read()
            if not ret:
                print("Falha ao capturar frame.")
                continue

            # Exibir instrução na tela
            texto = f"{pose} ({fotos_pose+1}/{FOTOS_POR_POSE})"
            cv2.putText(frame, texto, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.imshow("Coletor de Imagens", frame)

            # Salva imagem
            if not os.path.exists(pasta):
                os.makedirs(pasta)

            # dentro do loop, antes de cv2.imwrite
            caminho_foto = os.path.join(pasta, f"{nome_pessoa}_{contador_total}.jpg")
            print("Salvando em:", caminho_foto)
            ok = cv2.imwrite(caminho_foto, frame)
            if not ok:
                print("ERRO: falha ao salvar", caminho_foto)

            fotos_pose += 1
            contador_total += 1

            cv2.waitKey(int(INTERVALO_CAPTURA * 1000))

        print(f"✔ Pose concluída: {pose}")

    print(f"\n===== COLETA FINALIZADA =====")
    print(f"Total de imagens capturadas: {contador_total}")

    cap.release()
    cv2.destroyAllWindows()


# -------- INÍCIO --------

if __name__ == "__main__":
    nome = input("Digite o NOME da pessoa para o dataset: ")
    coletar_fotos(nome)