# Interview Intelligence Engine

A concurrent multi-source research engine for evidence-grounded technical interview preparation.

Instead of relying on a single source or sending every page through the same retrieval path, the engine discovers information across multiple source types, retrieves each source using the appropriate mechanism, normalizes and ranks the evidence by research purpose, and synthesizes it into grounded interview topics, practice questions, preparation priorities, and a study plan with source citations.

## Why I Built It

Interview preparation information is fragmented across job postings, interview experiences, engineering content, and other public sources. Researching each source sequentially is slow, and treating every source identically can create unnecessary overhead.

This project explores a more structured approach:

- run independent research operations concurrently
- separate discovery from retrieval
- use structured APIs when available
- use browser automation only when necessary
- preserve source provenance throughout the pipeline
- isolate individual source failures
- rank evidence differently depending on what the user is trying to learn

## Current Architecture

```text
Company + Role
      |
      v
Research Query Builder
      |
      +---------------------------+
      |                           |
      v                           v
General Discovery            ATS Discovery
  Hacker News                Lever / Ashby
      |                           |
      v                           v
Browser Retrieval         Structured API Content
   Playwright                      |
      |                            |
      +-------------+--------------+
                    |
                    v
              Evidence Items
                    |
                    v
           PostgreSQL Cache
                    |
                    v
        Normalize + Deduplicate
                    |
                    v
          Purpose-Aware Ranking
                    |
                    v
             Ranked Evidence
                    |
                    v
       Evidence-Grounded Gemini
               Synthesis
                    |
                    v
        Interview Intelligence
     Topics / Questions / Plan
                    |
                    v
        Resolved Source URLs
```

A key design decision is that ATS job descriptions do **not** need to be reopened in a browser. Lever and Ashby already expose useful structured job content, so the engine converts that API content directly into evidence while reserving Playwright for sources that actually require browser retrieval.

## Current Capabilities

- FastAPI service with health and research endpoints
- Company- and role-agnostic research query generation
- Concurrent source orchestration with `asyncio`
- Hacker News discovery through its public API
- Automatic public ATS discovery for Lever and Ashby
- Direct job-description evidence extraction from ATS APIs
- Role- and seniority-aware ATS job filtering
- Headless browser retrieval with Playwright
- Bounded browser concurrency
- Detection of HTTP error, access-denied, and verification pages
- URL, title, and evidence normalization and deduplication
- Purpose-aware evidence ranking across five research purposes
- PostgreSQL-backed evidence caching
- Evidence-grounded Gemini synthesis with structured output
- Source citations resolved from retrieved evidence IDs
- Retry handling for transient synthesis failures
- Graceful partial responses when synthesis is unavailable or invalid
- Failure isolation across independent retrieval paths
- 165 automated tests across the pipeline

## Tech Stack

**Frontend:** React, Vite
**Backend:** Python, FastAPI, Pydantic
**Concurrency:** asyncio
**HTTP:** HTTPX
**Browser Automation:** Playwright
**Database:** PostgreSQL, asyncpg
**AI Synthesis:** Gemini
**Testing:** pytest, Oxlint

## Engineering Decisions

### Source-specific retrieval

The engine does not force every source through browser automation. Structured ATS data is retrieved directly over HTTP, while general web sources can use Playwright.

### Concurrent I/O

Independent discovery and collection operations run concurrently rather than sequentially. In a controlled three-source I/O benchmark, median retrieval time decreased from approximately **1.204s to 0.502s**, a **58.3% reduction** compared with sequential execution.

This measures the concurrency architecture under controlled I/O conditions and is not presented as production latency.

### Bounded browser concurrency

Concurrency improves I/O throughput, but unbounded browser fan-out can consume unnecessary resources. Browser retrieval therefore limits simultaneous navigation and extraction operations.

### Failure isolation

Source failures are isolated so one unavailable provider does not invalidate successful evidence from other providers.

### Purpose-aware relevance

A job description and an interview experience should not be evaluated using identical relevance rules. Evidence is scored according to its research purpose rather than through one generic keyword filter.

### Evidence-grounded synthesis

Gemini receives ranked evidence produced by the retrieval pipeline rather than only a company and role. The model references evidence IDs in structured output, and those IDs are resolved back to the original source URLs before the API response is returned.

### Graceful synthesis degradation

If synthesis is unavailable, malformed, or references invalid evidence, the research endpoint preserves successful retrieval results and returns a `partial` response instead of failing the entire request.

## Testing

The current test suite contains **165 passing tests** covering concurrent orchestration, failure isolation, browser retrieval and bounded concurrency, discovery and deduplication, evidence provenance, purpose-aware relevance, ATS discovery and role matching, PostgreSQL caching, ResearchEngine integration, Gemini synthesis, evidence resolution, and graceful handling of invalid synthesis responses.

Run the suite with:

```bash
pytest -q
```

## Project Status

The core end-to-end pipeline is implemented: discovery, source-specific retrieval, evidence processing, PostgreSQL caching, purpose-aware ranking, and evidence-grounded interview-intelligence synthesis.

The implementation emphasizes a tested, inspectable pipeline in which retrieved evidence remains traceable through ranking and synthesis.

## Running Locally

```bash
git clone https://github.com/Yashi16ka/interview-intelligence-engine.git
cd interview-intelligence-engine

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium

# Create the local PostgreSQL database
createdb interview_intelligence

# Optional if using a non-default PostgreSQL connection
# export DATABASE_URL="postgresql://localhost/interview_intelligence"

# Optional: enables Gemini synthesis
# export GEMINI_API_KEY="your-api-key"

uvicorn app.main:app --reload
```

In a second terminal, start the React interface:

```bash
cd frontend
npm install
npm run dev
```

Open localhost:5173 in your browser. The frontend sends research requests to the FastAPI service running at localhost:8000.

By default, the application connects to `postgresql://localhost/interview_intelligence`. `DATABASE_URL` can override this connection. Without `GEMINI_API_KEY`, the service can still start and retrieve evidence, but synthesis is unavailable and research responses can return with `partial` status.

Run the tests with:

```bash
pytest -q
```

## Development Approach

The project was built incrementally with tests around each architectural layer. The commit history reflects the progression from concurrent source collection to evidence processing, purpose-aware relevance, automatic ATS discovery, structured ATS retrieval, PostgreSQL caching, evidence-grounded synthesis, and retrieval and synthesis failure handling.
