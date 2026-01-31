# Reconhecimento Facial (TCC de Engenharia da Computação)
Sistema de reconhecimento facial para registro de presença em instituições educacionais

Projeto de Trabalho de Conclusão de Curso (TCC) do curso de Engenharia da Computação.
Este repositório contém uma solução de reconhecimento facial para registro automático
de presença em ambientes educacionais, composta por uma aplicação cliente (Kivy/KivyMD)
e um backend Django REST API.

O que faz
- Abre a câmera no cliente Kivy e reconhece rostos usando encodings pré-treinados.
- Consulta uma API Django para obter dados do usuário reconhecido.
- Registra a presença enviando um POST para a API e apresenta um comprovante ao usuário.

Estrutura principal
- `app/` — aplicação cliente (Kivy / KivyMD) com `main.py` e recursos visuais.
- `servidor/` — backend Django com API REST e comandos de gerenciamento (treinamento, reconhecimento).
- `requirements.txt` — dependências do projeto (veja observações abaixo).

Pré-requisitos
- Windows (testado) ou Linux/Mac com suporte a Kivy e OpenCV
- Python 3.12 (o repositório inclui um wheel de `dlib` para CPython 3.12 no diretório `app/`)
- `pip` e virtualenv/venv

Passo a passo para executar (ambiente Windows)
1. Clone o repositório e entre na pasta do projeto:

   ```powershell
   cd "c:\Users\Usuario\Downloads\tcc\TCC---Reconhecimento-Facial"
   ```

2. Crie e ative um ambiente virtual (recomendado):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instale dependências principais (no root):

   ```powershell
   pip install -r requirements.txt
   ```

   Observação: se o `pip` não conseguir instalar `dlib` automaticamente, instale o wheel incluído:

   ```powershell
   pip install .\app\dlib-19.24.99-cp312-cp312-win_amd64.whl
   ```

4. Preparar o backend Django (opcional — se quiser rodar a API localmente):

   ```powershell
   cd servidor
   python manage.py migrate
   python manage.py createsuperuser   # opcional
   python manage.py runserver
   ```

   A API estará disponível por padrão em `http://127.0.0.1:8000/`.

5. Gerar/treinar encodings de rosto (se necessário):

   - Se você já tiver o arquivo `encodings.pickle`, copie/coloque ele dentro de `app/`.
   - Caso precise treinar novos encodings, existe um comando de gerenciamento em `registro/management/commands/treinamento.py`.

   Para executar o treinamento via Django (a partir da pasta `servidor`):

   ```powershell
   cd servidor
   python manage.py treinamento
   ```

   Depois do treinamento, coloque o `encodings.pickle` gerado em `app/` (ou atualize o caminho em `app/main.py`).

6. Executar a aplicação cliente Kivy:

   ```powershell
   cd ..\app
   python main.py
   ```

   - A aplicação abrirá a interface Kivy. Clique em "INICIAR RECONHECIMENTO" para abrir a câmera.
   - Centralize o rosto na ROI (área indicada) e aguarde o reconhecimento.

Notas importantes
- O `main.py` procura por `encodings.pickle` na pasta `app/`. Se não existir, a aplicação exibirá erro.
- O código do cliente faz chamadas para a API em `https://tcc-reconhecimento-facial-h8rq.onrender.com/` por padrão.
  Se estiver rodando o backend localmente, altere as URLs em `app/main.py` para `http://127.0.0.1:8000/`.
- Testado com Python 3.12 (compatibilidade com outras versões não garantida).

Contribuições e avisos
- Este projeto foi desenvolvido como TCC — qualquer uso em produção deve considerar
  aspectos de privacidade, consentimento e segurança dos dados biométricos.

Contato / Autoria
- Projeto de TCC — Engenharia da Computação

-- Fim --
