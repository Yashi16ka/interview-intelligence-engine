# Interview Intelligence Engine

A concurrent multi-source research engine for evidence-grounded technical interview preparation.

Instead of relying on a single source or sending every page through the same retrieval path, the engine discovers information across multiple source types, retrieves each source using the appropriate mechanism, normalizes and deduplicates the evidence, and ranks it by research purpose.

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
      |                     Lever / Ashby
      v                           |
Browser Retrieval                 v
   Playwright              Structured API Content
      |                           |
      +-------------+-------------+
                    |
                    v
             Evidence Items
                    |
                    v
       Normalize + Deduplicate
                    |
                    v
        Purpose-Aware Ranking
                    |
                    v
          Research Evidence
```

A key design decision is that ATS job descriptions do **not** need to be reopened in a browser. Lever and Ashby already expose useful structured job content, so the engine converts that API content directly into evidence while reserving Playwright for sources that actually require browser retrieval.

## Current Capabilities

- FastAPI service foundation with health and research endpoints
- Company- and role-agnostic research query generation
- Concurrent source orchestration with `asyncio`
- Failure isolation across independent collectors and discovery providers
- Headless browser retrieval with Playwright
- URL and title normalization and deduplication
- Purpose-aware evidence ranking for interview experiences, interview questions, technical interviews, role requirements, and company engineering context
- Automatic public ATS discovery for Lever and Ashby
- Role-aware filtering of ATS job postings
- Direct extraction of job-description evidence from ATS APIs
- Evidence provenance preserved across discovery and retrieval
- 101 automated tests across the research pipeline

## Tech Stack

**Backend:** Python, FastAPI, Pydantic
**Concurrency:** asyncio
**HTTP:** HTTPX
**Browser Automation:** Playwright
**Testing:** pytest

## Engineering Decisions

### Source-specific retrieval

The engine does not force every source through browser automation. Structured ATS data is retrieved directly over HTTP, while general web sources can use Playwright.

### Concurrent I/O

Independent discovery and collection operations run concurrently rather than sequentially. In a controlled three-source I/O benchmark, median retrieval time decreased from approximately **1.204s to 0.502s**, a **58.3% reduction** compared with sequential execution.

This measures the concurrency architecture under controlled I/O conditions and is not presented as production latency.

### Failure isolation

Source failures are isolated so one unavailable provider does not invalidate successful evidence from other providers.

### Purpose-aware relevance

A job description and an interview experience should not be evaluated using identical relevance rules. Evidence is scored according to its research purpose rather than through one generic keyword filter.

## Testing

The current test suite contains **101 passing tests** covering concurrent orchestration, failure isolation, browser collection, discovery and deduplication, evidence provenance, relevance scoring, ATS discovery and role matching, direct ATS evidence extraction, and ResearchEngine integration.

Run the suite with:

```bash
pytest -v
```

## Project Status

This project is actively under development. Current work focuses on the research and evidence pipeline.

Planned next stages include:

- PostgreSQL persistence and caching
- evidence aggregation and interview-intelligence synthesis
- generated interview questions and preparation plans
- evidence-backed citations in generated output
- retry, backoff, rate-limiting, and observability improvements
- API and demo polish

## Running Locally

```bash
git clone https://github.com/Yashi16ka/interview-intelligence-engine.git
cd interview-intelligence-engine

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium

uvicorn app.main:app --reload
```

Run the tests with:

```bash
pytest -v
```

## Development Approach

The project is being built incrementally with tests around each architectural layer. The commit history reflects the progression from concurrent source collection to evidence processing, purpose-aware relevance, automatic ATS discovery, and direct structured evidence retrieval.
