from rest_framework import viewsets
from registro.api.serializers import FuncionarioSerializer, TreinamentoSerializer, RegistroFuncionarioSerializer
from registro.models import Funcionario, Treinamento, RegistroFuncionario
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from registro.models import Treinamento

class FuncionarioViewSet(viewsets.ModelViewSet):
    queryset = Funcionario.objects.all()
    serializer_class = FuncionarioSerializer

class TreinamentoViewSet(viewsets.ModelViewSet):
    queryset = Treinamento.objects.all()
    serializer_class = TreinamentoSerializer

    @action(detail=False, methods=['get'])
    def download(self, request):
        try:
            treinamento = Treinamento.objects.latest('id')  # pega o último treinamento salvo
            if not treinamento.modelo:
                return Response({"error": "Nenhum modelo disponível"}, status=404)
            return FileResponse(treinamento.modelo.open(), as_attachment=True, filename='classificadorEigen.yml')
        except Treinamento.DoesNotExist:
            return Response({"error": "Treinamento não encontrado"}, status=404)

class RegistroFuncionarioViewSet(viewsets.ModelViewSet):
    queryset = RegistroFuncionario.objects.all()
    serializer_class = RegistroFuncionarioSerializer