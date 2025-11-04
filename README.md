1.Sistema OdontoPRO:
Este sistema faz parte do Projeto Integrador do curso técnico de Desenvolvimento de Sistemas e tem como objetivo o desenvolvimento de um sistema de gerenciamento e consultas para clínicas odontológicas. O sistema permitirá o cadastro de pacientes, agendamentos de consultas, controle de históricos médicos e outros recursos relacionados ao gerenciamento de uma clínica odontológica.

2.Tecnologias Utilizadas:
O projeto utiliza uma série de tecnologias modernas e ferramentas que tornam o desenvolvimento e a manutenção do sistema mais eficientes. As tecnologias utilizadas são:

Linguagens de Programação:
- Python
- JavaScript
- HTML
- CSS

Banco de Dados:
- MySQL Workbench

Design, Prototipação e Documentação:
- Canva
- Figma

Frameworks:
- Django (Backend)
- React (Frontend - Fase futura, para desenvolvimento mobile)

3.Como Clonar o Repositório:

- Para clonar o repositório e começar a trabalhar no projeto localmente, siga os passos abaixo:

I.Abra o terminal (ou o Git Bash, se estiver usando Windows).
II.Clone o repositório usando o comando:
git clone https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
(Substitua SEU_USUARIO e NOME_DO_REPOSITORIO pelo seu nome de usuário do GitHub e o nome do repositório, respectivamente.)

III.Entre no diretório do projeto:
cd NOME_DO_REPOSITORIO

IV.Instale as dependências do backend (Django):
- Se ainda não tiver o Django instalado, instale-o com:
pip install django
- Para instalar as dependências do projeto, use:
pip install -r requirements.txt

V.Configure o banco de dados:
Certifique-se de ter o MySQL Workbench instalado e configurado.
Crie um banco de dados para o projeto e configure o arquivo settings.py do Django com suas credenciais.

VI.Rodando o servidor backend:
- No diretório do projeto, execute o comando:
python manage.py runserver

VII.Configuração do Frontend (React - Futuro):
Para o frontend com React (quando implementado futuramente), será necessário usar o npm ou yarn para instalar as dependências e rodar o servidor de desenvolvimento.
