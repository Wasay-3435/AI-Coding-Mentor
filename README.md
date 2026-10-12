# AI Coding Mentor

An AI-powered programming assistant designed to help developers understand code, diagnose programming errors, improve code quality, and learn through guided explanations and practice.

## Overview

AI Coding Mentor aims to go beyond simply generating code or providing direct answers. It is designed to act as a programming mentor that helps users understand **why a problem occurs, how to approach solving it, and how to improve their programming skills**.

The application combines a web-based interface, a FastAPI backend, and LangChain-powered language-model workflows to deliver structured and educational programming assistance.

## Problem Statement

Programming learners frequently encounter errors that are difficult to understand or resolve independently. Traditional search-based solutions can provide fragmented explanations, while generic AI chat interfaces may produce inconsistent responses or solutions without sufficient educational context.

AI Coding Mentor aims to address these challenges through structured code analysis, understandable explanations, actionable suggestions, and interactive learning support.

## Key Features

### Implemented

- **Code analysis API:** Accepts source code and its programming language through a FastAPI endpoint.
- **AI-powered diagnosis:** Uses a LangChain pipeline and a Google Gemini model to analyze submitted code.
- **Structured AI responses:** Uses Pydantic models to organize summaries, detected issues, severity levels, explanations, and suggestions.
- **Prompt engineering:** Incorporates role-based instructions, zero-shot instructions, few-shot examples, and a structured diagnostic process.
- **Error handling:** Provides a controlled API response when the AI service is unavailable.
- **Automated evaluation:** Evaluates AI responses against predefined programming-error cases.
- **Unit testing:** Tests evaluation logic and JSON report generation using mocked responses.

### Planned

- Interactive web frontend and coding workspace.
- Improved code debugging and suggested fixes.
- Progressive hints that encourage independent problem-solving.
- AI-powered code review.
- Conversational AI mentor for follow-up questions.
- AI-generated programming exercises.
- More comprehensive evaluation datasets and historical reports.

Features marked as planned will be implemented and verified during development.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Backend framework | FastAPI |
| Request and response validation | Pydantic |
| LLM orchestration | LangChain |
| AI provider integration | Google Gemini via `langchain-google-genai` |
| Configuration and environment variables | `python-dotenv` |
| API documentation | FastAPI / OpenAPI / Swagger UI |
| Testing | Python `unittest` and `unittest.mock` |
| Evaluation reports | JSON |
| Version control | Git and GitHub |

## System Architecture

The planned application follows a modular architecture:

```text
User
  |
  v
Web Frontend
  |
  v
FastAPI Backend
  |
  v
API Route
  |
  v
Validation (Pydantic)
  |
  v
Application Service
  |
  v
LangChain Prompt and Model
  |
  v
Google Gemini
  |
  v
Structured Analysis Response
  |
  v
Frontend Results
```

The backend separates HTTP routing, application logic, prompt construction, AI integration, and data models to make the application easier to maintain, test, and extend.

## Current API

### Analyze Code

**Endpoint:** `POST /api/v1/analyze-code`

The endpoint accepts a programming language and source code, then returns a structured analysis.

Example request:

```json
{
  "language": "python",
  "code": "print(x)"
}
```

The structured response contains:

- `summary`: A concise description of the analysis.
- `issues`: Detected issues, including their type, severity, and explanation.
- `suggestions`: Recommended next steps or improvements.

The actual response depends on the submitted code and the model's analysis.

## Project Structure

```text
AI-Coding-Mentor/
├── backend/
│   └── app/
│       ├── api/
│       │   └── routes/
│       ├── chains/
│       ├── models/
│       ├── prompts/
│       ├── services/
│       ├── utils/
│       └── main.py
├── frontend/
├── tests/
│   └── evaluation/
│       ├── code_analysis_cases.py
│       ├── run_evaluation.py
│       ├── test_evaluator.py
│       ├── test_report.py
│       └── reports/
├── docs/
│   ├── design/
│   └── reports/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

Some directories and features are reserved for ongoing development.

## Getting Started

### 1. Prerequisites

- Python 3.11
- Git
- A Google Gemini API key with access to a supported model

### 2. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AI-Coding-Mentor
```

Replace the placeholder URL with the actual repository URL.

### 3. Create a virtual environment

**Windows PowerShell:**

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a local `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

Replace the placeholder with your own key. Never commit the `.env` file or expose API keys in source code, screenshots, or public repositories.

### 6. Start the backend

From the project root, run:

```bash
uvicorn backend.app.main:app --reload
```

The local API should be available at:

- API root: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 7. Run the unit tests

Run the evaluation and reporting tests without making live Gemini requests:

```bash
python -m unittest tests.evaluation.test_evaluator tests.evaluation.test_report -v
```

### 8. Run the live evaluation

When the Gemini API is available and quota permits:

```bash
python -m tests.evaluation.run_evaluation
```

The evaluation runner saves its latest JSON report under `tests/evaluation/reports/`.

## Evaluation Methodology

The evaluation suite currently includes examples covering:

1. Undefined variables.
2. List index errors.
3. Division by zero.
4. Syntax errors.
5. Potential logical errors.

The evaluator checks issue classification, expected keywords, explanations, and suggestions. Unit tests use mock responses to verify the evaluation logic independently of the AI provider.

The current dataset is small, and keyword matching is a heuristic rather than proof of semantic correctness. Live evaluation results must distinguish completed cases from skipped cases caused by API quota or availability errors.

## Documentation

- `docs/design/`: UI/UX designs, wireframes, prototypes, and interface decisions.
- `docs/reports/`: Project report, architecture documentation, methodology, testing, and discussion of results.
- `tests/evaluation/reports/`: Machine-generated JSON evaluation results.

## Development Status

The project is under active development. The backend code-analysis pipeline, structured response models, error handling, evaluation runner, and initial automated tests have been implemented. The frontend and additional mentoring features remain part of the development roadmap.

## Security

- Keep API credentials in local environment variables.
- Do not commit `.env` or other files containing secrets.
- Use `.env.example` only for placeholder configuration.
- Review generated AI suggestions before applying them to important code.

## Team

Developed as a university group project exploring generative AI, prompt engineering, backend development, and AI-assisted programming education.

## License

A license has not yet been selected. Until one is added, do not assume that the repository grants permission to redistribute or reuse its contents.
