# Testes Unitários - Backend

Este diretório contém os testes unitários para as camadas de domínio e aplicação do projeto.

## Estrutura dos Testes

```
tests/
├── unit/
│   ├── domain/
│   │   └── entities/
│   │       ├── test_user.py          # Testes para entidade User
│   │       ├── test_movie.py         # Testes para entidade Movie
│   │       └── test_like.py          # Testes para entidade Like
│   └── application/
│       ├── use_cases/
│       │   ├── auth/
│       │   │   └── test_register_use_case.py  # Testes para RegisterUserUseCase
│       │   └── movies/
│       │       └── test_create_movie_use_case.py  # Testes para CreateMovieUseCase
│       └── services/
│           └── test_security_service.py  # Testes para SecurityService
└── README.md
```

## Como Executar os Testes

### Executar Todos os Testes
```bash
pytest
```

### Executar Testes por Categoria

#### Testes das Entidades (Domínio)
```bash
pytest tests/unit/domain/
```

#### Testes dos Casos de Uso (Aplicação)
```bash
pytest tests/unit/application/use_cases/
```

#### Testes dos Serviços (Aplicação)
```bash
pytest tests/unit/application/services/
```

### Executar Testes Específicos

#### Testes de uma entidade específica
```bash
pytest tests/unit/domain/entities/test_user.py
pytest tests/unit/domain/entities/test_movie.py
pytest tests/unit/domain/entities/test_like.py
```

#### Testes de um caso de uso específico
```bash
pytest tests/unit/application/use_cases/auth/test_register_use_case.py
pytest tests/unit/application/use_cases/movies/test_create_movie_use_case.py
```

#### Executar um teste específico
```bash
pytest tests/unit/domain/entities/test_user.py::TestUser::test_user_creation_with_all_fields
```

### Opções Úteis do Pytest

#### Executar com output detalhado
```bash
pytest -v
```

#### Executar com cobertura de código
```bash
pytest --cov=src --cov-report=html
```

#### Executar apenas testes marcados como unit
```bash
pytest -m unit
```

#### Executar com output em tempo real
```bash
pytest -s
```

#### Parar na primeira falha
```bash
pytest -x
```

## Descrição dos Testes

### Testes das Entidades (Domínio)

#### TestUser (`test_user.py`)
- ✅ Criação de usuário com todos os campos
- ✅ Criação de usuário com campos mínimos
- ✅ Configuração automática de timestamps
- ✅ Ativação e desativação de usuário
- ✅ Atualização de senha
- ✅ Valores padrão
- ✅ Parametrização com diferentes dados

#### TestMovie (`test_movie.py`)
- ✅ Criação de filme com todos os campos
- ✅ Criação de filme com campos mínimos
- ✅ Configuração automática de timestamps
- ✅ Conversão de genres (JSON ↔ Lista)
- ✅ Atualização de avaliações
- ✅ Extração do ano da data de lançamento
- ✅ Tratamento de dados inválidos
- ✅ Operações complexas com genres

#### TestLike (`test_like.py`)
- ✅ Criação de like com todos os campos
- ✅ Criação de like com campos mínimos
- ✅ Configuração automática de timestamp
- ✅ Testes com diferentes IDs
- ✅ Timestamps únicos
- ✅ Casos extremos (IDs zero, IDs grandes)
- ✅ Representação string

### Testes dos Casos de Uso (Aplicação)

#### TestRegisterUserUseCase (`test_register_use_case.py`)
- ✅ Registro bem-sucedido de usuário
- ✅ Validação de email já existente
- ✅ Validação de username já existente
- ✅ Hash correto da senha
- ✅ Estrutura correta do usuário criado
- ✅ Tratamento de erros do repositório
- ✅ Tratamento de erros do serviço de segurança
- ✅ Parametrização com diferentes dados

#### TestCreateMovieUseCase (`test_create_movie_use_case.py`)
- ✅ Criação bem-sucedida com todos os campos
- ✅ Criação bem-sucedida com campos mínimos
- ✅ Passagem correta para o repositório
- ✅ Testes com diferentes avaliações
- ✅ Caracteres especiais no título
- ✅ Overview longo
- ✅ Tratamento de erros do repositório
- ✅ Integração com model_dump() do Pydantic

### Testes dos Serviços (Aplicação)

#### TestSecurityServiceInterface (`test_security_service.py`)
- ✅ Verificação da interface abstrata
- ✅ Assinaturas dos métodos
- ✅ Tipos de retorno corretos
- ✅ Fluxo completo de hash e verificação de senha
- ✅ Fluxo completo de criação e verificação de token
- ✅ Rastreamento de chamadas dos métodos
- ✅ Presença de todos os métodos abstratos

## Configuração do Pytest

O arquivo `pytest.ini` na raiz do projeto contém as configurações:

- **testpaths**: `tests` - diretório dos testes
- **python_files**: `test_*.py` - padrão dos arquivos de teste
- **python_classes**: `Test*` - padrão das classes de teste
- **python_functions**: `test_*` - padrão das funções de teste
- **addopts**: `-v --tb=short --strict-markers` - opções padrão

## Markers Personalizados

- `@pytest.mark.unit` - marca testes unitários
- `@pytest.mark.integration` - marca testes de integração
- `@pytest.mark.slow` - marca testes que demoram para executar

## Dependências para Testes

As dependências necessárias já estão incluídas no `requirements.txt`:
- `pytest==7.4.3` - framework de testes
- `pytest-asyncio==0.21.1` - suporte para testes assíncronos

## Boas Práticas

1. **Nomenclatura**: Use nomes descritivos para os testes
2. **Organização**: Siga a estrutura AAA (Arrange, Act, Assert)
3. **Isolamento**: Cada teste deve ser independente
4. **Mocking**: Use mocks para dependências externas
5. **Parametrização**: Use `@pytest.mark.parametrize` para testes similares
6. **Cobertura**: Mantenha alta cobertura de código

## Próximos Passos

Para expandir a suíte de testes, considere:

1. Adicionar testes de integração
2. Implementar testes para outros casos de uso
3. Adicionar testes para a camada de infraestrutura
4. Configurar CI/CD para execução automática dos testes
5. Implementar testes de performance
6. Adicionar testes de contrato para APIs
