# 🚀 Job Agent System - Sistema Completo de Búsqueda de Empleo con IA

Un sistema completo y moderno de búsqueda de empleo inteligente que combina FastAPI, ReactJS, LangGraph y MCP para proporcionar una experiencia excepcional en la búsqueda de trabajo.

## 📋 Resumen del Proyecto

Este sistema implementa un agente inteligente de búsqueda de empleo que puede:

- 🔍 **Analizar CVs** automáticamente usando IA
- 🎯 **Buscar ofertas** en múltiples plataformas (LinkedIn, Indeed, Glassdoor)
- 🤖 **Matching inteligente** entre CVs y ofertas usando LangGraph
- 📚 **Generar recomendaciones** personalizadas de formación
- 🔗 **Integrar herramientas externas** mediante MCP (Model Context Protocol)
- 📊 **Dashboard moderno** con ReactJS y Tailwind CSS

## 🏗️ Arquitectura

```
job-agent-system/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # Rutas API
│   │   ├── agents/            # Agentes LangGraph
│   │   ├── core/              # Configuración core
│   │   ├── models/            # Modelos de datos
│   │   ├── services/          # Lógica de negocio
│   │   ├── mcp/               # MCP Tools
│   │   └── utils/             # Utilidades
│   ├── tests/                 # Tests
│   ├── migrations/            # Migraciones DB
│   └── scripts/               # Scripts
├── frontend/                  # ReactJS Frontend
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   ├── pages/             # Páginas
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API services
│   │   ├── store/             # Estado global
│   │   ├── utils/             # Utilidades
│   │   └── types/             # Tipos TypeScript
│   ├── public/                # Archivos estáticos
│   └── tests/                 # Tests
├── docker/                    # Configuración Docker
├── docs/                      # Documentación
└── README.md                  # Este archivo
```

## 🛠️ Tecnologías Implementadas

### Backend (FastAPI)
- **FastAPI**: Framework web de alto rendimiento
- **LangGraph**: Orquestación de agentes AI con flujos complejos
- **MCP (Model Context Protocol)**: Integración con herramientas externas
- **PostgreSQL**: Base de datos principal con migraciones
- **Redis**: Caching y colas para tareas asíncronas
- **Celery**: Sistema de tareas en segundo plano
- **Pydantic**: Validación de datos con tipos estáticos
- **SQLAlchemy**: ORM para base de datos
- **JWT**: Autenticación y autorización
- **OpenAI**: Modelos de lenguaje para análisis
- **Alembic**: Migraciones de base de datos

### Frontend (ReactJS)
- **React 18**: Librería frontend moderna
- **Vite**: Build tool rápido y optimizado
- **TypeScript**: Tipado estático completo
- **Tailwind CSS**: Framework CSS utility-first
- **Zustand**: Manejo de estado global ligero
- **React Router**: Navegación SPA
- **React Query**: Manejo de estado asíncrono
- **React Hook Form**: Formularios optimizados
- **Zod**: Validación de esquemas
- **Radix UI**: Componentes accesibles
- **Axios**: Cliente HTTP

### DevOps & Deployment
- **Docker**: Contenerización completa
- **Docker Compose**: Orquestación local
- **Nginx**: Reverse proxy y serving estático
- **PostgreSQL**: Base de datos principal
- **Redis**: Caching y colas
- **Prometheus**: Métricas y monitoring
- **Grafana**: Dashboards de monitoreo
- **Flower**: Monitoreo de Celery

## 🚀 Características Principales

### 🤖 Agentes Inteligentes (LangGraph)

El sistema implementa múltiples agentes AI especializados:

1. **CV Analysis Agent**: Análisis automático de currículums
   - Extracción de texto de PDF/DOCX
   - Análisis de habilidades y experiencia
   - Clasificación por categorías
   - Detección de fortalezas y áreas de mejora

2. **Job Search Agent**: Búsqueda inteligente de ofertas
   - Búsqueda multi-fuente (LinkedIn, Indeed, Glassdoor)
   - Filtrado avanzado por ubicación, tipo, experiencia
   - Análisis de requisitos de cada puesto
   - Clasificación por relevancia

3. **Matching Agent**: Matching CV-Ofertas
   - Algoritmos de matching avanzados
   - Puntuación de compatibilidad 0-100%
   - Análisis de gaps de habilidades
   - Recomendaciones personalizadas

4. **Recommendation Agent**: Recomendaciones de formación
   - Análisis de gaps de habilidades
   - Sugerencias de cursos y recursos
   - Planes de aprendizaje personalizados
   - Seguimiento de progreso

### 🔗 MCP Integration

El sistema implementa MCP (Model Context Protocol) para integración con herramientas externas:

- **LinkedIn Jobs Tool**: Búsqueda en LinkedIn
- **Indeed Jobs Tool**: Búsqueda en Indeed
- **Glassdoor Jobs Tool**: Búsqueda en Glassdoor con ratings
- **Aggregate Jobs Tool**: Búsqueda agregada multi-fuente
- **Company Research Tool**: Investigación de empresas

### 📊 Dashboard Moderno

Interfaz de usuario completa con:
- **Análisis de CVs**: Visualización de habilidades y experiencia
- **Búsqueda de Ofertas**: Filtros avanzados y resultados en tiempo real
- **Matches**: Visualización de compatibilidad con ofertas
- **Recomendaciones**: Planes de aprendizaje personalizados
- **Progreso**: Seguimiento de desarrollo profesional

### 🔄 Sistema Asíncrono

Tareas en segundo plano con Celery:
- **Procesamiento de CVs**: Análisis sin bloquear la UI
- **Búsqueda de ofertas**: Búsquedas largas en background
- **Matching**: Cálculos complejos de compatibilidad
- **Notificaciones**: Email y notificaciones en tiempo real
- **Sincronización**: Actualización periódica de datos

## 🛠️ Instalación y Configuración

### Requisitos Previos

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Configuración del Entorno

1. **Clonar el repositorio**
   ```bash
   git clone (https://github.com/LeoR22/job-agent-system.git)
   cd job-agent-system
   ```

2. **Configurar variables de entorno**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   
   # Frontend
   cp frontend/.env.example frontend/.env
   ```

3. **Configurar variables clave**
   ```bash
   # Backend (.env)
   DATABASE_URL=postgresql://user:password@localhost:5432/job_agent_db
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=tu-secret-key-seguro
   OPENAI_API_KEY=tu-api-key-de-openai
   
   # Frontend (.env)
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   VITE_ENABLE_DEBUG=true
   ```

### Desarrollo Local

#### Opción 1: Docker Compose (Recomendado)

```bash
# Entorno de desarrollo
docker-compose -f docker-compose.dev.yml up -d

# Acceder a las aplicaciones
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Flower: http://localhost:5555
```

#### Opción 2: Manual

**Backend:**
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Celery Worker (en otra terminal):**
```bash
cd backend
celery -A app.core.celery worker --loglevel=info
```

### Producción

```bash
# Construir y levantar todos los servicios
docker-compose up -d

# Incluir servicios de monitoreo
docker-compose --profile monitoring up -d
```

## 📚 Uso del Sistema

### 1. Registro y Login

1. Crear cuenta en `/register`
2. Iniciar sesión en `/login`
3. Acceder al dashboard principal

### 2. Subir CV

1. Ir a `/cv/upload`
2. Arrastrar o seleccionar archivo PDF/DOCX
3. El sistema analizará automáticamente:
   - Extraer texto y estructura
   - Identificar habilidades y experiencia
   - Generar perfil profesional

### 3. Buscar Ofertas

1. Ir a `/jobs/search`
2. Ingresar palabras clave
3. Aplicar filtros (ubicación, tipo, experiencia)
4. El sistema buscará en múltiples fuentes:
   - LinkedIn
   - Indeed
   - Glassdoor

### 4. Ver Matches

1. Ir a `/jobs/matches`
2. Ver ofertas con mayor compatibilidad
3. Analizar gaps de habilidades
4. Recibir recomendaciones

### 5. Recomendaciones

1. Ir a `/recommendations`
2. Ver habilidades sugeridas
3. Acceder a recursos de aprendizaje
4. Seguir progreso de desarrollo

## 🔧 Endpoints API Principales

### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/register` - Registrar usuario
- `GET /api/v1/auth/me` - Obtener usuario actual
- `POST /api/v1/auth/refresh` - Refrescar token

### CVs
- `POST /api/v1/cvs/upload` - Subir y analizar CV
- `GET /api/v1/cvs/` - Listar CVs del usuario
- `GET /api/v1/cvs/{id}` - Obtener CV específico
- `PUT /api/v1/cvs/{id}/activate` - Activar CV
- `DELETE /api/v1/cvs/{id}` - Eliminar CV

### Búsqueda de Empleo
- `POST /api/v1/jobs/search` - Buscar ofertas
- `GET /api/v1/jobs/{id}` - Obtener oferta específica
- `GET /api/v1/jobs/matches` - Obtener matches

### Recomendaciones
- `GET /api/v1/recommendations/skills` - Obtener recomendaciones
- `POST /api/v1/recommendations/generate` - Generar nuevas recomendaciones

### Agentes (LangGraph)
- `POST /api/v1/agents/match` - Ejecutar matching
- `POST /api/v1/agents/analyze-cv` - Analizar CV
- `POST /api/v1/agents/search-jobs` - Buscar ofertas

### MCP Tools
- `GET /api/v1/mcp` - Listar herramientas disponibles
- `POST /api/v1/mcp/search` - Ejecutar búsqueda MCP

## 🐳 Docker y Deployment

### Estructura de Contenedores

```yaml
Servicios principales:
├── postgres        # Base de datos
├── redis           # Cache y colas
├── backend         # FastAPI application
├── frontend        # ReactJS build
├── celery-worker   # Tareas en background
├── celery-beat     # Programador de tareas
└── nginx           # Reverse proxy (producción)

Servicios de monitoreo:
├── flower          # Interfaz de Celery
├── prometheus      # Métricas
└── grafana         # Dashboards
```

### Comandos Docker

```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml up -d

# Producción
docker-compose up -d

# Monitoreo
docker-compose --profile monitoring up -d

# Ver logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Limpiar
docker-compose down -v
```

## 📈 Monitoreo y Métricas

### Métricas Disponibles

- **Health Checks**: `/health`
- **Prometheus Metrics**: `/metrics`
- **Celery Monitoring**: `http://localhost:5555`
- **Grafana Dashboards**: `http://localhost:3001`

### Alertas y Notificaciones

- **Error Tracking**: Integración con Sentry
- **Performance Monitoring**: Métricas en tiempo real
- **Health Checks**: Monitoreo de servicios
- **Log Aggregation**: Logs estructurados

## 🔒 Seguridad

### Implementaciones de Seguridad

- **Autenticación JWT**: Tokens firmados con expiración
- **Password Hashing**: bcrypt para almacenamiento seguro
- **CORS**: Configuración restrictiva de orígenes
- **Rate Limiting**: Límites de solicitud por IP
- **Input Validation**: Validación con Pydantic y Zod
- **SQL Injection Protection**: SQLAlchemy ORM
- **XSS Protection**: Sanitización de inputs
- **HTTPS**: SSL/TLS en producción

### Mejores Prácticas

- Variables de entorno para datos sensibles
- Rotación de claves periódica
- Validación de inputs en todos los endpoints
- Rate limiting en endpoints críticos
- Logs estructurados para auditoría
- Backups automáticos de base de datos

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest --cov=app tests/
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:ui
```

### Integration Tests

```bash
# Test de integración con Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📝 Documentación

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Arquitectura
- Diagramas de secuencia de LangGraph
- Diagramas de base de datos
- Diagramas de despliegue

### Guías de Desarrollo
- Guía de contribución
- Estándares de código
- Proceso de review

## 🚀 Deployment

### Entornos

- **Development**: `docker-compose.dev.yml`
- **Staging**: `docker-compose.staging.yml`
- **Production**: `docker-compose.yml`

### CI/CD Pipeline

El proyecto incluye una configuración completa de CI/CD con GitHub Actions:

#### 🔧 Flujo Automatizado

1. **Trigger**: Push a `main`/`develop` o Pull Request
2. **Linting & Testing**: 
   - Backend: Black, isort, flake8, mypy, pytest
   - Frontend: ESLint, TypeScript, Vitest
3. **Security Scan**: Trivy vulnerability scanner
4. **Build & Push**: Docker images multi-architecture
5. **Deploy**: Automático a staging/producción
6. **Monitor**: Health checks y notificaciones

#### 📋 Archivos de Configuración

- **GitHub Actions**: `.github/workflows/ci-cd.yml`
- **Docker Compose**: `docker-compose.yml`, `docker-compose.staging.yml`
- **Deployment Script**: `scripts/deploy.sh`
- **Environment Files**: `.env.production`, `.env.staging`

#### 🚀 Comandos de Despliegue

```bash
# Despliegue manual con script
./scripts/deploy.sh staging
./scripts/deploy.sh production

# Health checks
./scripts/deploy.sh health-check staging

# Backup
./scripts/deploy.sh backup production

# Rollback
./scripts/deploy.sh rollback production
```

#### 📊 Monitoreo en CI/CD

- **Métricas**: Prometheus + Grafana
- **Logs**: Structured logging con ELK stack
- **Alertas**: Slack notifications
- **Health Checks**: Endpoints automáticos
- **Performance**: Tiempos de despliegue y respuesta

#### 🔒 Seguridad en CI/CD

- **Secrets Management**: GitHub Secrets
- **Image Scanning**: Trivy security scans
- **Vulnerability Assessment**: Dependabot alerts
- **Code Signing**: Imágenes firmadas
- **Access Control**: RBAC en deployments

#### 🔄 Entornos Soportados

| Entorno | Trigger | Auto-deploy | Monitoreo | Rollback |
|----------|---------|-------------|-----------|----------|
| Staging | `develop` | ✅ | ✅ | ✅ |
| Production | `main` | ✅ | ✅ | ✅ |
| Feature | PR | ❌ | ❌ | ❌ |

#### 📈 Métricas de CI/CD

- **Build Time**: < 5 minutos
- **Test Coverage**: > 80%
- **Security Score**: A (Trivy)
- **Deployment Success**: > 95%
- **Rollback Time**: < 2 minutos

### Escalabilidad

- **Horizontal Scaling**: Múltiples instancias de backend/frontend
- **Load Balancing**: Nginx como balanceador
- **Database**: PostgreSQL con connection pooling
- **Cache**: Redis cluster para alto tráfico
- **Queue**: Celery con múltiples workers

## 🤝 Contribución

### Flujo de Trabajo

1. **Fork** el repositorio
2. **Branch**: Crear rama feature/`nombre-feature`
3. **Desarrollar**: Implementar cambios con tests
4. **Test**: Ejecutar tests locales
5. **Commit**: Commits atómicos y descriptivos
6. **Push**: Subir cambios al fork
7. **PR**: Crear Pull Request con descripción detallada
8. **Review**: Esperar revisión y hacer cambios solicitados
9. **Merge**: Integrar a main

### Estándares de Código

- **Python**: PEP 8, type hints, docstrings
- **TypeScript**: ESLint, Prettier, strict mode
- **React**: Hooks, functional components
- **FastAPI**: Pydantic models, dependency injection
- **SQL**: SQLAlchemy ORM, migraciones con Alembic

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- **OpenAI** Por los modelos de lenguaje GPT
- **LangChain** Por el framework de agentes
- **FastAPI** Por el excelente framework web
- **React** Por la librería frontend
- **Docker** Por la plataforma de contenerización
- **PostgreSQL** Por la base de datos robusta

## 📞 Contacto

- **Issues**: GitHub Issues
- **Email**: soporte@jobagent-system.com
- **Discord**: [Servidor de comunidad](https://discord.gg/jobagent)

---

🎉 **¡Gracias por usar Job Agent System!** 🎉
