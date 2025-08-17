# Sistema de Recomendação de Filmes - Clean Architecture

Um sistema backend completo para recomendação de filmes desenvolvido em Python 3.11 com FastAPI, implementando **Clean Architecture** (Arquitetura Limpa) com separação clara de responsabilidades.

## 🏗️ Nova Arquitetura - Clean Architecture

### Princípios Implementados

- **Separação de Responsabilidades**: Cada camada tem uma responsabilidade específica
- **Inversão de Dependência**: Camadas externas dependem das internas, não o contrário
- **Independência de Frameworks**: A lógica de negócio não depende de bibliotecas externas
- **Testabilidade**: Cada camada pode ser testada independentemente
- **Flexibilidade**: Fácil substituição de componentes (banco, framework, etc.)

### Estrutura das Camadas

```
src/
├── domain/                     # 🔵 CAMADA DE DOMÍNIO
│   ├── entities/              # Entidades de negócio (User, Movie, Like)
│   ├── repositories/          # Interfaces dos repositórios
│   └── value_objects/         # Objetos de valor (Pagination, Recommendation)
│
├── application/               # 🟢 CAMADA DE APLICAÇÃO
│   ├── use_cases/            # Casos de uso (RegisterUser, LoginUser, etc.)
│   ├── services/             # Interfaces de serviços
│   └── dtos/                 # Data Transfer Objects
│
├── infrastructure/           # 🔴 CAMADA DE INFRAESTRUTURA
│   ├── database/            # Implementação de banco de dados
│   │   ├── models/         # Modelos SQLAlchemy
│   │   └── repositories/   # Implementação dos repositórios
│   ├── api/                # Camada de apresentação (FastAPI)
│   │   ├── controllers/    # Controladores REST
│   │   └── dependencies/   # Dependências do FastAPI
│   ├── external/           # Serviços externos (JWT, bcrypt, TMDB)
│   └── config/            # Configurações (settings, logging)
│
└── shared/                   # 🟡 CAMADA COMPARTILHADA
    ├── exceptions/          # Exceções customizadas
    ├── utils/              # Utilitários gerais
    └── constants/          # Constantes da aplicação
```

### Fluxo de Dependências

```
🔴 Infrastructure → 🟢 Application → 🔵 Domain
      ↓                    ↓            ↓
   FastAPI              Use Cases    Entities
   SQLAlchemy           Services     Repositories (interfaces)
   JWT/bcrypt           DTOs         Value Objects
```

### Benefícios da Nova Arquitetura

1. **Domínio Puro**: Entidades não dependem de frameworks externos
2. **Casos de Uso Claros**: Lógica de negócio bem definida e testável
3. **Flexibilidade**: Troca de banco/framework sem afetar negócio
4. **Manutenibilidade**: Código mais organizado e fácil de entender
5. **Testabilidade**: Cada camada pode ser testada isoladamente

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.11+
- PostgreSQL
- Git

### 1. Clone e Configure

```bash
git clone <repository-url>
cd backend

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações
```

### 2. Inicializar Banco de Dados

```bash
# Nova versão com Clean Architecture
python scripts/init_db_new.py
```

### 3. Executar Aplicação

```bash
# Usando script principal
python run.py

# Ou diretamente com uvicorn
uvicorn src.infrastructure.api.main:app --reload
```

A aplicação estará disponível em: http://localhost:8000

## 📖 Documentação da API

### Endpoints Implementados (Nova Arquitetura)

#### Autenticação
- `POST /api/v1/auth/register` - Registrar usuário
- `POST /api/v1/auth/login` - Login (form-data)
- `POST /api/v1/auth/login-json` - Login (JSON)

### Swagger UI
Acesse: http://localhost:8000/docs

## 🔧 Desenvolvimento

### Adicionando Novos Casos de Uso

1. **Criar Entidade** (se necessário) em `src/domain/entities/`
2. **Definir Repository Interface** em `src/domain/repositories/`
3. **Criar Use Case** em `src/application/use_cases/`
4. **Implementar Repository** em `src/infrastructure/database/repositories/`
5. **Criar Controller** em `src/infrastructure/api/controllers/`
6. **Configurar Dependencies** em `src/infrastructure/api/dependencies/`

### Exemplo: Adicionar Novo Algoritmo de Recomendação

```python
# 1. Criar interface (Application)
class RecommendationStrategy(ABC):
    @abstractmethod
    def recommend(self, user: User) -> List[Movie]:
        pass

# 2. Implementar algoritmo (Infrastructure)
class ContentBasedRecommendation(RecommendationStrategy):
    def recommend(self, user: User) -> List[Movie]:
        # Lógica do algoritmo
        pass

# 3. Registrar no container
recommendation_service.register_strategy(
    RecommendationAlgorithm.CONTENT_BASED,
    ContentBasedRecommendation()
)
```

### Testes por Camada

```bash
# Testes de domínio (sem dependências externas)
pytest tests/domain/ -v

# Testes de aplicação (mocks para infraestrutura)
pytest tests/application/ -v

# Testes de infraestrutura (integração)
pytest tests/infrastructure/ -v
```

## 🎯 Casos de Uso Implementados

### Autenticação
- ✅ **RegisterUserUseCase**: Registrar novo usuário
- ✅ **LoginUserUseCase**: Autenticar usuário

### Em Desenvolvimento
- ⏳ **GetMoviesUseCase**: Listar filmes
- ⏳ **LikeMovieUseCase**: Curtir filme
- ⏳ **GetRecommendationsUseCase**: Obter recomendações


## 🧪 Exemplo de Uso

### 1. Registrar Usuário
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "username": "usuario",
  "email": "user@example.com",
  "password": "senha123"
}'
```

### 2. Fazer Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login-json" \
-H "Content-Type: application/json" \
-d '{
  "username": "usuario",
  "password": "senha123"
}'
```

## 📚 Recursos de Estudo

### Clean Architecture
- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

### Padrões Implementados
- **Repository Pattern**: Abstração do acesso a dados
- **Use Case Pattern**: Encapsulamento da lógica de negócio
- **Dependency Injection**: Inversão de controle
- **Strategy Pattern**: Algoritmos intercambiáveis


## 🔍 Health Check

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "service": "Movie Recommendation System",
  "version": "2.0.0"
}
```

---

**Arquitetura implementada com ❤️ seguindo princípios SOLID e Clean Architecture**
