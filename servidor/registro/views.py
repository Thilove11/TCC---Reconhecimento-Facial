import cv2
import os
from django.shortcuts import render, redirect
from .forms import FuncionarioForm, ColetaFacesForm
from .models import Funcionario, ColetaFaces
from django.http import StreamingHttpResponse
from registro.camera import VideoCamera

camera_detection = VideoCamera()

def gen_detect_face(camera_detection):
    while True:
        frame = camera_detection.detect_face()
        if frame is None:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def face_detection(request):
    return StreamingHttpResponse(gen_detect_face(camera_detection), content_type='multipart/x-mixed-replace; boundary=frame')

def criar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES)
        if form.is_valid():
            funcionario = form.save()
            return redirect('criar_coleta_faces', funcionario_id=funcionario.id)
    else:
        form = FuncionarioForm()
    return render(request, 'criar_funcionario.html', {'form': form})

def extract(camera_detection, funcionario_slug):
    amostra = 0
    numeroAmostras = 30
    largura, altura = 220, 220
    file_paths = []

    while amostra < numeroAmostras:
        ret, frame = camera_detection.get_camera()
        crop = camera_detection.sample_faces(frame)

        if crop is not None:
            amostra += 1

            face = cv2.resize(crop, (largura, altura))
            imagemCinza = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            file_name_path = f'./tmp/{funcionario_slug}_{amostra}.jpg'
            print(file_name_path)

            cv2.imwrite(file_name_path, imagemCinza)
            file_paths.append(file_name_path)
        else:
            print("Face não encontrada")

        if amostra >= numeroAmostras:
            break

    camera_detection.restart()
    return file_paths

def face_extract(context, funcionario):
    num_coletas = ColetaFaces.objects.filter(funcionario__slug=funcionario.slug).count()

    print(num_coletas)
    if num_coletas >= 30:
        context['erro'] = 'Limite máximo de coletas atingido.'
    else:
        file_paths = extract(camera_detection, funcionario.slug)
        print(file_paths)

        for path in file_paths:
            coleta_face = ColetaFaces.objects.create(funcionario=funcionario)
            coleta_face.image.save(os.path.basename(path), open(path, 'rb'))
            os.remove(path)

        context['file_paths'] = ColetaFaces.objects.filter(funcionario__slug=funcionario.slug)
        context['extracao_ok'] = True

    return context

def criar_coleta_faces(request, funcionario_id):
    print(funcionario_id)
    funcionario = Funcionario.objects.get(id=funcionario_id)

    botao_clicado = request.GET.get('clicked', 'False') == 'True'
    context = {
        'funcionario': funcionario,
        'face_detection': face_detection,
        'valor_botao': botao_clicado,
    }

    if botao_clicado:
        print("Cliquei em Extrair Imagens!")
        context = face_extract(context, funcionario)

    return render(request, 'criar_coleta_faces.html', context)

