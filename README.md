# MicroSelectIA - Microservicio de Selección Inteligente de Candidatos

## 📝 Descripción

Microservicio de IA independiente para calcular la compatibilidad entre candidatos y ofertas laborales. Utiliza procesamiento de lenguaje natural y algoritmos de machine learning para generar scores de matching precisos.

## 🚀 Características

- ✅ API REST independiente en Python
- ✅ Análisis de compatibilidad con IA
- ✅ Procesamiento de habilidades y experiencia
- ✅ Cálculo de porcentajes de matching
- ✅ Ordenamiento automático por compatibilidad
- ✅ Explicaciones detalladas de cada match
- ✅ Soporte para múltiples modelos de IA
- ✅ Fácil deploy en Render

## 🛠️ Tecnologías

- **Python 3.11+**
- **FastAPI** - Framework web moderno y rápido
- **Transformers** - Modelos de lenguaje (BERT, etc.)
- **Scikit-learn** - Algoritmos de ML
- **Sentence-Transformers** - Embeddings semánticos
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI

## 📦 Instalación Local

### 1. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar el servidor

```bash
python main.py
```

El servidor estará disponible en: `http://localhost:8000`

## 🌐 API Endpoints

### 1. Health Check

```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

### 2. Calcular Match Simple

```http
POST /api/match/single
```

**Request Body:**
```json
{
  "candidate": {
    "id": "candidate-uuid",
    "name": "Juan Pérez",
    "skills": ["Python", "FastAPI", "Docker"],
    "experience_years": 3,
    "education": [
      {
        "degree": "Ingeniería de Sistemas",
        "institution": "Universidad XYZ"
      }
    ],
    "languages": ["Español", "Inglés"],
    "summary": "Desarrollador backend con 3 años de experiencia..."
  },
  "job": {
    "id": "job-uuid",
    "title": "Backend Developer",
    "description": "Buscamos desarrollador backend con experiencia en Python...",
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "requirements": ["3+ años de experiencia", "Inglés intermedio"],
    "location": "Remoto",
    "type": "FULL_TIME"
  }
}
```

**Respuesta:**
```json
{
  "candidate_id": "candidate-uuid",
  "job_id": "job-uuid",
  "compatibility_score": 0.87,
  "match_percentage": 87,
  "breakdown": {
    "skills_match": 0.75,
    "experience_match": 1.0,
    "education_match": 0.85,
    "semantic_match": 0.92
  },
  "matched_skills": ["Python", "FastAPI", "Docker"],
  "missing_skills": ["PostgreSQL"],
  "explanation": "Excelente compatibilidad. El candidato tiene 75% de las habilidades requeridas, experiencia suficiente y alta similitud semántica con la descripción del puesto.",
  "recommendations": [
    "Desarrollar habilidad en PostgreSQL",
    "Destacar experiencia con Docker"
  ]
}
```

### 3. Calcular Matches Múltiples (Ranking)

```http
POST /api/match/batch
```

**Request Body:**
```json
{
  "candidates": [
    {
      "id": "candidate-1",
      "name": "Juan Pérez",
      "skills": ["Python", "FastAPI", "Docker"],
      "experience_years": 3,
      "summary": "..."
    },
    {
      "id": "candidate-2",
      "name": "María García",
      "skills": ["Python", "Django", "PostgreSQL"],
      "experience_years": 5,
      "summary": "..."
    }
  ],
  "job": {
    "id": "job-uuid",
    "title": "Backend Developer",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "requirements": ["3+ años"],
    "description": "..."
  }
}
```

**Respuesta:**
```json
{
  "job_id": "job-uuid",
  "total_candidates": 2,
  "matches": [
    {
      "candidate_id": "candidate-2",
      "candidate_name": "María García",
      "compatibility_score": 0.92,
      "match_percentage": 92,
      "rank": 1,
      "breakdown": { ... },
      "explanation": "..."
    },
    {
      "candidate_id": "candidate-1",
      "candidate_name": "Juan Pérez",
      "compatibility_score": 0.87,
      "match_percentage": 87,
      "rank": 2,
      "breakdown": { ... },
      "explanation": "..."
    }
  ]
}
```

### 4. Explicar Match (Detallado)

```http
POST /api/match/explain
```

Devuelve un análisis detallado de por qué un candidato es compatible o no.

## 🧠 Algoritmos de Matching

El microservicio utiliza múltiples estrategias de matching:

### 1. **Skills Matching (40%)**
- Calcula la intersección de habilidades
- Usa embeddings semánticos para detectar similitudes (ej: "React" ≈ "React.js")
- Penaliza habilidades faltantes críticas

### 2. **Experience Matching (25%)**
- Evalúa años de experiencia vs requerimientos
- Analiza experiencia relevante en el campo
- Considera progresión profesional

### 3. **Semantic Matching (25%)**
- Usa modelos de lenguaje (Sentence-BERT)
- Compara el resumen del candidato con la descripción del trabajo
- Detecta similitudes conceptuales

### 4. **Education & Other (10%)**
- Evalúa nivel educativo
- Considera idiomas
- Analiza ubicación geográfica

## 🔧 Configuración

Crear archivo `.env`:

```env
# API Settings
API_PORT=8000
API_HOST=0.0.0.0
API_DEBUG=False

# AI Model
AI_MODEL=sentence-transformers/all-MiniLM-L6-v2
AI_DEVICE=cpu  # o 'cuda' si tienes GPU

# Weights (suma debe ser 1.0)
SKILLS_WEIGHT=0.40
EXPERIENCE_WEIGHT=0.25
SEMANTIC_WEIGHT=0.25
EDUCATION_WEIGHT=0.10

# Thresholds
MIN_MATCH_SCORE=0.30
GOOD_MATCH_SCORE=0.60
EXCELLENT_MATCH_SCORE=0.80

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://clipers.sufactura.store
```

## 🚀 Deploy en Render

### 1. Crear `render.yaml`:

```yaml
services:
  - type: web
    name: microselectia
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: API_PORT
        value: 10000
      - key: PYTHON_VERSION
        value: 3.11.0
```

### 2. Push a GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo>
git push -u origin main
```

### 3. Conectar en Render

1. Ir a render.com
2. New -> Web Service
3. Conectar repositorio
4. Configurar variables de entorno
5. Deploy!

## 📊 Testing

### Ejecutar tests

```bash
pytest tests/
```

### Test de carga

```bash
python tests/load_test.py
```

## 🔗 Integración con Backend Java

El backend de Spring Boot debe llamar a este microservicio:

```java
@Service
public class AIMatchingService {
    
    @Value("${ai.matching.service.url}")
    private String aiServiceUrl;
    
    private final RestTemplate restTemplate;
    
    public List<JobMatchDTO> calculateMatches(Job job, List<User> candidates) {
        String url = aiServiceUrl + "/api/match/batch";
        
        BatchMatchRequest request = new BatchMatchRequest();
        request.setJob(convertJobToDTO(job));
        request.setCandidates(convertCandidatesToDTO(candidates));
        
        ResponseEntity<BatchMatchResponse> response = 
            restTemplate.postForEntity(url, request, BatchMatchResponse.class);
        
        return response.getBody().getMatches();
    }
}
```

## 📈 Métricas y Monitoreo

El microservicio expone métricas en:

```http
GET /metrics
```

Incluye:
- Total de requests
- Tiempo promedio de respuesta
- Matches calculados
- Errores

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la branch (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

MIT License - Ver archivo LICENSE

## 👥 Autores

- Equipo Clippers

## 📞 Soporte

Para reportar bugs o solicitar features, abre un issue en GitHub.
