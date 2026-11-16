# AquaPulse — Agent Workflow

**Project:** AquaPulse — AI-Powered Smart Fisheries & Coastal Safety System  
**Pilot region:** Palghar, Maharashtra, India  
**Purpose:** Define how the seven specialist agents receive tasks, retrieve evidence, collaborate and return validated results to the central orchestrator.

---

## 1. Workflow goals

AquaPulse presents one assistant to the user. The central LangGraph orchestrator interprets each request and delegates work to one or more specialist agents.

The workflow must:

- Route a question to the smallest useful set of agents.
- Support single-agent and multi-agent requests.
- Allow independent agents to run in parallel when appropriate.
- Preserve source, location, timestamp, units and mock/live status.
- Validate agent results before generating a final answer.
- Return partial results honestly when a source or agent is unavailable.
- Ask a focused clarification when essential information is missing.
- Never invent live weather, official warnings, fish prices, environmental measurements or complaint statuses.

## 2. System workflow at a glance

```text
User
 |
 v
React UI (chat / image / dashboard action)
 |
 v
FastAPI request validation and authentication
 |
 v
Input preprocessor
 |-- detect text or image
 |-- identify language
 |-- normalize location/date/species/market entities
 |-- validate attachments
 |
 v
LangGraph Orchestrator
 |
 +--> Intent classification
 |
 +--> Task planning
 |
 +--> Route selection
       |
       +--> Weather Agent
       +--> Fisheries Agent
       +--> Disaster Agent
       +--> Market Agent
       +--> Environment Agent
       +--> Government Scheme Agent
       +--> Complaint Agent
       |
       v
Agent result collection
 |
 v
Evidence / freshness / policy validation
 |
 v
Response synthesis
 |
 v
Response returned to user with sources and caveats
```

## 3. Standard agent execution contract

Every agent should implement the same callable interface, even though its internal tools differ.

Suggested interface:

```python
async def run_agent(
    query: str,
    location: dict | None = None,
    context: dict | None = None,
) -> dict:
    ...
```

Standard result:

```json
{
  "agent_name": "Environment Agent",
  "status": "success",
  "summary": "Short evidence-based result",
  "data": {},
  "location": {
    "name": "Satpati",
    "district": "Palghar",
    "state": "Maharashtra"
  },
  "sources": [
    {
      "title": "Dataset or document title",
      "publisher": "Source organization",
      "url": null,
      "observed_at": null,
      "published_at": null,
      "retrieved_at": "ISO-8601 timestamp"
    }
  ],
  "warnings": [],
  "is_mock_data": false,
  "confidence": null
}
```

Allowed `status` values:

- `success`: required evidence was retrieved and processed.
- `partial`: some useful evidence exists, but part of the task could not be completed.
- `unavailable`: required evidence or service is unavailable.
- `error`: execution failed.

`confidence` must be omitted or null unless a documented, evaluated method produces it. Do not use the LLM's self-assessment as a calibrated confidence score.

## 4. Central orchestrator workflow

### 4.1 Request intake

1. Receive a request through `POST /api/v1/chat` or a dedicated image endpoint.
2. Authenticate the user where required.
3. Assign a request ID and conversation ID.
4. Validate text length, attachment type and file size.
5. Extract only the context needed for the request.
6. Detect the language and preserve the user's preferred response language.

### 4.2 Intent classification

Classify the request into one or more intents:

| Intent | Agent |
|---|---|
| Weather forecast, wind, waves, rain | Weather |
| Species, fish biology, seasonal fisheries | Fisheries |
| Cyclone, flood, high tide, coastal hazard | Disaster |
| Fish price, market comparison, catch value | Market |
| Water quality, pollution, erosion, mangroves | Environment |
| Government fisheries scheme, eligibility documents | Government Scheme |
| Register or track a complaint | Complaint |

The classifier should return structured output, for example:

```json
{
  "intents": ["weather", "disaster"],
  "agents": ["weather", "disaster"],
  "location": "Palghar",
  "date": "2026-11-06",
  "needs_clarification": false,
  "clarification_question": null
}
```

These values are an example of the schema, not live data.

### 4.3 Task planning

The planner converts the request into a small list of agent tasks. Each task should include:

- task ID
- agent name
- exact question to answer
- required location and time range
- relevant conversation context
- required output fields
- dependencies, if any

Do not dispatch every agent for every question.

### 4.4 Routing and execution

- Use a single-agent path for a single-domain request.
- Use parallel fan-out for independent multi-agent tasks.
- Use sequential execution when one agent needs another agent's output.
- Use a clarification path when a required detail is missing.
- Apply timeouts, bounded retries and a maximum graph-step budget.

### 4.5 Result collection and validation

For every agent result:

1. Validate the response schema.
2. Check that the result belongs to the requested location and time.
3. Check source and observation dates.
4. Check units and data type.
5. Identify mock, historical, stale or unavailable data.
6. Detect contradictions between agents or sources.
7. Keep the source attached to the claim it supports.

### 4.6 Response synthesis

The response generator should:

- Answer the user's question directly.
- Combine compatible findings without hiding disagreements.
- Identify which agents contributed.
- Include relevant dates, units and locations.
- Cite or link available sources.
- State missing information and limitations.
- Avoid unsupported safety, legal or financial conclusions.

## 5. Individual agent workflows

### 5.1 Weather Agent

**Purpose:** Retrieve and explain weather and marine-condition information.

```text
Weather question
      |
Extract location and requested time
      |
Check required location/date
      |
Retrieve approved forecast and official bulletins
      |
Normalize units and timestamps
      |
Check forecast validity and source freshness
      |
Identify official fishermen warnings
      |
Generate concise explanation
      |
Return source, issue time, valid period and caveats
```

**Inputs**
- Query
- Coastal location or supported area
- Requested date/time window
- Optional user context

**Processing**
1. Identify whether the user asks about general weather or marine conditions.
2. Query the configured source adapter.
3. Retrieve official warnings relevant to the location and valid period.
4. Normalize values and units.
5. Mark unavailable fields rather than estimating them.
6. Return a structured result.

**Example questions**
- “What are the available marine conditions for Palghar tomorrow?”
- “Explain the wind and wave information in this bulletin.”
- “Is there an official fishermen warning for this coastal area?”

**Output fields**
- forecast summary
- wind and wave data, when available
- rainfall/visibility, when available
- warning details
- issue and validity times
- source references
- freshness status
- limitations

**Safety rule:** Never state that fishing is safe or authorized solely from a model-generated summary. Highlight official warnings and direct users to follow competent authorities.

### 5.2 Fisheries Agent

**Purpose:** Provide evidence-based fish species and fisheries information.

```text
Fisheries question or identified species
      |
Extract species / location / season
      |
Search species reference data
      |
Retrieve local fisheries and landing-centre records
      |
Retrieve relevant advisory or regulation
      |
Separate general distribution from local observations
      |
Generate species/fisheries explanation
      |
Return references and limitations
```

**Processing**
1. Determine whether the question concerns a species, season, catch record, regulation or fisheries practice.
2. Search curated species data and approved documents.
3. Retrieve local catch/landing-centre observations only when available.
4. Check observation dates and geographic scope.
5. Explain what is known and what is not known.

**Example questions**
- “What is the scientific name of Pomfret?”
- “What seasonal information is documented for this species near Palghar?”
- “Are there fisheries advisories relevant to this question?”

**Output fields**
- common and scientific name
- taxonomy
- habitat and documented distribution
- seasonal information
- local observation records
- relevant advisory/regulation references
- source dates and caveats

**Safety/data rule:** A species photograph or general habitat record cannot prove the exact place where a fish was caught or guarantee that it can be caught at a particular time.

### 5.3 Disaster Agent

**Purpose:** Retrieve and explain official coastal hazard warnings.

```text
Hazard question
      |
Extract location and time
      |
Retrieve official warning sources
      |
Check issue time, validity and affected area
      |
Deduplicate matching alerts
      |
Preserve official severity and instructions
      |
Summarize warning in user's language
      |
Return source and validity details
```

**Processing**
1. Identify hazard category.
2. Query official configured alert sources.
3. Match the requested location against the warning's affected area.
4. Check issue and expiry/validity time.
5. Preserve official wording and severity.
6. Present preparedness instructions from the source.

**Example questions**
- “Are there any official cyclone warnings for this area?”
- “Explain this high-tide advisory.”
- “Which locations are listed in this coastal warning?”

**Output fields**
- hazard type
- official severity/category
- affected area
- issuing authority
- issue time
- validity period
- official instructions
- source link
- retrieval time

**Safety rule:** The agent must not invent alerts, alter official severity, or replace emergency instructions with LLM-generated advice.

### 5.4 Market Agent

**Purpose:** Retrieve dated, comparable fish-market prices.

```text
Price question
      |
Extract species, market, date, grade and unit
      |
Check required fields
      |
Retrieve verified price records
      |
Validate unit, grade and observation date
      |
Compare compatible records
      |
Calculate values using deterministic code
      |
Return prices with source and freshness
```

**Processing**
1. Resolve the fish species or ask for clarification.
2. Resolve the market/location and requested date.
3. Retrieve records from configured sources.
4. Validate currency, unit, grade/size and observation date.
5. Compare only like-for-like records.
6. Calculate indicative value only when quantity and unit are compatible.

**Example questions**
- “What is the latest recorded Pomfret price at this market?”
- “Compare the available Bangda prices across these markets.”
- “Estimate the value of 20 kg using this dated price record.”

**Output fields**
- species
- market
- price
- currency
- unit
- grade/size, if known
- observation date
- source
- comparison basis
- mock/live status

**Data rule:** If no current verified price exists, say so. Do not substitute a generated or mock value.

### 5.5 Environment Agent

**Purpose:** Analyze documented coastal environmental conditions in Palghar.

```text
Environmental question
      |
Classify topic:
water / pollution / shoreline / mangrove / biodiversity
      |
Extract location, parameter and time range
      |
      +----------------------------+
      |                            |
Structured data query        Document/RAG search
      |                            |
CSV / PostgreSQL             PDF / TXT / reports
      |                            |
      +-------------+--------------+
                    |
          Validate units and dates
                    |
          Deterministic analysis
                    |
       Apply configured reference rules
                    |
          Check evidence and gaps
                    |
          Generate explanation
                    |
       Return records, sources and caveats
```

**Supported topics**
- Water quality: pH, DO, BOD, COD, turbidity, salinity and temperature when present in source data.
- Pollution: documented plastic, sewage, industrial discharge, oil-spill or waste incidents.
- Shoreline: documented erosion/accretion observations and historical comparisons.
- Mangroves: coverage, distribution and documented change.
- Biodiversity: documented coastal and marine ecosystem information.
- Trends: comparison of observations across dates and locations.

**Processing**
1. Classify the environmental topic.
2. Extract location, time range and parameter.
3. Query structured data for numeric questions.
4. Use RAG for report/document questions.
5. Validate measurement units, dates, location and source.
6. Apply versioned, configurable reference thresholds where appropriate.
7. Calculate comparisons and trends with deterministic code.
8. Explain findings and limitations.

**Example questions**
- “What water-quality records are available for Satpati?”
- “Compare the recorded pH values at two locations.”
- “Summarize documented pollution incidents in Palghar.”
- “What do these shoreline observations indicate?”
- “Summarize the environmental report I uploaded.”

**Output fields**
- topic and location
- measured parameters and units
- observation dates
- documented findings
- trend/comparison results
- reference threshold and version, if used
- source references
- mock/historical/live status
- data gaps and limitations

**Evidence rule:** Do not state that a location is polluted or environmentally unsafe without supporting evidence. A threshold flag is a screening indicator, not automatically a regulatory finding or full ecological assessment.

### 5.6 Government Scheme Agent

**Purpose:** Explain fisheries-related government schemes using official documents.

```text
Scheme question
      |
Identify scheme / state / user question
      |
Search official scheme documents
      |
Retrieve relevant clauses and dates
      |
Extract eligibility, benefits and documents
      |
Check document version and authority
      |
Generate evidence-grounded explanation
      |
Return official application route and caveats
```

**Processing**
1. Identify the scheme or ask which type of support the user means.
2. Search approved official documents.
3. Retrieve relevant eligibility, benefits, documents and procedure sections.
4. Check publication/update date and jurisdiction.
5. Explain conditions without making an eligibility decision.

**Example questions**
- “What fisheries schemes are listed by the government?”
- “Which documents does this scheme guideline mention?”
- “Where does the official document say to apply?”

**Output fields**
- scheme name
- issuing authority
- purpose
- eligibility criteria
- listed benefits
- required documents
- application route
- official source and document date
- caveats

**Rule:** Do not guarantee eligibility, approval, payment or current availability. Direct users to the official authority for confirmation.

### 5.7 Complaint Agent

**Purpose:** Manage complaint intake and tracking with explicit user confirmation and authorized staff controls.

```text
Complaint request
      |
Identify category and location
      |
Collect description and optional evidence
      |
Validate required fields and consent
      |
Show submission summary to user
      |
User confirms submission?
      |                 |
     No                Yes
      |                 |
Save draft / exit   Create complaint record
                        |
                Generate tracking ID
                        |
                Route to configured queue
                        |
                Return receipt and status
                        |
                Authorized staff updates
                        |
                Status history and closure
```

**Supported categories**
- Environmental pollution
- Coastal waste
- Fisheries-related issue
- Infrastructure or service issue
- Other configured categories

**Required information**
- category
- description
- location
- date/time, if known
- contact method, if needed by the workflow
- consent
- optional image/document

**Processing**
1. Determine that the user intends to submit or track a complaint.
2. Collect only required information.
3. Validate the location and attachment.
4. Display a summary and request confirmation.
5. On confirmation, create a database record and tracking ID.
6. Route to a configured authority queue; do not invent an authority.
7. Return the actual stored status.
8. Permit status changes only to authorized staff and record an audit trail.

**Rule:** Never claim that a complaint was submitted until the database transaction succeeds. Never invent a tracking number, assigned department, acknowledgement or resolution.

## 6. Multi-agent collaboration workflows

### 6.1 Fishing conditions question

**User:** “Summarize the available fishing conditions for tomorrow near Palghar.”

**Agents**
- Weather: forecast and marine-condition records.
- Disaster: official hazard warnings.
- Fisheries: relevant fisheries advisory or restriction information, if available.

**Execution**
1. Orchestrator extracts location and date.
2. Weather and Disaster tasks run in parallel.
3. Fisheries runs when relevant advisory/regulatory information is needed.
4. Validator checks source validity and geographic coverage.
5. Response synthesizer presents findings and clearly identifies missing data.

Do not return a simple “safe to fish” approval.

### 6.2 Fish image plus price

**User:** uploads a fish image and asks, “Identify this fish and tell me its price.”

**Agents/services**
- Fish Vision: candidate species and confidence.
- Fisheries: taxonomy, species facts and documented distribution.
- Market: dated prices for the identified candidate, if the match is sufficiently reliable.

**Execution**
1. Validate and store image securely.
2. Run the classifier and obtain top-k predictions.
3. If confidence is low, ask for a clearer image or return an uncertain result.
4. If the species match is adequate, query Fisheries and Market.
5. Market validates grade, unit, market and date.
6. Synthesize species facts and available price records.

Do not infer exact catch location or current catch availability from the image.

### 6.3 Coastal pollution question and complaint

**User:** “There is waste near my coastal area. What should I do, and can I report it?”

**Agents**
- Environment: retrieve documented environmental context, if available.
- Complaint: collect and submit a report only after confirmation.

**Execution**
1. Environment checks whether relevant records exist; it must not assume the user's observation is already verified.
2. Assistant explains the distinction between the user's report and independently verified records.
3. Complaint Agent collects category, location and description.
4. User reviews and confirms.
5. Complaint is stored and routed according to configured rules.
6. User receives the actual tracking identifier and status.

### 6.4 Water quality report question

**User:** “Summarize the water-quality condition at Satpati from the uploaded report.”

**Agent**
- Environment only, unless another domain is explicitly required.

**Execution**
1. Validate the uploaded report.
2. Extract text/tables and preserve page/record references.
3. Retrieve relevant passages and measurements.
4. Check units, sample date and location.
5. Calculate any requested comparison using deterministic code.
6. Return a summary with source/page references and limitations.

### 6.5 Government scheme eligibility question

**User:** “Can I apply for this fisheries scheme?”

**Agent**
- Government Scheme Agent.

**Execution**
1. Identify the scheme and jurisdiction.
2. Retrieve the latest available official guideline.
3. Ask for only the missing eligibility details that the document requires.
4. Compare user-provided details against published criteria.
5. Explain which criteria appear to match or remain unknown.
6. Direct the user to the official authority for final determination.

Do not store sensitive information unless required and consented to.

## 7. Fish Vision workflow in detail

The vision module is a service used by the orchestrator, not an eighth conversational agent.

**Input**
- Image file
- Optional user-provided local name
- Optional capture location/date, if the user chooses to provide it

**Processing**
1. Validate MIME type, extension and file size.
2. Decode and preprocess the image.
3. Run the trained PyTorch classifier.
4. Return top-k predictions and calibrated confidence.
5. Apply an unknown/abstention threshold established through validation.
6. Pass supported candidate species to Fisheries Agent.
7. Pass candidate species and required market filters to Market Agent.
8. Validate all retrieved records before synthesis.

**Example response schema**

```json
{
  "predicted_species": null,
  "scientific_name": null,
  "top_predictions": [],
  "confidence": null,
  "identification_status": "uncertain",
  "fisheries_information": {},
  "market_prices": [],
  "sources": [],
  "warnings": [
    "Species identification is uncertain; a clearer image may be needed."
  ]
}
```

Possible `identification_status` values: `identified`, `uncertain`, `unsupported`.

A classifier confidence score is meaningful only if the model has been evaluated and calibrated on representative held-out images. Include an unknown class or abstention behavior for species outside the training set.

## 8. LangGraph node plan

Suggested graph nodes:

| Node | Responsibility |
|---|---|
| `validate_request` | Validate request and permissions |
| `preprocess_input` | Normalize text, language and entities |
| `route_input_type` | Select text or image path |
| `classify_image` | Call Fish Vision service |
| `classify_intent` | Identify domain intents |
| `plan_tasks` | Build minimal agent task list |
| `route_agents` | Dispatch selected agents |
| `run_weather` | Invoke Weather Agent |
| `run_fisheries` | Invoke Fisheries Agent |
| `run_disaster` | Invoke Disaster Agent |
| `run_market` | Invoke Market Agent |
| `run_environment` | Invoke Environment Agent |
| `run_scheme` | Invoke Government Scheme Agent |
| `run_complaint` | Invoke Complaint Agent |
| `collect_results` | Merge agent results |
| `validate_evidence` | Check schema, sources and freshness |
| `synthesize_response` | Compose user-facing answer |
| `check_response` | Apply safety and output policy |
| `request_clarification` | Ask one essential question |

The actual graph can use a task-dispatch node and reusable agent runner rather than requiring a separate hard-coded graph branch for every agent. Keep routing explicit and testable.

## 9. Shared state design

Illustrative state:

```python
class AquaPulseState(TypedDict, total=False):
    request_id: str
    conversation_id: str
    user_id: str | None
    query: str
    language: str
    location: dict
    requested_time_range: dict
    input_type: str
    image_asset_id: str | None
    image_predictions: list[dict]
    intents: list[str]
    planned_tasks: list[dict]
    agent_results: list[dict]
    evidence: list[dict]
    warnings: list[str]
    errors: list[dict]
    needs_clarification: bool
    clarification_question: str | None
    final_response: dict
```

State management requirements:
- Use a reducer for concurrent agent results.
- Avoid mutable global state.
- Keep user data scoped to the request and authorized conversation.
- Do not pass unnecessary personal information to agents.
- Set a maximum graph step count and per-agent timeouts.
- Make retries bounded and idempotent where possible.

## 10. Data and source workflow

For every external or uploaded data source:

1. Register source name, publisher, access method and license/terms.
2. Record geographic coverage and supported variables.
3. Normalize dates, units and location identifiers.
4. Store original observation/publication date separately from retrieval time.
5. Mark simulated data with `is_mock = true`.
6. Keep source references with derived results.
7. Define freshness rules per source type.
8. Monitor ingestion errors and missing periods.

Use PostgreSQL/Pandas for structured numeric queries. Use ChromaDB for semantic retrieval over approved documents. Do not rely on vector similarity alone for exact prices, measurements or date comparisons.

## 11. Error and fallback workflow

| Failure | Expected behavior |
|---|---|
| Ollama unavailable | Return service-unavailable/partial response; do not fabricate |
| One agent timeout | Return other validated results and identify the missing agent |
| All sources empty | Say information is unavailable |
| Stale data | Label as historical/stale and show date |
| Conflicting sources | Present the conflict and source dates; do not silently choose |
| Invalid image | Explain supported formats and request a valid upload |
| Low-confidence image | Abstain from identification or show uncertain candidates |
| Database unavailable | Do not claim a write or complaint submission succeeded |
| RAG has no evidence | State that no relevant document evidence was found |
| Missing required location/date | Ask one focused clarification |

## 12. Logging and audit

Log:
- request ID
- selected agent names
- execution start/end and duration
- source retrieval outcomes
- freshness checks
- validation outcomes
- retry count
- error category

For complaint workflows, audit creation, assignment, status changes and closure with actor, timestamp and change reason.

Do not log passwords, access tokens, unnecessary personal information or raw uploaded images.

## 13. Workflow testing checklist

### Routing tests
- Weather-only question routes to Weather.
- Fisheries-only question routes to Fisheries.
- Environment-only question routes to Environment.
- Market-only question routes to Market.
- Disaster-only question routes to Disaster.
- Scheme question routes to Scheme.
- Complaint submission/tracking routes to Complaint.
- Multi-domain question selects only the necessary agents.
- General conversation does not activate all agents.

### Collaboration tests
- Weather + Disaster result aggregation.
- Fisheries + Market for a fish image.
- Environment result plus Complaint submission after user confirmation.
- Partial response when one agent fails.
- Conflicting evidence handling.

### Data-quality tests
- Historical data is not labelled live.
- Mock data is always labelled mock.
- Price units and grades are checked.
- Environmental measurements retain units and observation dates.
- Official warning validity is checked.
- Sources remain attached to the claims they support.

### Security tests
- Unauthorized users cannot access complaint records.
- User uploads are validated.
- Complaint creation requires confirmation.
- Agent tools cannot access unrelated data or perform unauthorized actions.

## 14. Recommended implementation order

1. Define common Pydantic schemas and the shared LangGraph state.
2. Build and test the Environment Agent workflow.
3. Build Fisheries and Market workflows.
4. Build Weather and Disaster workflows.
5. Build Government Scheme workflow.
6. Build Complaint workflow with authorization and confirmation.
7. Implement the orchestrator's single-agent routing.
8. Add multi-agent planning, parallel execution and aggregation.
9. Add Fish Vision and connect it to Fisheries and Market.
10. Add frontend integration and end-to-end tests.

Build each agent independently with mocked adapters first. Replace mock adapters with verified sources incrementally. Do not describe the system as live until the actual source integration, freshness and failure behavior have been tested.

---

**Project:** AquaPulse  
**Pilot:** Palghar, Maharashtra  
**Related document:** `architecture.md`  
**Next milestone:** Common agent contract, shared state and a tested Environment Agent workflow.
