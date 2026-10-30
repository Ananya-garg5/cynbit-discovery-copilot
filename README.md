# Cynbit Discovery Copilot

An AI-assisted proof of concept for analyzing incoming enquiries and supporting Cynbit's discovery process.

## What it does

The system takes a user enquiry and:

1. Classifies it as:
   - Business Sales Lead
   - Non-Sales Enquiry
   - Not Applicable
2. Retrieves relevant Cynbit services, products, and published case studies.
3. Generates a short discovery brief.
4. Suggests follow-up questions.
5. Assigns an AI-assisted lead priority.
6. Drafts a response for human review.

The system uses Cynbit's publicly available website information as its knowledge base.

## Architecture

```text
User Enquiry
     ↓
Enquiry Classifier
     ↓
Business / Non-Sales / Not Applicable
     ↓
Knowledge Retrieval
     ↓
Relevant Services / Products / Case Studies
     ↓
Gemini LLM
     ↓
Structured Discovery Analysis
     ↓
Grounding & Validation
     ↓
Human Review
```

## Tech Stack

- Python 3.11
- Streamlit
- Google Gemini API
- Pydantic
- scikit-learn
- TF-IDF + cosine similarity

## Project Structure

```text
cynbit-discovery-copilot/
│
├── app/
│   └── streamlit_app.py
│
├── src/
│   ├── analyzer.py
│   ├── classifier.py
│   ├── grounding.py
│   ├── prompts.py
│   ├── retriever.py
│   └── schemas.py
│
├── data/
│   └── cynbit_knowledge.json
│
├── evaluation/
│   ├── evaluation_cases.json
│   └── sample_outputs.json
│
├── tests/
│   ├── test_analyzer.py
│   ├── test_evaluation.py
│   ├── test_fresh.py
│   ├── test_grounding.py
│   └── test_retriever.py
│
├── docs/
│   ├── AI_Opportunity_Report_Cynbit.pdf
│   └── Technical_Approach_Cynbit_Discovery_Copilot.pdf
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

Clone the repository and open the project folder:

```bash
git clone https://github.com/Ananya-garg5/cynbit-discovery-copilot.git
cd cynbit-discovery-copilot
```

Create and activate a virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file from `.env.example`:

```text
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3-flash-preview
```

The API key should be kept local and must not be committed to GitHub.

## Run the Application

```powershell
streamlit run app/streamlit_app.py
```

The Streamlit interface can then be opened in the browser.

## Evaluation

The repository contains manually created evaluation cases covering:

- Business sales enquiries
- Non-sales enquiries
- Not-applicable enquiries
- Service retrieval
- Product retrieval
- Case-study retrieval
- Grounding and unsupported-claim checks

The current deterministic evaluation set achieved:

- Classification: 10/10
- Service retrieval: 10/10
- Product retrieval: 10/10
- Case-study retrieval: 10/10

These are development evaluation results on a manually created test set, not an independent benchmark.

## Knowledge Base

The knowledge base was created from Cynbit's publicly available website content and contains information about:

- Services
- Products
- Published case studies
- Other relevant public information

The current implementation uses TF-IDF retrieval because the knowledge base is small. A vector/embedding-based retrieval system could be considered if the knowledge base grows.

## Limitations

- The prototype uses a small manually prepared knowledge base.
- It has not been connected to Cynbit's internal CRM or historical enquiry data.
- Lead priority is an AI-assisted heuristic and is not an official Cynbit scoring system.
- Generated responses require human review before being sent.
- The evaluation cases were created for development and are not representative of all possible real-world enquiries.

## Reports

The `docs/` folder contains:

- **AI Opportunity Report** — analysis of possible AI/ML opportunities for Cynbit.
- **Technical Approach Report** — architecture, model choices, data pipeline, prompt engineering, validation, evaluation, and execution plan.

## Note

This project is a proof of concept developed for the Cynbit AI/ML Engineer Intern assessment. It is based on publicly available information and does not represent Cynbit's internal systems or processes.