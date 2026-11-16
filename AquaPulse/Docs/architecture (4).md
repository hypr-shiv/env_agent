# AquaPulse --- Multi-Agent System Architecture

**Project:** AquaPulse --- AI-Powered Smart Fisheries & Coastal Safety
System\
**Pilot:** Palghar, Maharashtra, India\
**Status:** Initial technical blueprint

## 1. Purpose

AquaPulse provides one conversational interface for fishermen and
coastal authorities. A central LangGraph orchestrator interprets each
request, selects one or more specialist agents, validates their
evidence, and returns a consolidated answer with sources, dates,
locations and uncertainty. The platform supports decision-making; it
does not replace official warnings, government instructions, fisheries
regulations or qualified environmental assessment.

## 2. Technology stack

  Layer                       Technology
  --------------------------- ---------------------------------
  Frontend                    React, Vite, Tailwind CSS
  Backend/API                 Python, FastAPI, Pydantic
  Orchestration               LangGraph StateGraph
  Language model              Ollama, Llama 3.2:3b
  Structured data             PostgreSQL
  Document retrieval          ChromaDB, Sentence Transformers
  Data processing             Pandas, NumPy
  Fish image classification   PyTorch, MobileNetV3
  Maps                        Leaflet, OpenStreetMap

Use one shared LLM initially. Specialize agents through separate
prompts, tools, retrieval sources and validation rules. Use a dedicated
computer-vision model for fish images.

## 3. High-level architecture

``` text
Users (Fishermen / Coastal Authorities)
                 |
          React Frontend
     Chat | Image | Dashboard | Maps
                 |
             FastAPI
 Authentication | Validation | Uploads
                 |
         Request Preprocessor
       Text / Image / Location / Language
                 |
        LANGGRAPH ORCHESTRATOR
       Intent | Planning | Routing
                 |
   +------+------+------+-------+------+
   |      |      |      |       |      |
Weather Fisheries Disaster Market Environment
   |      |      |      |       |
   +------+------+------+-------+
                 |
       Scheme Agent | Complaint Agent
                 |
       Result Normalization
                 |
       Evidence / Freshness Check
                 |
       Response Synthesis
                 |
          AquaPulse Answer

Shared services:
Ollama | PostgreSQL | ChromaDB | File Storage
Official APIs | Curated Datasets | Logs and Metrics
```

### Logical layers

  -----------------------------------------------------------------------
  Layer                               Responsibility
  ----------------------------------- -----------------------------------
  Presentation                        Chat, image upload, dashboards,
                                      maps and language selection

  API                                 Authentication, request validation,
                                      upload handling and response
                                      contracts

  Orchestration                       Intent classification, planning,
                                      routing, parallel execution and
                                      aggregation

  Specialist agents                   Domain-specific reasoning, tools,
                                      retrieval and analysis

  Intelligence                        Ollama, embeddings, RAG, image
                                      classification and deterministic
                                      analytics

  Data                                Structured records, documents,
                                      images, source metadata and audit
                                      logs

  Governance                          Safety checks, access control,
                                      freshness, provenance and human
                                      review
  -----------------------------------------------------------------------

## 4. Specialist agents

### 4.1 Weather Agent

-   Retrieve weather forecasts and marine conditions for supported
    coastal locations.
-   Summarize wind, waves, rainfall, visibility and other available
    parameters.
-   Retrieve official fishermen warnings and marine bulletins.
-   Include source, issue time, valid period and affected area.
-   Clearly identify stale or unavailable data.

Use approved weather APIs and official IMD/INCOIS bulletins. Never infer
that conditions are safe for fishing from a general forecast. Official
warnings take precedence.

### 4.2 Fisheries Agent

-   Explain fish taxonomy, common names and biological characteristics.
-   Retrieve documented habitat, distribution and seasonal information.
-   Summarize fisheries advisories, regulations and conservation
    information.
-   Retrieve local catch and landing-centre records when available.
-   Coordinate with Fish Vision and Market services.

Distinguish general species distribution from observed local catch.
Never promise a catch location or recommend fishing in restricted areas.

### 4.3 Disaster Agent

-   Retrieve official cyclone, heavy-rain, flood, high-tide and coastal
    hazard warnings.
-   Identify affected locations, severity, issue time and validity.
-   Summarize preparedness instructions from official sources.
-   Maintain alert history and avoid duplicate notifications.

The LLM may explain official warnings but must not create, downgrade or
override them.

### 4.4 Market Agent

-   Retrieve species-wise prices from configured markets.
-   Compare prices across markets and dates.
-   Show market, grade/size, unit, observation date and source.
-   Calculate indicative catch value only when quantity and comparable
    price units are supplied.
-   Identify missing or non-comparable records.

Never present mock prices as live prices. Do not compare different units
or grades without explaining the difference.

### 4.5 Environment Agent

-   Analyze water-quality measurements such as pH, dissolved oxygen,
    BOD, COD, turbidity, salinity and temperature when available.
-   Retrieve documented pollution incidents and environmental reports.
-   Analyze shoreline-change observations and mangrove records.
-   Summarize marine biodiversity information.
-   Compare historical observations and flag values crossing configured
    reference thresholds.
-   Provide location-specific evidence and data gaps.

Use curated official environmental records where available, including
relevant MPCB, ISRO/NCCR and forestry sources. Threshold exceedance is
not automatically a complete ecological or legal assessment. Include
reference, units, sample date and limitations. Never claim pollution
without evidence.

### 4.6 Government Scheme Agent

-   Search official scheme guidelines and notifications.
-   Explain purpose, eligibility criteria, required documents and
    application route.
-   Identify issuing authority and document date.
-   Provide a checklist based on retrieved evidence.

Do not guarantee eligibility, approval, benefit amount or application
success. Refer users to the responsible authority for confirmation.

### 4.7 Complaint Agent

-   Collect complaint category, description, location, date and optional
    evidence.
-   Validate required fields and user confirmation.
-   Create a complaint record and unique tracking identifier.
-   Route to a configured authority queue.
-   Provide status and status history.
-   Support authorized staff updates and closure notes.

Registration is not the same as authority acceptance or resolution.
Never fabricate a tracking ID or status. Protect personal information
and enforce role-based access.

## 5. LangGraph orchestration workflow

Use LangGraph `StateGraph` with typed shared state, nodes and
conditional edges. Run multiple agents in parallel only when the request
genuinely requires them.

``` text
START
  |
request_validation
  |
input_preprocessing
  |
input_type_router
  |----------------------------|
  |                            |
text_request                image_request
  |                            |
intent_classifier           image_validation
  |                            |
task_planner                fish_classifier
  |                            |
agent_router                species_result
  |                            |
  |                     Fisheries + Market tasks
  |                            |
  +-------------+--------------+
                |
        specialist execution
        (one or multiple agents)
                |
        result_normalization
                |
        evidence_validation
                |
        response_synthesis
                |
        response_policy_check
                |
               END
```

### Routing modes

-   **Single agent:** "Explain mangrove ecosystems in Palghar" →
    Environment Agent.
-   **Multi-agent:** "Summarize tomorrow's fishing conditions and
    official warnings" → Weather + Disaster, with Fisheries when
    relevant.
-   **Image-assisted:** fish classifier → Fisheries Agent + Market
    Agent.
-   **General query:** answer without invoking specialist agents
    unnecessarily.
-   **Clarification:** ask for missing location, date, species or market
    when needed.

Independent agents may run in parallel. Their results must be normalized
and aggregated without losing source attribution. Define reducers for
list-valued state fields. Set execution limits, per-agent timeouts,
bounded retries and loop prevention. Return partial results honestly
when an agent fails.

## 6. Shared state and agent contract

Illustrative LangGraph state:

``` python
class AquaPulseState(TypedDict, total=False):
    request_id: str
    conversation_id: str
    user_id: str | None
    user_query: str
    language: str
    location: dict
    input_type: str
    image_asset_id: str | None
    detected_intents: list[str]
    planned_agents: list[str]
    agent_results: list[dict]
    evidence: list[dict]
    warnings: list[str]
    final_response: dict
    errors: list[dict]
```

Standard agent result:

``` json
{
  "agent_name": "Environment Agent",
  "status": "success",
  "summary": "Evidence-based summary",
  "data": {},
  "location": "Satpati, Palghar",
  "sources": [
    {
      "title": "Source document or dataset",
      "publisher": "Publishing organization",
      "url": null,
      "observed_at": null,
      "published_at": null,
      "retrieved_at": "ISO-8601 timestamp"
    }
  ],
  "confidence": null,
  "warnings": [],
  "is_mock_data": false
}
```

Allowed statuses: `success`, `partial`, `unavailable`, `error`. Define
and test what confidence means; an LLM's self-reported confidence is not
a calibrated probability.

## 7. Fish image identification

Image classification is a separate computer-vision service. Do not ask
the LLM to identify pixels.

``` text
Image upload
    |
File type / size / safety validation
    |
Image preprocessing
    |
PyTorch classifier (MobileNetV3)
    |
Top-k candidate species + confidence
    |
Unknown / low-confidence check
    |
    +------------------------+
    |                        |
Fisheries Agent          Market Agent
 taxonomy, habitat,      dated price records,
 distribution, season    market, grade and unit
    |                        |
    +------------+-----------+
                 |
        Evidence validation
                 |
        User-facing result
```

Return candidate species, scientific/common names when supported, top
predictions, confidence, habitat/distribution evidence, local catch
records if available, and dated market prices. A photo cannot establish
where a fish was caught, current local availability, legal catchability
or exact market value. Use an unknown/abstain result when confidence is
insufficient.

## 8. Data architecture

### PostgreSQL --- structured and transactional data

-   users and roles
-   location reference data
-   fish species
-   catch and landing-centre records
-   market prices
-   weather snapshots
-   disaster alerts
-   environmental observations
-   schemes and document metadata
-   complaints and status history
-   agent execution and audit records

Use migrations, constraints, indexes, explicit units and timezone-aware
timestamps.

### ChromaDB --- semantic document retrieval

-   environmental reports
-   fisheries guidance
-   scheme guidelines
-   official bulletins
-   approved FAQs and manuals

Metadata should include `agent_name`, `document_id`, `publisher`,
`location`, `district`, `document_date`, `source_url`, `page_number`,
`document_type` and `is_mock`.

### File storage

Store images and uploaded documents in controlled file/object storage.
Use generated asset IDs, access controls, file-size limits, MIME
validation, retention policies and malware scanning where available.

### RAG workflow

``` text
Approved PDF / TXT / document
       |
Source validation and ingestion
       |
Text extraction + metadata normalization
       |
Chunking + embeddings
       |
ChromaDB
       |
Query + metadata filters
       |
Relevant passages and source metadata
       |
LLM answer grounded in retrieved evidence
       |
Citation and freshness validation
```

Use SQL/Pandas for exact numeric queries. Embeddings are for semantic
document retrieval, not a replacement for numeric querying.

## 9. Source governance and freshness

Candidate source categories:

  -----------------------------------------------------------------------
  Domain                              Sources to investigate
  ----------------------------------- -----------------------------------
  Weather                             IMD

  Marine conditions                   INCOIS

  Fisheries                           Department of Fisheries, FishBase,
                                      verified local records

  Disaster                            IMD, INCOIS, Maharashtra/district
                                      disaster authorities

  Market                              Verified local market and
                                      landing-centre records

  Environment                         MPCB, ISRO/NCCR, official forestry
                                      records

  Schemes                             Official central and Maharashtra
                                      government publications

  Complaints                          Authorized local authority
                                      workflows and AquaPulse records
  -----------------------------------------------------------------------

Verify access, terms of use, update frequency, geographic coverage,
units, licensing and attribution before integration.

Retain provenance fields where available: `source_id`, source name and
URL, `published_at`, `observed_at`, `retrieved_at`, `valid_from`,
`valid_until`, location and geographic scope, units and measurement
method, `is_mock`, and ingestion version. Only label data Live, Recently
retrieved, Historical, Mock or Unavailable when metadata and explicit
freshness rules support that label.

## 10. FastAPI endpoints

  -------------------------------------------------------------------------------------
  Method                  Endpoint                              Purpose
  ----------------------- ------------------------------------- -----------------------
  POST                    `/api/v1/chat`                        Submit query to
                                                                orchestrator

  POST                    `/api/v1/fish/identify`               Upload and classify
                                                                fish image

  GET                     `/api/v1/weather`                     Weather data/result

  GET                     `/api/v1/fisheries/species`           Search species

  GET                     `/api/v1/disaster/alerts`             Official alerts

  GET                     `/api/v1/market/prices`               Dated market prices

  GET                     `/api/v1/environment/water-quality`   Water-quality records

  GET                     `/api/v1/environment/reports`         Environmental reports

  GET                     `/api/v1/schemes`                     Scheme search

  POST                    `/api/v1/complaints`                  Submit complaint after
                                                                confirmation

  GET                     `/api/v1/complaints/{complaint_id}`   Track authorized
                                                                complaint

  POST                    `/api/v1/documents`                   Ingest approved
                                                                document

  GET                     `/api/v1/health`                      Health check
  -------------------------------------------------------------------------------------

Use Pydantic request/response models. The frontend should use the single
chat endpoint for conversational requests; domain endpoints can power
dashboards and authorized workflows.

## 11. Frontend information architecture

### Fishermen interface

-   AquaPulse AI chat
-   Marathi, Hindi and English selection
-   Text and image input
-   Fish identification results
-   Weather and official alert summary
-   Market price lookup
-   Scheme information
-   Complaint submission and tracking

### Coastal authority interface

-   Overview dashboard
-   Alert and incident records
-   Environmental observations and trends
-   Complaint queue and authorized status updates
-   Data freshness and source indicators
-   Reports with provenance

Design mobile-first for low bandwidth. Show sources and timestamps near
factual claims. Do not use color alone to communicate risk.

## 12. Security, privacy and safety

-   Authentication and role-based authorization.
-   Secrets in environment variables or a secret manager.
-   Upload type and size validation.
-   Restricted complaint and document access.
-   No passwords, tokens or sensitive personal data in logs.
-   Encryption in transit and protected storage.
-   Rate limits and request-size limits.
-   Parameterized SQL and safe file handling.
-   Treat uploaded documents and retrieved text as untrusted data, never
    as system instructions.
-   Audit complaint changes and administrative actions.
-   Require user confirmation before complaint creation.
-   Require authorized human approval before issuing public alerts or
    marking complaints resolved.

## 13. Observability and failure handling

Log request/conversation IDs, selected agents, execution duration,
source retrieval status, freshness, validation outcome, retries and
error category. Never expose stack traces or sensitive prompts to users.

Handle Ollama/API/database outages, empty retrievals, stale/conflicting
records, low-confidence image predictions, invalid uploads and partial
agent failures. A partial response must identify what could not be
checked.

## 14. Testing and evaluation

**Unit tests:** intent classification and routing; agent tools and
schemas; numeric calculations and units; freshness and provenance rules;
document parsing and retrieval filters; image validation and
low-confidence behavior; complaint authorization and state transitions.

**Integration tests:** single-agent and multi-agent queries; parallel
result aggregation; fish image → Fisheries + Market workflow; RAG
answers with source references; stale/missing data; partial agent
failure; Ollama/database outage; complaint submission and tracking
permissions.

**Evaluation metrics:** routing accuracy; answer correctness on a
reviewed test set; source-support rate; stale-data disclosure rate;
image top-1/top-3 accuracy on held-out images; low-confidence abstention
quality; latency and failure rate; complaint workflow correctness.

A successful demo is not proof of production readiness. Maintain a
labelled evaluation set and obtain domain-expert review for high-impact
outputs.

## 15. Suggested project structure

``` text
AquaPulse/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/v1/
│   │   ├── orchestrator/
│   │   │   ├── graph.py
│   │   │   ├── state.py
│   │   │   ├── router.py
│   │   │   ├── planner.py
│   │   │   └── prompts.py
│   │   ├── agents/
│   │   │   ├── weather/
│   │   │   ├── fisheries/
│   │   │   ├── disaster/
│   │   │   ├── market/
│   │   │   ├── environment/
│   │   │   ├── schemes/
│   │   │   └── complaints/
│   │   ├── vision/
│   │   ├── retrieval/
│   │   ├── services/
│   │   ├── database/
│   │   └── schemas/
│   ├── datasets/mock/
│   ├── migrations/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/components/
│   ├── src/pages/
│   ├── src/services/
│   └── package.json
├── storage/documents/
├── storage/uploads/
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── data_dictionary.md
│   └── deployment.md
├── .env.example
├── .gitignore
└── README.md
```

Keep secrets and real user uploads out of Git. Use controlled object
storage in production.

## 16. Implementation roadmap

1.  **Foundation:** repository, dependencies, Ollama, PostgreSQL,
    schemas and source metadata.
2.  **Environment Agent:** mock datasets, deterministic CSV analysis,
    document ingestion, RAG, FastAPI endpoints and tests.
3.  **Specialist agents:** Fisheries, Weather, Disaster, Market, Scheme
    and Complaint agents, each independently tested.
4.  **Orchestration:** typed LangGraph state, intent routing, parallel
    execution, aggregation, validation and limits.
5.  **Fish Vision:** labelled/licensed dataset, classifier evaluation,
    top-k predictions and abstention; connect Fisheries and Market.
6.  **Frontend:** chat, language selection, image upload, dashboards,
    maps, schemes and complaints.
7.  **Pilot readiness:** security, integration and evaluation tests;
    source verification; expert review; limited Palghar pilot with
    mock/live labels.

## 17. MVP acceptance criteria

1.  A user can ask a domain question through one chat interface.
2.  The orchestrator routes to the appropriate agent.
3.  Multi-domain queries invoke multiple agents.
4.  Environment Agent answers from structured mock records and retrieved
    documents.
5.  Mock, historical, unavailable and current data are distinguished.
6.  Fish image classification returns candidates and can abstain when
    uncertain.
7.  Market prices include dates, units and sources.
8.  Final responses identify participating agents and source metadata.
9.  Complaint submission requires confirmation and tracking is
    access-controlled.
10. Automated tests cover routing, retrieval, validation and failure
    paths.

## 18. Key architecture decisions

-   One shared Ollama model initially; separate agent prompts, tools and
    retrieval.
-   LangGraph for explicit orchestration and state transitions.
-   PostgreSQL for structured facts and transactions.
-   ChromaDB for semantic retrieval over approved documents.
-   Deterministic code for calculations, filtering and threshold checks.
-   Dedicated computer vision for fish images.
-   Independently testable and replaceable agents.
-   Clearly labelled mock data until verified sources are integrated.

## 19. References

-   LangGraph Graph API:
    https://langchain-ai.github.io/langgraph/how-tos/multi-agent-network/
-   LangGraph Python reference:
    https://reference.langchain.com/python/langgraph/overview
-   LangGraph multi-agent workflows:
    https://www.langchain.com/blog/langgraph-multi-agent-workflows

------------------------------------------------------------------------

**Project:** AquaPulse\
**Pilot:** Palghar, Maharashtra\
**Next milestone:** Repository foundation, shared data contracts and the
first independently tested Environment Agent.
