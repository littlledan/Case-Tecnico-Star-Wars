# Star Wars Explorer - Serverless API & Frontend

Solução de Back End desenvolvida em Python para o desafio técnico da **PowerOfData**. O projeto implementa uma arquitetura Serverless sobre **Google Cloud Functions**, gerenciada via **API Gateway** e consumindo a SWAPI.

---

## 🏗️ Arquitetura da Solução

O diagrama abaixo ilustra o fluxo de dados e os componentes da arquitetura proposta:

```mermaid
graph LR
    User[Usuário / Streamlit] -- "GET /?category=films&expand=characters" --> Gateway[GCP API Gateway]
    Gateway -- "Roteamento" --> CloudFunc[Cloud Run Function]
    
    subgraph Google Cloud Platform
        Gateway
        CloudFunc
    end
    
    CloudFunc -- "Request (requests lib)" --> SWAPI[Star Wars API Externa]
    SWAPI -- "JSON Data" --> CloudFunc
    CloudFunc -- "Processamento Paralelo & Ordenação" --> Gateway
    Gateway -- "JSON Enriquecido" --> User
    
    style User fill:#f9f,stroke:#333,stroke-width:2px
    style SWAPI fill:#bbf,stroke:#333,stroke-width:2px
    style CloudFunc fill:#dfd,stroke:#333,stroke-width:2px

Tecnologias Utilizadas
Linguagem: Python 3.10+

Framework Serverless: Google Functions Framework

Concorrência: concurrent.futures

Testes: Pytest & Mock

Interface: Streamlit (para validação visual)

Nota sobre o Deploy
O código foi desenvolvido e testado localmente utilizando o emulador oficial do Google (functions-framework), garantindo compatibilidade total com o ambiente de Cloud. Devido a restrições de faturamento na conta pessoal do GCP (bloqueio regional), o deploy em produção foi simulado localmente. Os arquivos de infraestrutura (openapi.yaml) estão inclusos para demonstrar o provisionamento.

Como executar o projeto
1. Instalação
Bash
python -m venv venv
# Ative a venv
pip install -r requirements.txt
2. Executar Back End (Simulação Cloud)
Bash
functions-framework --target=starwars_search --debug
3. Executar Front End (Interface de Teste)
Em um novo terminal (com a venv ativa):
Bash
streamlit run frontend.py
O navegador abrirá automaticamente em http://localhost:8501.
4. Executar Testes Unitários
Bash
pytest