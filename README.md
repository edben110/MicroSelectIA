# MicroSelectIA - AI Candidate Matching Service

Microservicio de IA para calcular compatibilidad entre candidatos y ofertas laborales usando procesamiento de lenguaje natural y machine learning.

## Requisitos

- Python 3.9+
- pip

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

El archivo `.env` ya está configurado con valores por defecto. Variables principales:

- `API_PORT`: Puerto del servicio (default: 8000)
- `API_HOST`: Host del servicio (default: 0.0.0.0)
- `CORS_ORIGINS`: Orígenes permitidos para CORS (incluye http://localhost:8080 para el backend Java)

## Ejecución

### Opción 1: Script de inicio
```bash
python start.py
```

### Opción 2: Uvicorn directo
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Opción 3: Windows
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Endpoints Disponibles

Una vez iniciado, accede a:

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Match Single**: POST http://localhost:8000/api/match/single
- **Match Batch**: POST http://localhost:8000/api/match/batch
- **Explain Match**: POST http://localhost:8000/api/match/explain

## Integración con Backend Java

El backend Java (ClippersBackend) está configurado para conectarse a este servicio en:
- URL: `http://localhost:8000`
- Timeout: 30 segundos

### Configuración en Backend Java

En `application.properties`:
```properties
ai.matching.service.url=http://localhost:8000
ai.matching.service.enabled=true
ai.matching.service.timeout=30000
```

## Testing

Ejecutar test de endpoints:
```bash
python test_api.py
```

O usar el endpoint de prueba:
```bash
curl -X POST http://localhost:8000/api/match/test
```

## Estructura del Proyecto

```
microSelectIA/
├── app/
│   ├── main.py              # Aplicación FastAPI
│   ├── api/
│   │   └── routes/
│   │       ├── health.py    # Health check endpoints
│   │       └── matching.py  # Matching endpoints
│   ├── core/
│   │   └── config.py        # Configuración
│   ├── schemas/
│   │   └── matching.py      # Modelos Pydantic
│   └── services/
│       ├── matching_engine.py # Motor de matching
│       └── ai_matcher.py      # IA matching logic
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias Python
└── start.py                # Script de inicio
```

## Estado del Servicio

Para verificar que el servicio está funcionando:

```bash
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "service": "MicroSelectIA",
  "version": "1.0.0"
}
```

## Notas Importantes

1. **Primera Ejecución**: La primera vez que se ejecuta, descargará el modelo de IA (~90MB). Esto puede tomar unos minutos.

2. **Memoria**: El servicio requiere al menos 2GB de RAM disponible para el modelo de IA.

3. **CORS**: Ya está configurado para aceptar requests desde el backend Java (localhost:8080) y el frontend (localhost:3000).

4. **Fallback**: El backend Java tiene lógica de fallback si este servicio no está disponible.

## Solución de Problemas

### Error: Puerto 8000 en uso
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Error: Módulo no encontrado
```bash
pip install -r requirements.txt --upgrade
```

### Error: CUDA no disponible
El servicio está configurado para usar CPU por defecto. Si tienes GPU compatible, cambia en `.env`:
```
AI_DEVICE=cuda
```
