# 🏋️‍♂️ GymFlow Analytics

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15+-000000?style=for-the-badge&logo=next.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

Plataforma SaaS para la gestión y analítica integral de gimnasios, diseñada especialmente para adaptarse a la dinámica socioeconómica de **Maracaibo, Zulia (Venezuela)**. 

GymFlow Analytics permite el control de acceso en tiempo real, normalización de ingresos multidivisa a USD, persistencia resiliente en modo offline ante fallas de conectividad y auditoría estricta mediante borrado lógico.

## ✨ Características Clave

- 🚦 **Control de Acceso en Recepción:** Semáforo visual en tiempo real para recepcionistas (🟢 Activo, 🟡 Gracia, 🔴 Vencido).
- 👤 **Gestión Auditada de Miembros:** Registro completo con borrado lógico (nunca eliminación física).
- 💵 **Normalización Multidivisa VES ➔ USD:** Conversión e historial transaccional en tiempo real para estabilidad contable.
- ⏳ **Motor de Período de Gracia Automático:** Margen configurable de 5 días de acceso asistido antes de efectuar bloqueo automático.
- 🔄 **Sincronización Diaria Integrada:** Cron job programado para actualización batch del estado de membresías.
- 📊 **Dashboard Administrativo:** Indicadores KPI, métricas de retención, filtros temporales y flujo de caja detallado.
- 👥 **Gestión de Personal (Staff) con RBAC:** Control de acceso basado en roles para Administradores y Operadores de recepción (*workers*).
- 📶 **Tolerancia a Fallas de Red (Offline First):** Registro local con **IndexedDB** y cola de sincronización batch automática al recuperar conexión.
- 🛡️ **Seguridad y Resiliencia:** Autenticación JWT con HttpOnly Cookies, hashing bcrypt, logging rotativo diario y backups automatizados de PostgreSQL.
- ⚡ **Script de Reinicio en Un Clic:** Ejecutable PowerShell (`restart.ps1`) para entorno local de desarrollo.
- 🤖 **Desarrollo Guiado por Agentes IA:** Sistema multiagente integrado (`leader`, `implementer`, `reviewer`) para asegurar consistencia del sistema.

---

## 🛠️ Stack Tecnológico

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-6C757D?style=flat-square)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)

### Frontend
![Next.js](https://img.shields.io/badge/Next.js_15-000000?style=flat-square&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)
![pnpm](https://img.shields.io/badge/pnpm-F69220?style=flat-square&logo=pnpm&logoColor=white)
![Zod](https://img.shields.io/badge/Zod-3E67B1?style=flat-square&logo=zod&logoColor=white)

---

## 📂 Estructura del Repositorio

GymFlow/
├── agents/            # Protocolos y roles para agentes IA (leader, implementer, reviewer)
├── backend/
│   ├── alembic/       # Migraciones y esquemas de base de datos PostgreSQL
│   ├── app/           # Código fuente FastAPI (routes, models, services, schemas)
│   ├── logs/          # Archivos de logs con rotación diaria
│   ├── test_*.py      # Suite de pruebas unitarias e integración con Pytest
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/           # Aplicación Next.js (app router, components, lib)
│   ├── tests/         # Suite de pruebas frontend
│   ├── package.json
│   └── pnpm-lock.yaml
├── docs/              # Especificaciones técnicas, PRD y reglas de negocio
├── progress/          # Seguimiento de Sprints (current.md, history.md)
├── agents.md          # Protocolos de navegación e instrucciones para agentes
├── design_system.md   # Tokens de diseño y componentes Tailwind
├── feature_list.json  # Backlog interactivo de características y estado
├── init.md            # Protocolo de verificación e inicialización de entorno
└── restart.ps1        # Script de reinicio rápido para entorno de desarrollo

---

## 🚀 Instalación y Configuración

Sigue estos pasos para clonar e instalar **GymFlow Analytics** en tu entorno local:

### 1. Clonar el repositorio
git clone https://github.com/LuisGalban/GymFlow.git
cd GymFlow

### 2. Configurar el Backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

### 3. Migraciones y Ejecución del Backend
# Aplicar migraciones en PostgreSQL
alembic upgrade head

# Iniciar el servidor de desarrollo
uvicorn main:app --reload

### 4. Configurar el Frontend
En otra terminal:
cd frontend

# Instalar dependencias con pnpm
pnpm install

# Iniciar el servidor de desarrollo
pnpm dev

### 📍 Puntos de Acceso
* **Frontend UI:** http://localhost:3000
* **Documentación Interactiva API (Swagger):** http://localhost:8000/docs
* **Health Check API:** http://localhost:8000/health

---

## 🔑 Variables de Entorno Requeridas

Crea un archivo .env dentro de la carpeta backend/ con los siguientes parámetros:

# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/gymflow_db

# Seguridad
JWT_SECRET_KEY=tu_clave_secreta_super_segura
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Entorno
ENVIRONMENT=development
LOG_LEVEL=INFO

---

## 🏛️ Arquitectura y Reglas Duras del Proyecto

El desarrollo de este software se rige bajo **4 Reglas Duras** de arquitectura obligatorias:

1. 🗑️ **Borrado Lógico Obligatorio:** Queda estrictamente prohibida la ejecución de sentencias DELETE físicas en la base de datos para preservar la trazabilidad contable y auditoría.
2. 💵 **Normalización USD Contable:** Todos los registros de transacciones e ingresos financieros deben ser convertidos y almacenados con su equivalente estandarizado en USD al tipo de cambio del momento.
3. 🛡️ **Validación Estricta:** Entrada y salida de datos totalmente tipadas y validadas mediante **Pydantic** en Backend y **Zod** en Frontend.
4. 🧪 **Metodología Test-First:** Desarrollo mediante iteraciones controladas siguiendo la disciplina **Rojo-Verde-Refactor**.

---

## 🧪 Testing

Para ejecutar la suite de pruebas unitarias e integración en el backend:

cd backend
pytest -v

---

## 🗺️ Roadmap

- [x] Control de acceso con semáforo visual y motor de período de gracia.
- [x] Registro y persistencia transaccional multidivisa (VES/USD).
- [x] Resiliencia de red offline mediante caché IndexedDB.
- [x] Roles RBAC y auditoría mediante borrado lógico.
- [ ] Integración con biometría/lectores de huella para recepción.
- [ ] Módulo de envío de alertas de vencimiento mediante WhatsApp API.
- [ ] Reportes analíticos exportables en PDF/Excel.

*Este proyecto se encuentra actualmente en desarrollo activo.*

---

## 🤝 Contribución

Las contribuciones, reportes de bugs y sugerencias son bienvenidos. Por favor, revisa el archivo CONTRIBUTING.md *(próximamente)* antes de enviar un Pull Request.

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo LICENSE para obtener más información.

---

## 👨‍💻 Autor

**Luis Galban**  
*Desarrollador de Software | Ingeniería en Informática*

* 🐙 GitHub: [@LuisGalban](https://github.com/LuisGalban)
* 💼 LinkedIn: [Luis Galban](https://www.linkedin.com/in/luis-galban)
