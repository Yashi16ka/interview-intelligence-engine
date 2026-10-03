import { useState } from 'react'
import './App.css'

function SourceLinks({ urls }) {
  if (!urls?.length) {
    return null
  }

  const uniqueSources = new Set(urls).size

  return (
    <div className="source-count">
      {uniqueSources} {uniqueSources === 1 ? 'source' : 'sources'}
    </div>
  )
}

function ResultSection({
  eyebrow,
  title,
  items,
  headingKey,
  bodyKey,
  numbered = false,
}) {
  return (
    <section className="result-section">
      <div className="section-heading">
        <span>{eyebrow}</span>
        <h3>{title}</h3>
      </div>

      <div className="result-cards">
        {items.map((item, index) => (
          <article
            className="result-card"
            key={`${item[headingKey]}-${index}`}
          >
            {numbered && (
              <div className="item-number">
                {String(index + 1).padStart(2, '0')}
              </div>
            )}

            <div className="result-card-content">
              <h4>{item[headingKey]}</h4>
              <p>{item[bodyKey]}</p>
              <SourceLinks urls={item.evidence_urls} />
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

function App() {
  const [company, setCompany] = useState('')
  const [role, setRole] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()

    setLoading(true)
    setResult(null)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company: company.trim(),
          role: role.trim(),
        }),
      })

      if (!response.ok) {
        throw new Error(`Research failed (${response.status})`)
      }

      const data = await response.json()
      setResult(data)
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Research failed. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app">
      <nav className="nav">
        <div className="brand">
          <div className="brand-mark">II</div>
          <span>Interview Intelligence</span>
        </div>

        <span className="nav-label">AI-powered research</span>
      </nav>

      <section className="hero">
        <div className="eyebrow">INTERVIEW RESEARCH ENGINE</div>

        <h1>
          Prepare with evidence,
          <span> not guesswork.</span>
        </h1>

        <p className="hero-copy">
          Research a company and role to uncover relevant interview
          topics, practice questions, preparation priorities, and a
          focused study plan grounded in public evidence.
        </p>

        <form className="research-form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="company">Company</label>
            <input
              id="company"
              type="text"
              placeholder="e.g. Stripe"
              value={company}
              onChange={(event) => setCompany(event.target.value)}
            />
          </div>

          <div className="field">
            <label htmlFor="role">Role</label>
            <input
              id="role"
              type="text"
              placeholder="e.g. Software Engineer"
              value={role}
              onChange={(event) => setRole(event.target.value)}
            />
          </div>

          <button
            className="research-button"
            type="submit"
            disabled={
              loading || !company.trim() || !role.trim()
            }
          >
            {loading ? 'Researching…' : 'Research interview'}
            {!loading && <span aria-hidden="true">→</span>}
          </button>
        </form>

        <div className="pipeline">
          <span>Discover</span>
          <span className="pipeline-arrow">→</span>
          <span>Retrieve</span>
          <span className="pipeline-arrow">→</span>
          <span>Rank evidence</span>
          <span className="pipeline-arrow">→</span>
          <span>Synthesize</span>
        </div>

        {error && (
          <div className="request-message error-message">
            {error}
          </div>
        )}

        {result && (
          <section className="results">
            <div className="results-header">
              <div>
                <div className="results-kicker">RESEARCH COMPLETE</div>
                <h2>{result.company}</h2>
                <p>{result.role}</p>
              </div>

              <span className={`status-badge ${result.status}`}>
                {result.status}
              </span>
            </div>

            <div className="stats-grid">
              <div className="stat">
                <strong>{result.stats.raw_count}</strong>
                <span>Collected</span>
              </div>
              <div className="stat">
                <strong>{result.stats.unique_count}</strong>
                <span>Unique</span>
              </div>
              <div className="stat">
                <strong>{result.stats.relevant_count}</strong>
                <span>Relevant</span>
              </div>
            </div>

            {result.status === 'partial' && (
              <div className="partial-notice">
                Evidence was retrieved successfully, but AI synthesis
                is temporarily unavailable.
              </div>
            )}

            {result.intelligence.key_topics.length > 0 && (
              <ResultSection
                eyebrow="WHAT TO KNOW"
                title="Key Topics"
                items={result.intelligence.key_topics}
                headingKey="topic"
                bodyKey="reason"
              />
            )}

            {result.intelligence.likely_questions.length > 0 && (
              <ResultSection
                eyebrow="WHAT TO PRACTICE"
                title="Practice Questions"
                items={result.intelligence.likely_questions}
                headingKey="question"
                bodyKey="rationale"
                numbered
              />
            )}

            {result.intelligence.preparation_priorities.length > 0 && (
              <ResultSection
                eyebrow="WHERE TO FOCUS"
                title="Preparation Priorities"
                items={result.intelligence.preparation_priorities}
                headingKey="priority"
                bodyKey="reason"
              />
            )}

            {result.intelligence.study_plan.length > 0 && (
              <ResultSection
                eyebrow="WHAT TO DO NEXT"
                title="Study Plan"
                items={result.intelligence.study_plan}
                headingKey="action"
                bodyKey="focus"
                numbered
              />
            )}

            {result.evidence.length > 0 && (
              <section className="result-section evidence-section">
                <div className="section-heading">
                  <span>SOURCES</span>
                  <h3>Research Evidence</h3>
                </div>

                <div className="evidence-list">
                  {result.evidence.map((item, index) => (
                    <a
                      className="evidence-item"
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      key={`${item.url}-${index}`}
                    >
                      <div>
                        <span className="evidence-provider">
                          {item.provider}
                        </span>
                        <strong>{item.title}</strong>
                      </div>

                      <span className="evidence-score">
                        Score {item.score} ↗
                      </span>
                    </a>
                  ))}
                </div>
              </section>
            )}
          </section>
        )}
      </section>
    </main>
  )
}

export default App
