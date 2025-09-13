from rest_framework import viewsets
from registro.api.serializers import FuncionarioSerializer, TreinamentoSerializer
from registro.models import Funcionario, Treinamento
from rest_framework.decorators import action
from django.http import FileResponse
from .serializers import TreinamentoSerializer

class FuncionarioViewSet(viewsets.ModelViewSet):
    queryset = Funcionario.objects.all()
    serializer_class = FuncionarioSerializer

    @action(detail=True, methods=['get'], url_path='download')
    def download_modelo(self, request, pk=None):
        treinamento = self.get_object()
        if not treinamento.modelo:
            return Response({"erro": "Nenhum arquivo associado"}, status=404)
        return FileResponse(treinamento.modelo.open('rb'), as_attachment=True, filename=treinamento.modelo.name)