# 🚀 Guía Paso a Paso: Deploy MicroSelectIA en Render

## ✅ Requisitos Previos
- [ ] Cuenta en GitHub (gratis)
- [ ] Cuenta en Render (gratis)
- [ ] MicroSelectIA funcionando localmente

---

## 📋 Paso 1: Subir a GitHub

### 1.1 Crear repositorio en GitHub
1. Ve a https://github.com/new
2. Nombre: `microselectia`
3. Descripción: `AI-powered candidate matching microservice`
4. Público o Privado (funciona con ambos)
5. Click "Create repository"

### 1.2 Push del código
```bash
cd C:\Users\edben\OneDrive\Desktop\Clippers\microSelectIA

# Inicializar git (si no está inicializado)
git init

# Agregar archivos
git add .

# Commit
git commit -m "Initial commit - MicroSelectIA ready for Render"

# Conectar con GitHub
git remote add origin https://github.com/TU-USUARIO/microselectia.git

# Push
git push -u origin main
```

---

## 🌐 Paso 2: Deploy en Render

### 2.1 Crear cuenta en Render
1. Ve a https://render.com
2. Click "Get Started"
3. Sign up con GitHub (recomendado)
4. Autoriza Render a acceder a tus repos

### 2.2 Crear Web Service
1. En Dashboard, click **"New +"**
2. Selecciona **"Web Service"**
3. Conecta tu repositorio:
   - Click "Connect a repository"
   - Busca `microselectia`
   - Click "Connect"

### 2.3 Configurar el Servicio

**Configuración Básica:**
```
Name: microselectia
Region: Oregon (o el más cercano a ti)
Branch: main
Runtime: Python 3
```

**Build & Start Commands:**
```
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

**Plan:**
- **Free**: $0/mes
  - 512 MB RAM
  - Servicio duerme después de 15 min de inactividad
  - 750 horas/mes
  - ⚠️ Cold start de ~30s después de dormir
  
- **Starter**: $7/mes (RECOMENDADO)
  - 2 GB RAM
  - Servicio siempre activo
  - Sin cold starts
  - Mejor performance

### 2.4 Variables de Entorno

En la sección **"Environment Variables"**, agregar:

```bash
# COPIAR EXACTAMENTE ESTAS VARIABLES
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
API_TITLE=MicroSelectIA
API_DESCRIPTION=AI-powered candidate matching microservice
API_VERSION=1.0.0

# AI Model
AI_MODEL=sentence-transformers/all-MiniLM-L6-v2
AI_DEVICE=cpu

# Matching Weights
SKILLS_WEIGHT=0.40
EXPERIENCE_WEIGHT=0.25
SEMANTIC_WEIGHT=0.25
EDUCATION_WEIGHT=0.10

# Thresholds
MIN_MATCH_THRESHOLD=0.30
GOOD_MATCH_THRESHOLD=0.60
EXCELLENT_MATCH_THRESHOLD=0.80

# CORS - IMPORTANTE: Cambiar con tus URLs
CORS_ORIGINS=https://backend.sufactura.store,https://tu-frontend.onrender.com,http://localhost:8080,http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

**⚠️ IMPORTANTE**: Reemplaza `CORS_ORIGINS` con las URLs de tu backend y frontend reales.

### 2.5 Disco Persistente (Opcional pero Recomendado)

En **"Advanced"** → **"Add Disk"**:
```
Name: model-cache
Mount Path: /opt/render/project/.cache
Size: 1 GB
```

Esto cachea el modelo BERT para que no se descargue en cada deploy.

### 2.6 Deploy

1. Click **"Create Web Service"**
2. Render empezará a construir
3. **Primera build toma ~5-10 minutos** (descarga modelo AI)
4. Verás logs en tiempo real

---

## ✅ Paso 3: Verificar Deployment

### 3.1 Obtener URL
Después del deploy exitoso, Render te da una URL:
```
https://microselectia-XXXX.onrender.com
```

### 3.2 Verificar Health
```bash
curl https://microselectia-XXXX.onrender.com/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "service": "MicroSelectIA",
  "model": {
    "name": "sentence-transformers/all-MiniLM-L6-v2",
    "status": "loaded"
  }
}
```

### 3.3 Ver Documentación
Abre en navegador:
```
https://microselectia-XXXX.onrender.com/docs
```

---

## 🔗 Paso 4: Conectar con Backend Spring Boot

### 4.1 Actualizar application.properties

En tu backend (`backendClipers/src/main/resources/application.properties`):

```properties
# MicroSelectIA Configuration
microselectia.enabled=true

# ⚠️ CAMBIAR CON TU URL DE RENDER
microselectia.url=https://microselectia-XXXX.onrender.com

# Fallback a matching local si falla
microselectia.fallback-to-local=true

# Timeouts
microselectia.connection-timeout=10000
microselectia.read-timeout=60000
```

### 4.2 Actualizar CORS en Render

En Render Dashboard → Tu servicio → Environment:

Edita `CORS_ORIGINS` para incluir tu backend:
```bash
CORS_ORIGINS=https://backend.sufactura.store,https://tu-backend.onrender.com,http://localhost:8080
```

Click "Save Changes" → Render redeploy automáticamente

### 4.3 Probar desde Backend

```bash
# Desde tu máquina local
curl -X POST https://microselectia-XXXX.onrender.com/api/match/test
```

O desde Java:
```java
// Test endpoint
@GetMapping("/api/test-ai-matching")
public ResponseEntity<?> testAIMatching() {
    boolean healthy = aiMatchingService.isServiceHealthy();
    return ResponseEntity.ok(Map.of("ai_service_healthy", healthy));
}
```

---

## 📊 Paso 5: Monitoreo

### 5.1 Ver Logs en Tiempo Real
Render Dashboard → Tu servicio → **Logs**

Verás:
```
Starting MicroSelectIA...
AI Model: sentence-transformers/all-MiniLM-L6-v2
Loading model...
Model loaded successfully!
Application started on 0.0.0.0:8000
```

### 5.2 Métricas
Render Dashboard → Tu servicio → **Metrics**
- CPU usage
- Memory usage
- Request count
- Response times

### 5.3 Eventos
Render Dashboard → Tu servicio → **Events**
- Deploys
- Crashes
- Restarts

---

## 🐛 Troubleshooting

### Problema 1: "Build Failed"
**Causa**: Error al instalar dependencias
**Solución**:
```bash
# Verificar requirements.txt localmente
pip install -r requirements.txt

# Si falla, actualizar pip
pip install --upgrade pip
```

### Problema 2: "Service Unavailable (503)"
**Causa**: Servicio dormido (plan Free)
**Solución**: 
- Espera 30 segundos (cold start)
- O upgradeate a plan Starter ($7/mes)

### Problema 3: "Out of Memory"
**Causa**: RAM insuficiente (512MB en Free)
**Solución**: Upgrade a Starter (2GB RAM)

### Problema 4: "CORS Error"
**Causa**: Backend URL no está en CORS_ORIGINS
**Solución**:
```bash
# Actualizar variable en Render
CORS_ORIGINS=https://backend.sufactura.store,...
```

### Problema 5: "Model Download Timeout"
**Causa**: Primera build tarda mucho
**Solución**: 
- Es normal, espera 10 min
- Próximas builds serán rápidas (modelo cacheado)

---

## 🎯 Checklist Final

- [ ] Código en GitHub
- [ ] Servicio creado en Render
- [ ] Variables de entorno configuradas
- [ ] CORS_ORIGINS con URLs correctas
- [ ] Deploy exitoso (status: Live)
- [ ] Health check funciona
- [ ] Docs accesibles (/docs)
- [ ] Backend configurado con URL de Render
- [ ] Test desde backend funciona
- [ ] Logs sin errores

---

## 💰 Costos

### Plan Free
- **Costo**: $0/mes
- **Límites**: 
  - 512MB RAM
  - Duerme después de 15 min
  - 750 horas/mes
- **Ideal para**: Testing, desarrollo

### Plan Starter (RECOMENDADO)
- **Costo**: $7/mes
- **Beneficios**:
  - 2GB RAM
  - Siempre activo (no duerme)
  - Sin cold starts
  - Mejor performance
- **Ideal para**: Producción

---

## 🚀 Próximos Pasos

1. ✅ Deploy exitoso
2. ⏭️ Integrar con backend
3. ⏭️ Probar matching real
4. ⏭️ Monitorear performance
5. ⏭️ Ajustar weights según resultados
6. ⏭️ (Opcional) Configurar custom domain

---

## 📞 URLs Importantes

- **Servicio**: https://microselectia-XXXX.onrender.com
- **Health**: https://microselectia-XXXX.onrender.com/health
- **Docs**: https://microselectia-XXXX.onrender.com/docs
- **Dashboard**: https://dashboard.render.com

---

**¡Deployment exitoso en Render! 🎉**

Tiempo estimado total: **15-20 minutos**
