# 🚀 Guía Rápida de Deployment - MicroSelectIA

## 📋 Tabla de Contenidos
- [Deployment Local](#deployment-local)
- [Deployment con Docker](#deployment-con-docker)
- [Deployment en Render](#deployment-en-render)
- [Integración con Backend](#integración-con-backend)
- [Testing](#testing)

---

## 🏠 Deployment Local

### Requisitos
- Python 3.11+
- 4GB RAM mínimo (8GB recomendado)
- 2GB de espacio en disco

### Paso a Paso

1. **Crear entorno virtual**
```bash
python -m venv venv
```

2. **Activar entorno virtual**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar template
copy .env.example .env

# Editar .env con tus configuraciones
```

5. **Iniciar servidor**
```bash
python main.py
```

6. **Verificar**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Script Rápido (Windows)
```bash
start-local.bat
```

---

## 🐳 Deployment con Docker

### Requisitos
- Docker Desktop instalado y corriendo
- 8GB RAM disponible

### Paso a Paso

1. **Build de imagen**
```bash
docker build -t microselectia:latest .
```

2. **Ejecutar contenedor**
```bash
docker run -d \
  --name microselectia \
  -p 8000:8000 \
  -e API_DEBUG=false \
  microselectia:latest
```

3. **Con Docker Compose (recomendado)**
```bash
docker-compose up -d
```

4. **Ver logs**
```bash
docker-compose logs -f microselectia
```

5. **Detener**
```bash
docker-compose down
```

### Script Rápido (Windows)
```bash
start-docker.bat
```

---

## ☁️ Deployment en Render

### Opción 1: Usando render.yaml (Recomendado)

1. **Push a GitHub**
```bash
git init
git add .
git commit -m "Initial commit - MicroSelectIA"
git remote add origin https://github.com/tu-usuario/microselectia.git
git push -u origin main
```

2. **Conectar con Render**
- Ve a https://render.com
- Click en "New +"
- Selecciona "Blueprint"
- Conecta tu repositorio
- Render detectará automáticamente `render.yaml`

3. **Configurar Variables de Entorno**
Las variables ya están en `render.yaml`, pero puedes ajustarlas:
- `CORS_ORIGINS`: Agrega tus URLs de producción
- `AI_DEVICE`: Mantén en `cpu` (Render no tiene GPU gratis)
- `LOG_LEVEL`: `INFO` para producción

4. **Deploy**
- Click en "Apply"
- Render construirá y desplegará automáticamente
- Primera build tomará ~5-10 minutos (descarga modelo AI)

### Opción 2: Manual

1. **New Web Service**
- Tipo: Web Service
- Repositorio: Tu repo de GitHub
- Branch: main

2. **Configuración**
```
Name: microselectia
Environment: Python 3
Region: Oregon (o el más cercano)
Branch: main
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

3. **Plan**
- Starter ($7/mes) o Free (con limitaciones)
- Free: 512MB RAM, duerme después de 15min inactividad

4. **Variables de Entorno**
Agregar todas las de `render.yaml`:
```
API_HOST=0.0.0.0
API_PORT=8000
AI_MODEL=sentence-transformers/all-MiniLM-L6-v2
...
```

5. **Deploy**
- Click "Create Web Service"
- Espera la build (5-10 min primera vez)

### Post-Deployment

1. **Obtener URL**
```
https://microselectia-xxxx.onrender.com
```

2. **Verificar Health**
```bash
curl https://microselectia-xxxx.onrender.com/health
```

3. **Ver Documentación**
```
https://microselectia-xxxx.onrender.com/docs
```

### Optimizaciones para Render

1. **Caché de Modelo**
- Render proporciona disco persistente
- El modelo se descarga una vez y se cachea
- Próximas builds son más rápidas

2. **Cold Start**
- En plan Free, el servicio "duerme" después de 15min
- Primera request después de dormir toma ~30s
- Plan Starter mantiene servicio siempre activo

3. **Límites de Plan Free**
- 512MB RAM
- 0.1 CPU
- 750 horas/mes
- Suficiente para pruebas y desarrollo

---

## 🔗 Integración con Backend

### 1. Configurar Backend Spring Boot

**application.properties**
```properties
# MicroSelectIA Configuration
microselectia.enabled=true
microselectia.url=http://localhost:8000
microselectia.fallback-to-local=true
microselectia.connection-timeout=5000
microselectia.read-timeout=30000
```

**Producción**
```properties
microselectia.url=https://microselectia-xxxx.onrender.com
```

### 2. Agregar RestTemplate

**Config.java**
```java
@Configuration
public class RestTemplateConfig {
    
    @Bean
    public RestTemplate restTemplate() {
        RestTemplate restTemplate = new RestTemplate();
        
        // Timeouts
        HttpComponentsClientHttpRequestFactory factory = 
            new HttpComponentsClientHttpRequestFactory();
        factory.setConnectTimeout(5000);
        factory.setReadTimeout(30000);
        
        restTemplate.setRequestFactory(factory);
        return restTemplate;
    }
}
```

### 3. Usar AIMatchingService

**JobService.java**
```java
@Service
public class JobService {
    
    @Autowired
    private AIMatchingService aiMatchingService;
    
    public void matchCandidatesForJob(Long jobId) {
        // Get all candidates
        List<String> candidateIds = getCandidateIds();
        
        // Call AI matching
        List<RankedMatchResult> results = 
            aiMatchingService.matchBatchCandidates(
                candidateIds, 
                jobId.toString()
            );
        
        if (results != null) {
            // Use AI results
            saveMatchResults(results);
        } else {
            // Fallback to local matching
            performLocalMatching(jobId);
        }
    }
}
```

### 4. Actualizar CORS

**MicroSelectIA .env**
```bash
CORS_ORIGINS=https://backend.sufactura.store,https://frontend.sufactura.store,http://localhost:8080,http://localhost:3000
```

---

## 🧪 Testing

### 1. Test Manual

**Health Check**
```bash
curl http://localhost:8000/health
```

**Single Match**
```bash
curl -X POST http://localhost:8000/api/match/single \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "id": "1",
      "name": "Juan",
      "skills": ["python", "react"],
      "experience_years": 5
    },
    "job": {
      "id": "1",
      "title": "Developer",
      "skills": ["python", "javascript"]
    }
  }'
```

### 2. Test con Script

```bash
python test_api.py
```

### 3. Test desde Backend

```bash
# Desde backendClipers
curl http://localhost:8080/api/jobs/1/match
```

### 4. Swagger UI

Abre http://localhost:8000/docs y prueba los endpoints interactivamente.

---

## 📊 Monitoreo

### Logs en Local
```bash
# Ver logs en tiempo real
docker-compose logs -f microselectia
```

### Logs en Render
- Dashboard → Tu servicio → Logs
- Ver logs en tiempo real
- Buscar errores específicos

### Health Checks

**Local**
```bash
curl http://localhost:8000/health | jq
```

**Producción**
```bash
curl https://microselectia-xxxx.onrender.com/health | jq
```

### Métricas Importantes

1. **Tiempo de respuesta**
   - Single match: ~500ms - 2s
   - Batch match (10 candidatos): ~2s - 5s
   - Primera request: ~10s (carga modelo)

2. **Uso de recursos**
   - RAM: 500MB - 1GB
   - CPU: ~50% durante matching
   - Disco: ~500MB (modelo cacheado)

---

## 🐛 Troubleshooting

### Problema: "Model not found"
**Solución**: El modelo se descarga en primera ejecución. Espera 1-2 minutos.

### Problema: "Out of memory"
**Solución**: 
- Local: Aumenta RAM disponible
- Render: Usa plan Starter (512MB → 2GB)

### Problema: "Connection timeout"
**Solución**: 
- Verifica que el servicio esté corriendo
- Aumenta timeout en backend
- Verifica CORS

### Problema: "Service unavailable"
**Solución**:
- Render Free: El servicio puede estar "dormido", espera 30s
- Verifica logs para errores
- Reinicia el servicio

### Problema: Matching muy lento
**Solución**:
- Primera request siempre es lenta (carga modelo)
- Requests subsecuentes son rápidas
- Considera usar batch matching para múltiples candidatos

---

## 🎯 Próximos Pasos

1. ✅ Deploy local exitoso
2. ✅ Deploy en Render
3. ✅ Integrar con backend
4. ✅ Testing completo
5. 🔄 Monitorear performance
6. 🔄 Ajustar pesos de matching según resultados
7. 🔄 Implementar caché de resultados (opcional)
8. 🔄 Agregar autenticación (opcional)

---

## 📞 Soporte

- **Documentación API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Logs**: `docker-compose logs -f` o Render Dashboard

---

**¡Deployment exitoso! 🎉**
