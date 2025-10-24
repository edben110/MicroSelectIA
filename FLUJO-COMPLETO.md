# 🔄 Flujo Completo del Sistema con MicroSelectIA

## 📋 Escenario: Publicar Oferta y Encontrar Candidatos

### 1️⃣ Empresa Publica Oferta Laboral

**Frontend (Next.js)** → `POST /api/jobs`
```typescript
// Usuario crea nueva oferta
const newJob = {
  title: "Desarrollador Full Stack Senior",
  description: "Buscamos desarrollador con experiencia...",
  skills: ["python", "react", "postgresql", "docker"],
  requirements: [
    "5+ años de experiencia",
    "Título universitario en sistemas",
    "Inglés intermedio"
  ],
  location: "Ciudad de México",
  type: "FULL_TIME",
  salaryMin: 40000,
  salaryMax: 60000,
  minExperienceYears: 5
};

await api.post('/jobs', newJob);
```

**Backend (Spring Boot)** → Guarda en PostgreSQL
```java
@PostMapping("/api/jobs")
public ResponseEntity<Job> createJob(@RequestBody JobDTO jobDTO) {
    Job job = jobService.save(jobDTO);
    
    // Trigger automatic matching después de crear
    jobService.findBestCandidatesForJob(job.getId());
    
    return ResponseEntity.ok(job);
}
```

---

### 2️⃣ Sistema Busca Candidatos Automáticamente

**Backend** → Ejecuta matching automático
```java
@Service
public class JobService {
    
    @Autowired
    private AIMatchingService aiMatchingService;
    
    @Autowired
    private JobMatchRepository jobMatchRepository;
    
    public void findBestCandidatesForJob(Long jobId) {
        // 1. Obtener todos los candidatos activos
        List<User> candidates = userRepository
            .findByRoleAndActive(Role.CANDIDATE, true);
        
        List<String> candidateIds = candidates.stream()
            .map(User::getId)
            .map(String::valueOf)
            .collect(Collectors.toList());
        
        // 2. Llamar a MicroSelectIA
        log.info("Calling AI matching for job {}", jobId);
        
        List<RankedMatchResult> results = 
            aiMatchingService.matchBatchCandidates(
                candidateIds, 
                jobId.toString()
            );
        
        if (results != null && !results.isEmpty()) {
            // 3. Guardar resultados en BD
            saveMatchResults(jobId, results);
            
            // 4. Notificar a top candidatos
            notifyTopCandidates(jobId, results);
            
            log.info("AI matching completed: {} candidates processed", 
                results.size());
        } else {
            // Fallback a matching local si microservicio falla
            log.warn("AI matching failed, using local algorithm");
            performLocalMatching(jobId, candidates);
        }
    }
    
    private void saveMatchResults(Long jobId, List<RankedMatchResult> results) {
        Job job = jobRepository.findById(jobId).orElseThrow();
        
        for (RankedMatchResult result : results) {
            // Solo guardar matches con score mínimo
            if (result.getCompatibilityScore() >= 0.3) {
                JobMatch match = new JobMatch();
                match.setJob(job);
                match.setUser(userRepository.findById(
                    Long.parseLong(result.getCandidateId())
                ).orElseThrow());
                match.setScore(result.getCompatibilityScore());
                match.setMatchedSkills(result.getMatchedSkills());
                match.setExplanation(result.getExplanation());
                match.setRank(result.getRank());
                match.setMatchQuality(result.getMatchQuality());
                match.setCreatedAt(LocalDateTime.now());
                
                jobMatchRepository.save(match);
            }
        }
    }
    
    private void notifyTopCandidates(Long jobId, List<RankedMatchResult> results) {
        // Notificar a los top 10 candidatos
        results.stream()
            .limit(10)
            .filter(r -> r.getMatchQuality().equals("excellent") || 
                        r.getMatchQuality().equals("good"))
            .forEach(result -> {
                // Enviar email/notificación
                notificationService.notifyCandidateAboutMatch(
                    Long.parseLong(result.getCandidateId()),
                    jobId,
                    result.getMatchPercentage()
                );
            });
    }
}
```

---

### 3️⃣ MicroSelectIA Procesa el Matching

**Python Microservice** → Calcula compatibilidad
```python
# POST /api/match/batch recibe:
{
  "candidates": [
    {
      "id": "1",
      "name": "Juan Pérez",
      "skills": ["python", "javascript", "react", "sql"],
      "experience_years": 5,
      "experience": [...],
      "education": [...]
    },
    {
      "id": "2",
      "name": "María García",
      "skills": ["python", "django", "postgresql", "aws"],
      "experience_years": 7,
      ...
    },
    ... // Más candidatos
  ],
  "job": {
    "id": "123",
    "title": "Desarrollador Full Stack Senior",
    "skills": ["python", "react", "postgresql", "docker"],
    ...
  }
}

# Microservicio procesa:
# 1. Calcula skills match (exacto + semántico)
# 2. Calcula experience match
# 3. Calcula education match
# 4. Calcula semantic similarity con BERT
# 5. Combina scores con pesos configurados
# 6. Ordena por compatibilidad (mayor a menor)

# Retorna candidatos rankeados:
{
  "job_id": "123",
  "total_candidates": 50,
  "average_score": 0.62,
  "matches": [
    {
      "rank": 1,
      "candidate_id": "2",
      "candidate_name": "María García",
      "compatibility_score": 0.89,
      "match_percentage": 89,
      "match_quality": "excellent",
      "matched_skills": ["python", "postgresql"],
      "missing_skills": ["react", "docker"],
      "explanation": "María García tiene un 89% de compatibilidad...",
      "recommendations": [...]
    },
    {
      "rank": 2,
      "candidate_id": "1",
      "candidate_name": "Juan Pérez",
      "compatibility_score": 0.87,
      ...
    },
    ... // Resto ordenado por score
  ]
}
```

---

### 4️⃣ Backend Guarda Resultados

**PostgreSQL** → Tabla `job_matches`
```sql
job_match_id | job_id | user_id | score | rank | match_quality | matched_skills           | explanation
-------------|--------|---------|-------|------|---------------|-------------------------|-------------
1            | 123    | 2       | 0.89  | 1    | excellent     | ["python","postgresql"] | María García...
2            | 123    | 1       | 0.87  | 2    | excellent     | ["python","react"]      | Juan Pérez...
3            | 123    | 5       | 0.75  | 3    | good          | ["python"]              | Carlos López...
...
```

---

### 5️⃣ Empresa Ve Candidatos Recomendados

**Frontend** → `GET /api/jobs/123/matches`
```typescript
// Vista de la empresa
const JobMatches = () => {
  const [matches, setMatches] = useState([]);
  
  useEffect(() => {
    // Obtener matches ordenados por score
    api.get(`/jobs/${jobId}/matches?sort=score,desc`)
      .then(res => setMatches(res.data));
  }, [jobId]);
  
  return (
    <div className="matches-list">
      <h2>Candidatos Recomendados (AI Matching)</h2>
      
      {matches.map(match => (
        <CandidateCard key={match.id}>
          <div className="rank">#{match.rank}</div>
          <h3>{match.user.name}</h3>
          
          {/* Score visual */}
          <CompatibilityBadge score={match.matchPercentage}>
            {match.matchPercentage}% Compatible
          </CompatibilityBadge>
          
          {/* Calidad del match */}
          <QualityBadge quality={match.matchQuality}>
            {match.matchQuality.toUpperCase()}
          </QualityBadge>
          
          {/* Skills coincidentes */}
          <div className="matched-skills">
            {match.matchedSkills.map(skill => (
              <SkillBadge key={skill}>{skill}</SkillBadge>
            ))}
          </div>
          
          {/* Explicación de la IA */}
          <p className="explanation">{match.explanation}</p>
          
          {/* Acciones */}
          <div className="actions">
            <Button onClick={() => viewProfile(match.user.id)}>
              Ver Perfil
            </Button>
            <Button primary onClick={() => inviteToApply(match)}>
              Invitar a Postular
            </Button>
          </div>
        </CandidateCard>
      ))}
    </div>
  );
};
```

**Visualización**:
```
╔════════════════════════════════════════════════════════════╗
║  Candidatos Recomendados por IA (50 candidatos analizados)║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  🥇 #1  María García                       [89% EXCELLENT]║
║         Skills: python, postgresql, aws                    ║
║         Missing: react, docker                             ║
║         "María García tiene un 89% de compatibilidad con   ║
║         el puesto. Experiencia superior a requisitos."     ║
║         [Ver Perfil] [Invitar a Postular]                  ║
║                                                            ║
║  🥈 #2  Juan Pérez                         [87% EXCELLENT]║
║         Skills: python, react, sql                         ║
║         Missing: docker                                    ║
║         "Juan Pérez tiene un 87% de compatibilidad..."     ║
║         [Ver Perfil] [Invitar a Postular]                  ║
║                                                            ║
║  🥉 #3  Carlos López                          [75% GOOD]  ║
║         Skills: python, javascript                         ║
║         Missing: react, postgresql, docker                 ║
║         "Carlos López tiene un 75% de compatibilidad..."   ║
║         [Ver Perfil] [Invitar a Postular]                  ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

### 6️⃣ Candidato Ve Ofertas Recomendadas

**Frontend** → `GET /api/candidates/me/job-recommendations`
```typescript
// Vista del candidato
const JobRecommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  
  useEffect(() => {
    // Backend filtra jobs donde el candidato tiene buen match
    api.get('/candidates/me/job-recommendations?minScore=0.6')
      .then(res => setRecommendations(res.data));
  }, []);
  
  return (
    <div className="job-recommendations">
      <h2>Ofertas Recomendadas para Ti</h2>
      
      {recommendations.map(rec => (
        <JobCard key={rec.job.id}>
          <h3>{rec.job.title}</h3>
          <p>{rec.job.company.name}</p>
          
          {/* Tu compatibilidad */}
          <CompatibilityScore score={rec.matchPercentage}>
            Eres {rec.matchPercentage}% compatible
          </CompatibilityScore>
          
          {/* Tus fortalezas */}
          <div className="strengths">
            <h4>Tus fortalezas para este puesto:</h4>
            {rec.matchedSkills.map(skill => (
              <SkillBadge variant="success">{skill}</SkillBadge>
            ))}
          </div>
          
          {/* Áreas de mejora */}
          {rec.missingSkills.length > 0 && (
            <div className="improvements">
              <h4>Podrías mejorar en:</h4>
              {rec.missingSkills.map(skill => (
                <SkillBadge variant="warning">{skill}</SkillBadge>
              ))}
            </div>
          )}
          
          {/* Recomendaciones de la IA */}
          <div className="ai-recommendations">
            <h4>Recomendaciones:</h4>
            <ul>
              {rec.recommendations.map(r => (
                <li>{r}</li>
              ))}
            </ul>
          </div>
          
          <Button primary onClick={() => applyToJob(rec.job.id)}>
            Postular Ahora
          </Button>
        </JobCard>
      ))}
    </div>
  );
};
```

---

## 🎯 Flujo Completo Resumido

```
1. EMPRESA CREA OFERTA
   ↓
2. BACKEND GUARDA EN DB
   ↓
3. BACKEND LLAMA A MICROSELECTIA
   POST /api/match/batch
   (Envía: candidatos + oferta)
   ↓
4. MICROSELECTIA PROCESA CON IA
   - Skills matching
   - Experience matching
   - Semantic matching (BERT)
   - Education matching
   ↓
5. MICROSELECTIA RETORNA RANKING
   (Candidatos ordenados por score)
   ↓
6. BACKEND GUARDA MATCHES EN DB
   (Tabla job_matches)
   ↓
7. BACKEND NOTIFICA TOP CANDIDATOS
   (Email/notificación push)
   ↓
8. EMPRESA VE CANDIDATOS RECOMENDADOS
   (Ordenados por IA, con explicaciones)
   ↓
9. CANDIDATO VE OFERTAS RECOMENDADAS
   (Donde tiene alto score)
   ↓
10. MATCH! 🎉
```

---

## 💡 Ventajas del Sistema con IA

### Para Empresas 🏢
✅ **Ahorra tiempo**: No revisar 100+ CVs manualmente
✅ **Mejores decisiones**: Matching objetivo basado en datos
✅ **Explicaciones claras**: IA explica por qué cada candidato es bueno
✅ **Top candidatos primero**: Ranking automático por compatibilidad
✅ **Reduce sesgo**: Evaluación basada en skills y experiencia

### Para Candidatos 👨‍💻
✅ **Ofertas relevantes**: Solo ve trabajos donde tiene chance
✅ **Sabe dónde mejorar**: IA dice qué skills desarrollar
✅ **Transparencia**: Ve su score y explicación
✅ **Notificaciones inteligentes**: Solo para buenos matches
✅ **Mejor experiencia**: No aplica a ofertas donde no califica

### Para el Sistema 🤖
✅ **Escalable**: Matching de miles de candidatos en segundos
✅ **Preciso**: BERT entiende contexto semántico
✅ **Configurable**: Ajustar pesos según necesidades
✅ **Independiente**: Microservicio separado
✅ **Fallback**: Si falla, usa algoritmo local

---

## 🔧 Configuración Recomendada por Industria

### Tech Startups
```env
SKILLS_WEIGHT=0.50          # Skills son críticas
EXPERIENCE_WEIGHT=0.20      # Menos peso a años
SEMANTIC_WEIGHT=0.20        # Matching cultural
EDUCATION_WEIGHT=0.10       # Educación menos relevante
```

### Empresas Corporate
```env
SKILLS_WEIGHT=0.35
EXPERIENCE_WEIGHT=0.35      # Experiencia muy importante
SEMANTIC_WEIGHT=0.15
EDUCATION_WEIGHT=0.15       # Títulos formales importantes
```

### Posiciones Senior
```env
MIN_MATCH_THRESHOLD=0.60    # Solo candidates muy calificados
GOOD_MATCH_THRESHOLD=0.75
EXCELLENT_MATCH_THRESHOLD=0.85
```

### Posiciones Junior
```env
MIN_MATCH_THRESHOLD=0.30    # Más flexible
GOOD_MATCH_THRESHOLD=0.50
EXCELLENT_MATCH_THRESHOLD=0.70
```

---

## 📊 Métricas de Éxito

### KPIs a Medir
- **Time to Fill**: Reducción en días para llenar vacantes
- **Quality of Hire**: Score promedio de candidatos contratados
- **Candidate Satisfaction**: Feedback de candidatos sobre matches
- **Recruiter Efficiency**: Horas ahorradas en screening
- **Application Conversion**: % de aplicaciones → entrevistas

### Ejemplo de Impacto
```
ANTES (Manual):
- 100 CVs recibidos
- 8 horas de screening
- 10 candidatos preseleccionados
- 3 entrevistas
- 1 contratación
- Time to Fill: 45 días

DESPUÉS (Con IA):
- 100 candidatos analizados
- 5 minutos de matching automático
- 15 candidatos recomendados (ordenados)
- 5 entrevistas (mejores candidatos)
- 1 contratación
- Time to Fill: 20 días

AHORRO: 
- 75% menos tiempo de screening
- 55% reducción en time to fill
- +67% más entrevistas de calidad
```

---

## 🚀 Implementación Gradual

### Fase 1: MVP (Semana 1-2)
- [x] Deploy MicroSelectIA local
- [x] Integrar con backend
- [ ] Probar con 10 ofertas reales
- [ ] Ajustar pesos según feedback

### Fase 2: Beta (Semana 3-4)
- [ ] Deploy a Render (producción)
- [ ] Habilitar para todas las ofertas
- [ ] Recolectar métricas
- [ ] Mejorar UI de visualización

### Fase 3: Optimización (Mes 2)
- [ ] A/B testing de algoritmos
- [ ] Fine-tuning del modelo
- [ ] Dashboard de analytics
- [ ] Notificaciones automáticas

---

**¡Sistema completo y listo para transformar tu proceso de reclutamiento! 🎯🤖**
