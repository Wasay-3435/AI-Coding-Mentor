
import { useState } from "react";
import {
  createSession,
  analyzeCode,
  generateExercises,
  evaluateExercise,
} from "./services/api";
import "./App.css";

const starterCode = {
  Python:
    'def greet(name):\n    message = "Hello, "\n    return message + name\n\nprint(greet("World"))',
  JavaScript:
    'function greet(name) {\n  const message = "Hello, ";\n  return message + name;\n}\n\nconsole.log(greet("World"));',
  Java:
    'public class Main {\n    public static String greet(String name) {\n        String message = "Hello, ";\n        return message + name;\n    }\n\n    public static void main(String[] args) {\n        System.out.println(greet("World"));\n    }\n}',
  "C++":
    '#include <iostream>\n#include <string>\nusing namespace std;\n\nstring greet(string name) {\n    return "Hello, " + name;\n}\n\nint main() {\n    cout << greet("World") << endl;\n    return 0;\n}',
};

function App() {
  const [language, setLanguage] = useState("Python");
  const [code, setCode] = useState(starterCode.Python);
  const [activeTab, setActiveTab] = useState("Analysis");

  const [sessionId, setSessionId] = useState(null);

  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [exercises, setExercises] = useState([]);
  const [exercisesLoading, setExercisesLoading] = useState(false);
  const [exercisesError, setExercisesError] = useState("");

  // New state: each exercise has its own answer and evaluation result.
  const [exerciseAnswers, setExerciseAnswers] = useState({});
  const [evaluationResults, setEvaluationResults] = useState({});
  const [evaluatingExercises, setEvaluatingExercises] = useState({});
  const [evaluationErrors, setEvaluationErrors] = useState({});

  async function ensureSession() {
    if (sessionId) return sessionId;

    const session = await createSession();
    const id = session.session_id ?? session.id;

    if (!id) {
      throw new Error("The backend did not return a session ID.");
    }

    setSessionId(id);
    return id;
  }

  function clearExerciseResults() {
    setExercises([]);
    setExercisesError("");
    setExerciseAnswers({});
    setEvaluationResults({});
    setEvaluatingExercises({});
    setEvaluationErrors({});
  }

  async function handleAnalyze() {
    if (!code.trim()) {
      setError("Please enter some code before requesting an analysis.");
      setAnalysis(null);
      setActiveTab("Analysis");
      return;
    }

    setLoading(true);
    setError("");
    setAnalysis(null);
    clearExerciseResults();
    setActiveTab("Analysis");

    try {
      const currentSessionId = await ensureSession();

      const result = await analyzeCode({
        language,
        code,
        sessionId: currentSessionId,
      });

      setAnalysis(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while analyzing your code."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateExercises() {
    if (!analysis) {
      setExercisesError(
        "Analyze your code first to generate personalized exercises."
      );
      return;
    }

    setExercisesLoading(true);
    setExercisesError("");
    setExercises([]);
    setExerciseAnswers({});
    setEvaluationResults({});
    setEvaluationErrors({});

    try {
      const currentSessionId = await ensureSession();

      const result = await generateExercises({
        language,
        code,
        analysis,
        sessionId: currentSessionId,
        count: 3,
      });

      if (!Array.isArray(result.exercises)) {
        throw new Error(
          "The backend response did not contain an exercises list."
        );
      }

      setExercises(result.exercises);
    } catch (err) {
      setExercisesError(
        err instanceof Error
          ? err.message
          : "Something went wrong while generating exercises."
      );
    } finally {
      setExercisesLoading(false);
    }
  }

  // New handler: submit one exercise answer to the backend.
  async function handleEvaluateExercise(exercise, index) {
    const answer = exerciseAnswers[index] ?? "";

    if (!answer.trim()) {
      setEvaluationErrors((previous) => ({
        ...previous,
        [index]: "Please enter your solution before submitting.",
      }));
      return;
    }

    setEvaluatingExercises((previous) => ({
      ...previous,
      [index]: true,
    }));

    setEvaluationErrors((previous) => ({
      ...previous,
      [index]: "",
    }));

    try {
      const currentSessionId = await ensureSession();

      const result = await evaluateExercise({
        language,
        exercise,
        answer,
        sessionId: currentSessionId,
      });

      setEvaluationResults((previous) => ({
        ...previous,
        [index]: result,
      }));
    } catch (err) {
      setEvaluationErrors((previous) => ({
        ...previous,
        [index]:
          err instanceof Error
            ? err.message
            : "Something went wrong while evaluating your answer.",
      }));
    } finally {
      setEvaluatingExercises((previous) => ({
        ...previous,
        [index]: false,
      }));
    }
  }

  function changeLanguage(nextLanguage) {
    setLanguage(nextLanguage);
    setCode(starterCode[nextLanguage]);
    setAnalysis(null);
    setError("");
    clearExerciseResults();
  }

  function handleCodeChange(value) {
    setCode(value);
    setAnalysis(null);
    setError("");
    clearExerciseResults();
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="AI Coding Mentor home">
          <div className="brand-icon">&lt;/&gt;</div>
          <div className="brand-copy">
            <span className="brand-name">
              CodeMentor<span> AI</span>
            </span>
            <span className="brand-subtitle">
              YOUR PERSONAL CODING COACH
            </span>
          </div>
        </a>

        <div className="topbar-center">
          <span className="status-dot" />
          <span>Backend connected</span>
          <span className="topbar-divider">/</span>
          <span className="muted">
            {sessionId ? "Learning session active" : "New learning session"}
          </span>
        </div>

        <div className="topbar-right">
          <span className="avatar">S</span>
        </div>
      </header>

      <main className="workspace">
        <section className="page-heading">
          <div>
            <div className="eyebrow">YOUR LEARNING WORKSPACE</div>
            <h1>
              Write code. <span>Understand more.</span>
            </h1>
            <p>
              Practice programming with a mentor that helps you learn, not
              just fix.
            </p>
          </div>

          <div className="session-chip">
            <span className="session-indicator" />
            {sessionId ? "Session active" : "Practice mode"}
          </div>
        </section>

        <section className="workspace-grid">
          <div className="editor-panel panel">
            <div className="panel-heading editor-heading">
              <div className="panel-title">
                <span className="file-icon">{"</>"}</span>
                <span>Code editor</span>
                <span className="file-tab">
                  main.
                  {language === "Python"
                    ? "py"
                    : language === "JavaScript"
                      ? "js"
                      : language === "Java"
                        ? "java"
                        : "cpp"}
                </span>
              </div>

              <label className="language-select">
                <span className="sr-only">Programming language</span>
                <select
                  value={language}
                  onChange={(event) => changeLanguage(event.target.value)}
                  disabled={loading || exercisesLoading}
                >
                  {Object.keys(starterCode).map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="editor-body">
              <div className="line-numbers" aria-hidden="true">
                {code.split("\n").map((_, index) => (
                  <span key={index}>{index + 1}</span>
                ))}
              </div>

              <label className="sr-only" htmlFor="code-input">
                Your code
              </label>
              <textarea
                id="code-input"
                className="code-input"
                spellCheck="false"
                autoCapitalize="off"
                autoComplete="off"
                value={code}
                disabled={loading || exercisesLoading}
                onChange={(event) => handleCodeChange(event.target.value)}
                aria-label="Code editor"
              />
            </div>

            <div className="editor-footer">
              <span>
                <span className="footer-dot" />
                {language}
              </span>
              <span>{code.split("\n").length} lines</span>
              <span>UTF-8</span>
            </div>

            <div className="editor-actions">
              <div className="editor-hint">
                <span className="hint-symbol">⌘</span>
                Learn by doing
              </div>

              <button
                className="primary-button"
                onClick={handleAnalyze}
                disabled={loading || exercisesLoading}
              >
                <span>{loading ? "◌" : "✦"}</span>
                {loading ? "Analyzing..." : "Analyze code"}
                {!loading && <span className="button-arrow">→</span>}
              </button>
            </div>
          </div>

          <section className="mentor-panel panel">
            <div className="mentor-heading">
              <div className="mentor-identity">
                <div className="mentor-icon">✳</div>
                <div>
                  <h2>AI Mentor</h2>
                  <span>Your personal programming guide</span>
                </div>
              </div>
              <span className="ai-badge">AI POWERED</span>
            </div>

            <nav className="mentor-tabs" aria-label="Mentor sections">
              {["Analysis", "Exercises", "Progress"].map((tab) => (
                <button
                  key={tab}
                  className={`mentor-tab ${activeTab === tab ? "active" : ""}`}
                  onClick={() => setActiveTab(tab)}
                >
                  <span>
                    {tab === "Analysis"
                      ? "◈"
                      : tab === "Exercises"
                        ? "⌘"
                        : "↗"}
                  </span>
                  {tab}
                </button>
              ))}
            </nav>

            <div className="mentor-content">
              {activeTab === "Analysis" && (
                <>
                  {loading && (
                    <div className="welcome-card">
                      <div className="welcome-icon">✦</div>
                      <div>
                        <h3>Reviewing your code...</h3>
                        <p>
                          The AI mentor is analyzing your code. This may take
                          a few seconds.
                        </p>
                      </div>
                    </div>
                  )}

                  {error && (
                    <div className="demo-notice" role="alert">
                      <span>!</span>
                      <div>
                        <strong>Analysis failed</strong>
                        <p>{error}</p>
                        <button
                          className="secondary-button"
                          onClick={handleAnalyze}
                          disabled={loading}
                        >
                          Try again
                        </button>
                      </div>
                    </div>
                  )}

                  {!loading && !error && !analysis && (
                    <>
                      <div className="welcome-card">
                        <div className="welcome-icon">✦</div>
                        <div>
                          <h3>Let's understand your code</h3>
                          <p>
                            Click Analyze code to receive a real AI-generated
                            review of your submission.
                          </p>
                        </div>
                      </div>

                      <div className="section-label">WHAT YOU'LL GET</div>

                      <div className="feature-row">
                        <div className="feature-icon purple">⌕</div>
                        <div>
                          <h4>Code review</h4>
                          <p>
                            Understand logic, bugs and possible improvements.
                          </p>
                        </div>
                      </div>

                      <div className="feature-row">
                        <div className="feature-icon green">✓</div>
                        <div>
                          <h4>Actionable feedback</h4>
                          <p>
                            Learn why a change matters, not just what to
                            change.
                          </p>
                        </div>
                      </div>

                      <div className="feature-row">
                        <div className="feature-icon orange">✧</div>
                        <div>
                          <h4>Personalized practice</h4>
                          <p>
                            Turn what you learn into your next coding
                            challenge.
                          </p>
                        </div>
                      </div>

                      <div className="mentor-tip">
                        <span>✧</span>
                        <p>
                          <strong>Learning tip</strong>
                          <br />
                          Try to explain what your code does before asking for
                          feedback.
                        </p>
                      </div>
                    </>
                  )}

                  {!loading && !error && analysis && (
                    <div className="analysis-results">
                      <div className="result-heading">
                        <span className="result-status">✓</span>
                        <div>
                          <h3>Analysis complete</h3>
                          <p>Your code has been reviewed.</p>
                        </div>
                      </div>

                      <div className="section-label">SUMMARY</div>
                      <div className="result-card">
                        <p>{analysis.summary}</p>
                      </div>

                      <div className="section-label">
                        ISSUES ({analysis.issues?.length ?? 0})
                      </div>

                      {analysis.issues?.length ? (
                        analysis.issues.map((issue, index) => (
                          <div className="issue-card" key={index}>
                            <div className="issue-meta">
                              <span className="issue-type">{issue.type}</span>
                              <span
                                className={`severity severity-${String(
                                  issue.severity
                                ).toLowerCase()}`}
                              >
                                {issue.severity}
                              </span>
                            </div>
                            <p>{issue.explanation}</p>
                          </div>
                        ))
                      ) : (
                        <div className="result-card">
                          <p>No issues were reported by the analysis.</p>
                        </div>
                      )}

                      <div className="section-label">SUGGESTIONS</div>

                      {analysis.suggestions?.length ? (
                        <ul className="suggestion-list">
                          {analysis.suggestions.map((suggestion, index) => (
                            <li key={index}>{suggestion}</li>
                          ))}
                        </ul>
                      ) : (
                        <div className="result-card">
                          <p>No additional suggestions were provided.</p>
                        </div>
                      )}

                      <button
                        className="secondary-button"
                        onClick={() => setActiveTab("Exercises")}
                      >
                        Continue to practice →
                      </button>
                    </div>
                  )}
                </>
              )}

              {activeTab === "Exercises" && (
                <div className="exercises-view">
                  <div className="exercise-intro">
                    <div>
                      <div className="section-label">PERSONALIZED PRACTICE</div>
                      <h3>Build your skills</h3>
                      <p>
                        Exercises are generated from your code and its analysis.
                      </p>
                    </div>

                    <button
                      className="primary-button generate-button"
                      onClick={handleGenerateExercises}
                      disabled={exercisesLoading || loading || !analysis}
                    >
                      {exercisesLoading
                        ? "Generating..."
                        : "✦ Generate exercises"}
                    </button>
                  </div>

                  {!analysis && (
                    <div className="empty-state">
                      <div className="empty-icon">⌘</div>
                      <h3>Analysis comes first</h3>
                      <p>
                        Analyze your code before generating exercises tailored
                        to your learning needs.
                      </p>
                      <button
                        className="secondary-button"
                        onClick={() => setActiveTab("Analysis")}
                      >
                        Go to analysis →
                      </button>
                    </div>
                  )}

                  {exercisesError && (
                    <div className="demo-notice" role="alert">
                      <span>!</span>
                      <div>
                        <strong>Exercise generation failed</strong>
                        <p>{exercisesError}</p>
                        <button
                          className="secondary-button"
                          onClick={handleGenerateExercises}
                          disabled={exercisesLoading || !analysis}
                        >
                          Try again
                        </button>
                      </div>
                    </div>
                  )}

                  {exercisesLoading && (
                    <div className="welcome-card">
                      <div className="welcome-icon">✦</div>
                      <div>
                        <h3>Creating your exercises...</h3>
                        <p>
                          The AI mentor is preparing practice tasks based on
                          your analysis.
                        </p>
                      </div>
                    </div>
                  )}

                  {!exercisesLoading &&
                    !exercisesError &&
                    exercises.length === 0 &&
                    analysis && (
                      <div className="empty-state exercise-empty">
                        <div className="empty-icon">✧</div>
                        <h3>Ready when you are</h3>
                        <p>
                          Generate a set of practice exercises to reinforce
                          what you've learned.
                        </p>
                      </div>
                    )}

                  {!exercisesLoading &&
                    exercises.map((exercise, index) => (
                      <article className="exercise-card" key={index}>
                        <div className="exercise-card-heading">
                          <span className="exercise-number">
                            {String(index + 1).padStart(2, "0")}
                          </span>
                          <span
                            className={`difficulty difficulty-${String(
                              exercise.difficulty
                            ).toLowerCase()}`}
                          >
                            {exercise.difficulty}
                          </span>
                        </div>

                        <h3>{exercise.title}</h3>
                        <div className="exercise-concept">
                          {exercise.concept}
                        </div>
                        <p className="exercise-instructions">
                          {exercise.instructions}
                        </p>

                        {exercise.starter_code && (
                          <>
                            <div className="section-label">STARTER CODE</div>
                            <pre className="exercise-code">
                              <code>{exercise.starter_code}</code>
                            </pre>
                          </>
                        )}

                        {exercise.expected_skills?.length > 0 && (
                          <div className="skill-list">
                            {exercise.expected_skills.map((skill, skillIndex) => (
                              <span key={skillIndex} className="skill-chip">
                                {skill}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Added answer editor, submission and feedback. */}
                        <div className="answer-section">
                          <label
                            className="answer-label"
                            htmlFor={`exercise-answer-${index}`}
                          >
                            Your solution
                          </label>

                          <textarea
                            id={`exercise-answer-${index}`}
                            className="answer-editor"
                            value={exerciseAnswers[index] ?? ""}
                            onChange={(event) => {
                              const value = event.target.value;

                              setExerciseAnswers((previous) => ({
                                ...previous,
                                [index]: value,
                              }));

                              setEvaluationErrors((previous) => ({
                                ...previous,
                                [index]: "",
                              }));
                            }}
                            placeholder="Write your solution here..."
                            spellCheck={false}
                            rows={7}
                          />

                          <button
                            type="button"
                            className="primary-button evaluate-button"
                            onClick={() =>
                              handleEvaluateExercise(exercise, index)
                            }
                            disabled={Boolean(evaluatingExercises[index])}
                          >
                            {evaluatingExercises[index]
                              ? "Evaluating..."
                              : "✦ Submit for evaluation"}
                          </button>

                          {evaluationErrors[index] && (
                            <div className="demo-notice evaluation-error" role="alert">
                              <span>!</span>
                              <div>
                                <strong>Evaluation failed</strong>
                                <p>{evaluationErrors[index]}</p>
                              </div>
                            </div>
                          )}

                          {evaluationResults[index] && (
                            <div className="evaluation-result">
                              <div className="evaluation-heading">
                                <h4>Evaluation results</h4>
                                <span className="evaluation-score">
                                  {evaluationResults[index].score}/100
                                </span>
                              </div>

                              <p>
                                <strong>Result: </strong>
                                {evaluationResults[index].is_correct
                                  ? "Correct"
                                  : "Needs improvement"}
                              </p>

                              {evaluationResults[index].feedback && (
                                <p>{evaluationResults[index].feedback}</p>
                              )}

                              {evaluationResults[index].explanation && (
                                <div className="evaluation-detail">
                                  <h5>Explanation</h5>
                                  <p>{evaluationResults[index].explanation}</p>
                                </div>
                              )}

                              {evaluationResults[index].hint && (
                                <div className="evaluation-detail">
                                  <h5>Hint</h5>
                                  <p>{evaluationResults[index].hint}</p>
                                </div>
                              )}

                              {evaluationResults[index].strengths?.length > 0 && (
                                <div className="evaluation-detail">
                                  <h5>What you did well</h5>
                                  <ul>
                                    {evaluationResults[index].strengths.map(
                                      (item, itemIndex) => (
                                        <li key={itemIndex}>{item}</li>
                                      )
                                    )}
                                  </ul>
                                </div>
                              )}

                              {evaluationResults[index].improvements?.length > 0 && (
                                <div className="evaluation-detail">
                                  <h5>Areas to improve</h5>
                                  <ul>
                                    {evaluationResults[index].improvements.map(
                                      (item, itemIndex) => (
                                        <li key={itemIndex}>{item}</li>
                                      )
                                    )}
                                  </ul>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </article>
                    ))}
                </div>
              )}

              {activeTab === "Progress" && (
                <div className="empty-state">
                  <div className="empty-icon">↗</div>
                  <h3>Your learning journey</h3>
                  <p>
                    {sessionId
                      ? "Your learning session is active. We'll connect the progress report next."
                      : "Create a learning session by analyzing code to begin tracking progress."}
                  </p>
                  <button
                    className="secondary-button"
                    onClick={() => setActiveTab("Analysis")}
                  >
                    Start learning →
                  </button>
                </div>
              )}
            </div>

            <div className="mentor-footer">
              <span className="footer-sparkle">✳</span>
              <span>Built to help you think like a programmer.</span>
            </div>
          </section>
        </section>

        <footer className="app-footer">
          <span>
            CODEMENTOR AI <span className="footer-separator">/</span>{" "}
            LEARNING BY UNDERSTANDING
          </span>
          <span>
            Made for curious minds <span className="footer-heart">♥</span>
          </span>
        </footer>
      </main>
    </div>
  );
}

export default App;
