# API de Procesamiento de Mensajes de Chat

Este proyecto es una API RESTful diseñada para procesar, almacenar y recuperar mensajes de chat en tiempo real. Fue desarrollado como una evaluación técnica para un rol de Desarrollador Backend, implementando principios de arquitectura limpia, patrones de diseño robustos y funcionalidades avanzadas para demostrar un alto nivel de competencia técnica.

---

## 🌟 Características Principales

- **Procesamiento de Mensajes**: Valida, filtra contenido inapropiado y enriquece los mensajes con metadatos útiles como conteo de palabras y caracteres.
    
- **Almacenamiento Persistente**: Guarda los mensajes de forma segura en una base de datos SQLite a través de SQLAlchemy.
    
- **Recuperación Avanzada**: Permite obtener mensajes por sesión, con paginación (`limit`/`offset`) y filtrado por remitente.
    
- **Búsqueda de Contenido**: Ofrece un endpoint dedicado para buscar mensajes que contengan un texto específico.
    
- **Actualizaciones en Tiempo Real**: Implementa un endpoint WebSocket que notifica a todos los clientes conectados cuando se crea un nuevo mensaje.
    
- **Seguridad y Control**: Protege todos los endpoints con un sistema de autenticación por **API Key** y un mecanismo de **limitación de tasa** (Rate Limiting) para prevenir abusos.
    
- **Manejo de Errores Centralizado**: Devuelve respuestas de error estandarizadas y claras para diferentes escenarios.
    
- **Documentación Automática**: Genera documentación interactiva y estática de la API de forma automática.
    

---

## 🏗️ Arquitectura y Patrones de Diseño

La estructura del proyecto se basa en principios sólidos para garantizar que el código sea mantenible, escalable y fácil de probar.

### Arquitectura Hexagonal (Puertos y Adaptadores)

Este es el pilar del diseño. Separa la lógica de negocio pura de los detalles de la infraestructura (frameworks, bases de datos, etc.).

- **🏛️ Dominio (`src/domain`)**: El corazón de la aplicación. Contiene los modelos de negocio puros (la clase `Message`), las reglas de negocio (qué es contenido inapropiado) y las interfaces o "puertos" (`IMessageRepository`) que definen los contratos que la aplicación necesita, sin saber quién los implementará. **Es 100% independiente de FastAPI y SQLAlchemy.**
    
- **🧩 Aplicación (`src/application`)**: Orquesta los casos de uso (ej. "crear un nuevo mensaje"). Llama a los modelos de dominio para ejecutar la lógica de negocio y usa los puertos del dominio para solicitar acciones a la infraestructura (ej. "guarde este mensaje").
    
- **🔌 Infraestructura (`src/infrastructure`)**: Contiene todo el código que interactúa con el mundo exterior. Se divide en **"adaptadores"** que implementan los puertos del dominio.
    
    - **Adaptadores de Entrada**: Exponen la aplicación al mundo. Aquí viven los endpoints de FastAPI, los manejadores de WebSockets y la lógica de autenticación.
        
    - **Adaptadores de Salida**: Implementan la comunicación con servicios externos, como la clase `SQLiteMessageRepository` que traduce los objetos de dominio a un formato que la base de datos entiende.
        
![Diagrama de Arquitectura Hexagonal](https://github.com/DiegoOrtiz27-pragma/chat-api-fastAPI/blob/main/img/arquitectura_hexagonal.png)

### Patrones de Diseño Utilizados

- **Inyección de Dependencias (Dependency Injection)**: En lugar de que los componentes creen sus propias dependencias, estas se les "inyectan" desde fuera (ver `dependencies.py`). Esto desacopla el código y facilita enormemente las pruebas, permitiéndonos reemplazar dependencias reales (como un repositorio de base de datos) por "mocks" o simuladores.
    
- **Singleton**: El `ConnectionManager` para los WebSockets se implementa como un Singleton a nivel de módulo. Esto asegura que exista **una única instancia** del gestor de conexiones en toda la aplicación, permitiendo que el endpoint `POST` pueda comunicar eficientemente los nuevos mensajes a los clientes conectados a través del endpoint WebSocket.
    
- **Repositorio (Repository Pattern)**: Abstrae la lógica de acceso a datos. El `MessageService` no sabe si los datos se guardan en SQLite, PostgreSQL o un archivo de texto; solo habla con la interfaz `IMessageRepository`, cumpliendo el contrato.
    

---

## 💻 Stack Tecnológico

- **Lenguaje**: Python 3.10+
    
- **Framework**: FastAPI
    
- **Base de Datos**: SQLite (a través de SQLAlchemy ORM)
    
- **Validación de Datos**: Pydantic
    
- **Limitación de Tasa**: SlowAPI
    
- **Testing**: Pytest, Pytest-Mock, Pytest-Asyncio
    

---

## 🚀 Cómo Empezar

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local.

### **Pre-requisitos**

- Tener instalado Python 3.10 o superior.
    
- Tener instalado Git.
    

### **Instalación**

1. **Clona el repositorio**:
    
    Bash
    
    ```
    git clone <URL_DE_TU_REPOSITORIO_GIT>
    cd chat-api
    ```
    
2. **Crea y activa un entorno virtual**:
    
    - En Windows (PowerShell):
        
        Bash
        
        ```
        python -m venv venv
        .\venv\Scripts\activate
        ```
        
    - En macOS/Linux:
        
        Bash
        
        ```
        source venv/bin/activate
        ```
        
3. **Instala las dependencias**:
    
    Bash
    
    ```
    pip install -r requirements.txt
    ```
    

### **Ejecución**

Una vez instaladas las dependencias, inicia el servidor de desarrollo con Uvicorn:

Bash

```
uvicorn src.infrastructure.main:app --reload
```

El servidor estará disponible en `http://127.0.0.1:8000`.

---

## 📚 Documentación de la API

La documentación de la API es generada automáticamente y es la mejor forma de explorar y probar los endpoints.

- **Swagger UI (interactivo)**: `http://127.0.0.1:8000/docs`
    
- **ReDoc (lectura)**: `http://127.0.0.1:8000/redoc`
    

---

## Endpoints

Todos los endpoints requieren autenticación a través de la cabecera `X-API-Key: <tu-clave-secreta>`.

### 1. Crear un Mensaje

Procesa, almacena y transmite un nuevo mensaje de chat.

- **Método**: `POST`
    
- **URL**: `/api/messages/`
    

### 2. Obtener Mensajes por Sesión

Recupera una lista de mensajes para una sesión específica.

- **Método**: `GET`
    
- **URL**: `/api/messages/{session_id}`
    
- **Parámetros**: `limit`, `offset`, `sender`.
    

### 3. Buscar Mensajes por Contenido

Busca mensajes en todas las sesiones que contengan un texto.

- **Método**: `GET`
    
- **URL**: `/api/messages/search/`
    
- **Parámetro**: `q` (término de búsqueda).
    

### 4. Conexión WebSocket para Tiempo Real

Establece una conexión para recibir notificaciones de nuevos mensajes.

- **Protocolo**: `ws`
    
- **URL**: `/api/messages/ws`
    
- **Autenticación**: A través de un query param: `ws://127.0.0.1:8000/api/messages/ws?X-API-Key=<tu-clave-secreta>`
    

---

## 🧪 Pruebas

El proyecto tiene una cobertura de pruebas del 100%, validando todas las capas de la aplicación.

- Para ejecutar todas las pruebas:
    
    Bash
    
    ```
    pytest
    ```
    
- Para generar un reporte de cobertura en formato HTML:
    
    Bash
    
    ```
    pytest --cov=src --cov-report=html
    ```
    
    Luego, abre el archivo `htmlcov/index.html` en tu navegador.