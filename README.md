# Bookstore API

Projeto do módulo "Integrando Modelos e Serializers em Django REST Framework" da EBAC.
A API expõe as entidades `Category`, `Product` e `Order` com seus respectivos serializers
e testes automatizados.

As dependências são gerenciadas com **Poetry**, garantindo builds reproduzíveis
(`pyproject.toml` + `poetry.lock`) em qualquer máquina ou contêiner.

## Requisitos

- Python 3.13+
- [Poetry](https://python-poetry.org/docs/#installation) 2.x

## Instalação

```powershell
poetry install
```

O comando cria o ambiente virtual e instala exatamente as versões registradas em `poetry.lock`.

## Execução

```powershell
poetry run python manage.py migrate
poetry run python manage.py runserver
```

A API fica disponível em `http://127.0.0.1:8000/`.

## Testes

```powershell
poetry run python manage.py test
```

## Comandos úteis do Poetry

| Comando | Descrição |
| --- | --- |
| `poetry install` | Instala as dependências a partir do `poetry.lock`. |
| `poetry add <pacote>` | Adiciona uma dependência e atualiza o lock. |
| `poetry lock` | Regera o `poetry.lock` após alterar o `pyproject.toml`. |
| `poetry show --tree` | Exibe a árvore de dependências resolvidas. |
| `poetry run <comando>` | Executa um comando dentro do ambiente virtual. |
| `poetry env info` | Mostra o ambiente virtual em uso. |

## Estrutura

```text
bookstore/     configuração do projeto Django
categories/    modelo, serializer e testes de Category
products/      modelo, serializer e testes de Product (inclui Category aninhada)
orders/        modelo, serializer e testes de Order
```
