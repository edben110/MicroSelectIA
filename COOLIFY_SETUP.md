# Despliegue en Coolify - MicroSelectIA

## Configuración Rápida

### 1. Crear Servicio en Coolify

1. Dashboard → New Resource → Docker Compose
2. Conecta tu repositorio Git
3. Selecciona la rama (master/main)

### 2. Configuración del Servicio

**General:**
- Name: `microselectia`
- Port: `8180`
- Health Check Path: `/health`

**Build:**
- Docker Compose File: `docker-compose.yml`
- Build Command: (dejar vacío, usa el Dockerfile)

### 3. Variables de Entorno

Copia y pega estas variables en Coolify Dashboard → Environment:

```
API_PORT=8180
API_HOST=0.0.0.0
API_DEBUG=False
API_TITLE=MicroSelectIA - AI Candidate Matching Service
API_VERSION=1.0.0
API_DESCRIPTION=Microservicio de IA para calcular compatibilidad entre candidatos y ofertas laborales
AI_MODEL=sentence-transformers/all-MiniLM-L6-v2
AI_DEVICE=cpu
AI_MAX_LENGTH=512
SKILLS_WEIGHT=0.40
EXPERIENCE_WEIGHT=0.25
SEMANTIC_WEIGHT=0.25
EDUCATION_WEIGHT=0.10
MIN_MATCH_SCORE=0.30
GOOD_MATCH_SCORE=0.60
EXCELLENT_MATCH_SCORE=0.80
CORS_ORIGINS=https://tu-frontend.com,https://tu-backend.com
CACHE_ENABLED=True
CACHE_TTL_SECONDS=3600
LOG_LEVEL=INFO
LOG_FORMAT=json
```

**IMPORTANTE:** Actualiza `CORS_ORIGINS` con tus URLs reales de producción.

### 4. Volúmenes (Opcional pero Recomendado)

Para cachear el modelo de IA y acelerar reinicios:

- Name: `model_cache`
- Mount Path: `/root/.cache`

### 5. Deploy

Click en "Deploy" y espera 2-3 minutos (primera vez descarga el modelo de IA ~90MB)

## Verificación

Una vez desplegado, verifica:

```bash
# Health check
curl https://tu-dominio.com/health

# Documentación
https://tu-dominio.com/docs
```

## Configuración en Backend Java

Actualiza tu `application.properties`:

```properties
microselectia.url=https://tu-dominio.com
microselectia.enabled=true
microselectia.fallback-to-local=true
```

O si usas el nombre del servicio interno en Coolify:

```properties
microselectia.url=http://microselectia:8180
```

## Recursos Recomendados

- **RAM:** Mínimo 2GB (recomendado 4GB)
- **CPU:** 1 core (2 cores para mejor rendimiento)
- **Disco:** 2GB para cache del modelo

## Troubleshooting

**Health check falla:**
- Aumenta el `start_period` a 90s en docker-compose.yml
- Verifica logs: `docker logs microselectia`

**Primera solicitud lenta:**
- Normal, el modelo se carga en memoria (30-60s)
- Solicitudes siguientes serán rápidas

**Error de CORS:**
- Verifica que CORS_ORIGINS incluya tu dominio
- Formato: `https://dominio1.com,https://dominio2.com` (sin espacios)

**Out of Memory:**
- Aumenta RAM a 4GB
- El modelo requiere ~1.5GB en memoria

## URLs del Servicio

Después del despliegue tendrás:

- **API Base:** `https://tu-dominio.com`
- **Health:** `https://tu-dominio.com/health`
- **Docs:** `https://tu-dominio.com/docs`
- **Single Match:** `POST https://tu-dominio.com/api/match/single`
- **Batch Match:** `POST https://tu-dominio.com/api/match/batch`
- **Explain Match:** `POST https://tu-dominio.com/api/match/explain`
