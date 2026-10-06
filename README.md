# Bookstore API

Projeto do módulo "Integrando Modelos e Serializers em Django Rest Framework" da EBAC.
A API expõe as entidades `Category`, `Product` e `Order` com seus respectivos serializers
e testes automatizados.

As dependências são gerenciadas com **Poetry**, usando `pyproject.toml` e `poetry.lock`
para instalações reproduzíveis.

## Requisitos

- Python 3.13+
- [Poetry](https://python-poetry.org/docs/#installation) 2.x

## Instalação

```powershell
poetry install
```

## Execução

```powershell
poetry run python manage.py migrate
poetry run python manage.py runserver
```

A API fica disponível em `http://127.0.0.1:8000/`.

## Docker

Com Docker Engine e o plugin Docker Compose instalados, copie `.env.example` para
`.env` na raiz do projeto e defina uma senha local exclusiva em
`POSTGRES_PASSWORD` (não versione o arquivo `.env`). `POSTGRES_DB` e
`POSTGRES_USER` já usam `bookstore` como padrão. Depois, inicie a API com:

```powershell
Copy-Item .env.example .env
```

```bash
docker compose up --build
```

O serviço web aguarda o PostgreSQL ficar saudável antes de aplicar as migrações.
A API fica disponível em `http://localhost:8000/`, e o banco PostgreSQL 17
persiste no volume `postgres_data`. O banco não expõe sua porta no host.
Para parar os containers, use `docker compose down`. Para também apagar o banco,
use `docker compose down --volumes`.

Fora do Docker, a aplicação continua usando SQLite por padrão. Para conectar a
um PostgreSQL externo, defina `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`,
`POSTGRES_PASSWORD` e, opcionalmente, `POSTGRES_PORT` (padrão: `5432`).
Os dados do SQLite existente não são transferidos automaticamente; o volume
antigo `bookstore_data` e o arquivo `db.sqlite3` não são apagados pela mudança.

Para executar os testes com PostgreSQL:

```bash
docker compose run --rm web poetry run python manage.py test
```

As listagens da API usam paginação por número de página, com até dois registros por página.
Use `?page=2` para navegar e `?page_size=N` para solicitar outro tamanho de página,
limitado a 100 registros por página.
As respostas de listagem possuem os campos `count`, `next`, `previous` e `results`.

## Autenticação

Todos os endpoints da API exigem autenticação via **Token Authentication** do
Django REST Framework. Crie um usuário e obtenha um token em `api/auth/token/`:

```powershell
poetry run python manage.py createsuperuser
```

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -d "username=<usuario>&password=<senha>"
```

A resposta traz `{"token": "<token>"}`. Use o token no cabeçalho `Authorization`
em todas as demais requisições:

```bash
curl http://127.0.0.1:8000/api/categories/ \
  -H "Authorization: Token <token>"
```

Requisições sem um token válido recebem `401 Unauthorized`.

## Testes

```powershell
poetry run pytest -q
```

Também é possível executar a suíte pelo runner do Django:

```powershell
poetry run python manage.py test
```

## Estrutura

```text
bookstore/     configuração do projeto Django
categories/    modelo, serializer e testes de Category
products/      modelo, serializer e testes de Product (inclui Category aninhada)
orders/        modelo, serializer e testes de Order
```