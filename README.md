# ProposalCraft: Autonomous Business RFP & Document Generator

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Document_Agent-orange.svg)](https://github.com/langchain-ai/langgraph)
[![ReportLab](https://img.shields.io/badge/ReportLab-PDF_Generation-red.svg)](https://www.reportlab.com/)
[![python-docx](https://img.shields.io/badge/python--docx-DOCX_Export-blue.svg)](https://python-docx.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ProposalCraft** is an autonomous generative AI pipeline built with **FastAPI**, **LangGraph**, and **ReportLab**. It transforms complex enterprise RFPs, client scope documents, and unstructured conversational notes into structured, executive-ready commercial proposals. Featuring multi-agent planning, technical architecture drafting, pricing estimation, and automated styling, it compiles and exports production-grade **PDF**, **PPTX**, and **DOCX** packages in seconds.

---

## Architecture Overview

```mermaid
flowchart TD
    ClientDoc[RFP Document: PDF / DOCX / Text] --> Parser[Document Extraction Node]
    Parser --> Spec[Structured RFP Specification]
    
    subgraph Agentic Document Synthesis [LangGraph Graph Engine]
        Spec --> Extractor[Requirements Extractor Agent]
        Extractor --> Planner[Section Architect Agent]
        
        Planner -->|Parallel Sub-Agents| ScopeAgent[Scope & Deliverables Agent]
        Planner -->|Parallel Sub-Agents| ArchAgent[Technical Architecture Agent]
        Planner -->|Parallel Sub-Agents| PricingAgent[Cost & Milestone Estimator Agent]
        
        ScopeAgent --> Reviewer[Executive Reviewer & Compliance Agent]
        ArchAgent --> Reviewer
        PricingAgent --> Reviewer
        
        Reviewer -->|Approved| LayoutEngine[Layout & Multi-Format Compiler]
    end

    LayoutEngine --> PDF[ReportLab Styled PDF]
    LayoutEngine --> DOCX[python-docx Document]
    LayoutEngine --> PPTX[python-pptx Presentation]
```

---

## Key Features

- **Autonomous RFP Decomposition**: Ingests vendor questionnaires and tender documents; maps out explicit requirements, implicit risks, and compliance milestones.
- **Coordinated Multi-Agent Synthesis**: Deploys specialized sub-agents for each proposal section (Executive Summary, Proposed Technical Architecture, Deliverables, Security Compliance, and Commercials) using **LangGraph**.
- **Dynamic Multi-Format Compiler**: Compiles the unified proposal data model into three enterprise formats:
  - **PDF**: Pixel-perfect layout with cover pages, tables, callout blocks, and footers using **ReportLab**.
  - **DOCX**: Native editable Microsoft Word document using **python-docx**.
  - **PPTX**: Multi-slide pitch presentation using **python-pptx**.
- **Commercial & Milestone Estimation**: Calculates resource allocations, timelines, and payment milestone tables based on scope complexity.
- **RESTful FastAPI Service**: Asynchronous endpoints for generation, draft editing, and instant downloading.

---

## Tech Stack

| Component | Technologies |
| :--- | :--- |
| **API & Server** | Python 3.11, FastAPI, Uvicorn, AsyncIO, Pydantic v2 |
| **Agent Orchestration** | LangGraph, LangChain Core |
| **Document Generation** | ReportLab (PDF), python-docx (DOCX), python-pptx (PPTX) |
| **LLM Inference** | Groq (Llama 3.3 70B Versatile), OpenAI GPT-4o |
| **Parsing & Storage** | PyMuPDF, python-docx, PostgreSQL (Templates & Archives) |
| **DevOps** | Docker, Docker Compose, Pytest |

---

## Project Structure

```text
proposalcraft-agent/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── proposals.py         # Generate, inspect, and update
│   │   │   ├── export.py            # Download PDF, PPTX, DOCX
│   │   │   └── templates.py         # Company brand themes & styling
│   │   └── router.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── agents/
│   │   ├── state.py                 # ProposalGraphState schema
│   │   ├── extractor.py             # RFP requirement parser
│   │   ├── section_planner.py       # Table of contents & outline builder
│   │   ├── writers.py               # Technical & commercial section writers
│   │   ├── reviewer.py              # Tone & compliance checker
│   │   └── graph.py                 # Compiled LangGraph pipeline
│   ├── renderers/
│   │   ├── pdf_renderer.py          # ReportLab flowables & styling
│   │   ├── docx_renderer.py         # python-docx formatting
│   │   └── pptx_renderer.py         # Slide deck generator
│   └── main.py
├── templates/                       # Default styling & company logos
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Quickstart

### 1. Installation

```bash
git clone https://github.com/Deeps72-ux/proposalcraft-agent.git
cd proposalcraft-agent

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Configuration

```env
GROQ_API_KEY=gsk_your_groq_key
OPENAI_API_KEY=sk_your_openai_key
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/proposalcraft
COMPANY_NAME="Your Company or Studio"
DEFAULT_CURRENCY=USD
```

### 3. Run FastAPI Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## API Endpoints

- `POST /api/v1/proposals/generate`: Ingest RFP text/document and generate structured proposal.
- `GET /api/v1/proposals/{id}/export/{format}`: Export proposal as `pdf`, `docx`, or `pptx`.
- `PUT /api/v1/proposals/{id}/section`: Edit specific sections before final document build.

---

## License

MIT License.
