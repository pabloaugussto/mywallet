💰 MyWallet - Controle Financeiro Pessoal
Aplicação web desenvolvida em Python/Django para gestão financeira pessoal. O sistema permite o lançamento de despesas e receitas, conversão automática de moedas (Dólar para Real) e visualização de dados através de dashboards interativos.

Projetado para rodar localmente com rotinas de backup automático na nuvem.

📸 Screenshots
<img width="1918" height="890" alt="image" src="https://github.com/user-attachments/assets/3f9ca042-6869-427d-b7de-90a2ea53c779" />

✨ Funcionalidades
📊 Dashboard Interativo: Visão geral de Entradas, Saídas e Saldo Global.

📉 Gráficos Dinâmicos: Gráfico de rosca (Chart.js) detalhando despesas por categoria.

📅 Filtro Temporal: Filtragem de transações por Mês e Ano.

💲 Multi-moeda Inteligente: Suporte a transações em BRL e USD. O sistema consulta a cotação do dia (via API) e converte automaticamente para Reais nos relatórios.

🔒 Segurança: Acesso restrito via login obrigatório.

☁️ Backup Automático: Script personalizado (.bat) que realiza backup do banco de dados no Google Drive antes e depois do uso.

🔔 Feedback Visual: Mensagens de confirmação (Toasts) para ações de criar, editar e excluir.

🛠️ Tecnologias Utilizadas
Back-end: Python 3, Django 5.

Front-end: HTML5, CSS3, Bootstrap 5.

JavaScript: Chart.js (Gráficos), Scripts de interação.

Banco de Dados: SQLite3.

Automação: Batch Script (Windows) para inicialização e backup.

🚀 Como rodar o projeto
Pré-requisitos
Antes de começar, você vai precisar ter instalado em sua máquina:

Python 3.x

Git

Passo a passo
Clone o repositório

Bash

git clone https://github.com/seu-usuario/mywallet.git
cd mywallet
Crie e ative o ambiente virtual

Bash

# No Windows
python -m venv venv
venv\Scripts\activate
Instale as dependências

Bash

pip install -r requirements.txt
Realize as migrações do banco de dados

Bash

python manage.py migrate
Crie um superusuário (para acessar o sistema)

Bash

python manage.py createsuperuser
Inicie o servidor

Bash

python manage.py runserver
Acesse http://127.0.0.1:8000/ no seu navegador.

🦇 Automação (Windows)
O projeto inclui um arquivo MyWallet.bat na raiz. Este executável facilita o uso diário:

Realiza backup do db.sqlite3 para uma pasta configurada (ex: Google Drive).

Ativa o ambiente virtual.

Inicia o servidor Django.

Abre o navegador automaticamente.

📝 Licença
Este projeto está sob a licença MIT.

Feito por Pablo Augusto. 👋
