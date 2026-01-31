from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from random import randint
from django.utils import timezone

class Funcionario(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    foto = models.ImageField(upload_to="foto/")
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=50)
    curso = models.CharField(max_length=100)
    aula = models.CharField(max_length=100)
    matricula = models.CharField(max_length=50)

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        seq = self.nome + '_FUNC' + str(randint(1000000, 9999999))
        self.slug = slugify(seq)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Alunos"
        verbose_name_plural = "Alunos"

class ColetaFaces(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='funcionario_coletas')
    image = models.ImageField(upload_to='roi/')

class Treinamento(models.Model):
    modelo = models.FileField(upload_to='treinamento/')

    class Meta:
        verbose_name = "Treinamento"
        verbose_name_plural = 'Treinamentos'

    def __str__(self):
        return 'Classificador (frontalface)'
    
    def clean(self):
        model = self.__class__
        if model.objects.exclude(id=self.id).exists:
            raise ValidationError('Só pode haver um arquivo salvo.')
    
class RegistroFuncionario(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro Alunos"
        verbose_name_plural = 'Registro Alunos'

    def __str__(self):
        # Formata para DD/MM/YYYY HH:MM
        data_local = timezone.localtime(self.data_hora)
        data_formatada = data_local.strftime("%d/%m/%Y %H:%M")
        return f"{self.funcionario.nome} - {data_formatada}"