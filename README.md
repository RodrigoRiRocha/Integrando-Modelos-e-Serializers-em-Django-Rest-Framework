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

## Docker Networking (exercicio EBAC)

### Principais tipos de rede

| Driver/modo | Uso principal | Observacoes |
| --- | --- | --- |
| `bridge` | Containers no mesmo Docker Engine | Rede isolada do host, DNS por nome de servico e portas publicadas quando necessario. |
| `host` | Compartilhar a rede do host | Sem isolamento de rede; `ports` nao se aplica. Nativo no Linux; no Docker Desktop 4.34+ exige habilitacao e tem limitacoes. |
| `none` | Container sem acesso a rede | Apenas loopback; inadequado para a API que depende do banco. |
| `overlay` | Comunicacao entre hosts Docker | Requer Docker Swarm; usado em aplicacoes distribuidas. |
| `macvlan` | Container com MAC proprio na rede fisica | Exige configuracao da rede e suporte do ambiente; nao funciona no Docker Desktop Windows/macOS. |
| `ipvlan` | Containers com IPs proprios compartilhando o MAC da interface pai | Usado em integracoes avancadas de rede Linux; nao necessario neste projeto. |

`host` e `none` sao modos de rede configurados com `network_mode` no Compose.
Os demais sao drivers. A tabela compara as alternativas; este exercicio
implementa **bridge**, adequada para API e PostgreSQL no mesmo host.

### Rede bridge explicita no Compose

O arquivo `compose.yaml` declara a rede `bookstore_network` com `driver: bridge`.
Os servicos `web` e `db` entram explicitamente nessa rede; nao dependemos da rede
`default` implicita do Compose. Nao e necessario executar `docker network create`:
o proprio Compose cria e gerencia a rede ao subir os servicos.

```text
Host: localhost:8000
  |
  | porta publicada 8000:8000
  v
web:8000 ---- bookstore_network (bridge) ---- db:5432
      DNS: db -> IP do banco
```

O Compose adiciona o nome do projeto ao recurso, por exemplo
`bookstore_bookstore_network` quando usamos `-p bookstore`. Isso evita colisao
com outras execucoes. O Django usa `POSTGRES_HOST=db` e a porta interna `5432`:
o DNS da bridge resolve o nome do servico, sem IP fixo e sem usar `localhost`
para acessar outro container. Apenas a API publica a porta `8000` no host;
o PostgreSQL nao publica portas. A bridge permite saida de rede por padrao,
mas nao substitui autenticacao, firewall ou criptografia.

### Execucao e verificacao

Prepare o `.env` conforme a secao Docker e execute os comandos abaixo sempre
com o mesmo nome de projeto. `config --quiet` valida sem imprimir a senha.

```powershell
docker compose -p bookstore config --quiet
docker compose -p bookstore up --build -d
docker compose -p bookstore ps
docker network ls --filter label=com.docker.compose.project=bookstore
docker network inspect bookstore_bookstore_network --format '{{.Driver}}'
docker network inspect bookstore_bookstore_network --format '{{json .Containers}}'
```

O driver deve ser `bridge`, e a lista de containers deve conter `web` e `db`.
Confira tambem o DNS e uma consulta real ao PostgreSQL a partir da API:

```powershell
docker compose -p bookstore exec web poetry run python -c "import socket; print(socket.gethostbyname('db'))"
docker compose -p bookstore exec web poetry run python manage.py shell -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('SELECT 1'); print(cursor.fetchone()); cursor.close()"
docker compose -p bookstore exec web poetry run python manage.py test
curl.exe -i http://localhost:8000/api/categories/
```

Resultados esperados: um IP interno para `db`, `(1,)` na consulta SQL, testes
aprovados e HTTP `200` com a listagem paginada na configuracao atual.
Se permissoes de autenticacao forem exigidas, uma resposta `401` sem token
tambem comprova que a API esta acessivel pela porta publicada.
Se algo falhar, consulte `docker compose -p bookstore logs web db`.
Para evidenciar a entrega, registre a saida do driver, os dois containers
conectados, a resolucao DNS e a consulta SQL; nunca inclua o `.env` ou senhas.

```powershell
docker compose -p bookstore down
docker network ls --filter label=com.docker.compose.project=bookstore
```

O `down` remove os containers e a rede criada pelo Compose, mas preserva o
volume do PostgreSQL. Nao use `--volumes` se quiser manter os dados.

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
