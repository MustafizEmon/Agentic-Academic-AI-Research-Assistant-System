***Agentic Academic AI Research Assistant System***
A multi-agent AI research workspace that transforms natural language objectives into structured analytical literature matrices table and manuscript-ready literature review text. Utilizing LLM execution and public scientific indexes, it implements and deploys an interactive context-aware RAG copilot chat widget for the researchers.

# Overview

The Agentic Academic AI Research Assistant System is the concept of helps researchers instead of manually searching for research papers, comparing studies, extracting important information, and writing reviews, the system does these tasks automatically.

Users only need to enter a research topic. The platform then uses multiple AI agents to search academic databases, collect and validate research papers, organize findings into easy-to-read comparison tables, and generate literature reviews texts.

# Features

***Research Discovery & Management***

* Converts simple research topics into effective search keywords and phrases automatically.
* Searches multiple academic databases at the same time, including arXiv, Semantic Scholar, and OpenAlex.
* Collects research papers, tracks publication information, and downloads PDF files.
* Lets users set a maximum number of papers to process and prioritizes locally uploaded papers before downloading additional papers online.

***Advanced Analysis***

* Automatically checks downloaded files to ensure they contain useful research content. At the start, the user also has the option to upload papers from local storage.
* Removes scanned PDFs, empty files, lecture notes, and other low-quality documents.
* Generates two types of literature reviews:
  * A detailed thematic review explaining major contents and findings.
  * A concise "Related Work" section ready to be inserted into academic manuscripts.
* Creates an interactive comparison table showing key information such as research problems, methods, findings, limitations, and publication venues and links.

***Productivity & System Features***

* Includes a built-in AI chat assistant that can answer questions based on the collected research papers.
* Uses a lightweight Python-based retrieval system instead of complex vector databases, making installation simpler and more reliable.
* Provides a one-click reset option to clear all stored papers and start a new research project.
* Supports exporting literature reviews as text files and comparison tables in spreadsheet-compatible formats for further analysis.

# System Architecture

The application architecture is designed around a Linear Directed Pipeline with an Intercepting Loop Feedback Philosophy. Components are isolated into highly specialized structural wrappers to ensure computational encapsulation and fault containment.

<div align="center"> <img src="backend\Resources\system.svg" alt="Interface" width="800"> </div>

### The AI Agents

***QueryAgent (The Interpreter & Planner):*** What it does: Takes your unrefined, natural language research topic and translates it into an optimized search strategy.

Role: It breaks down the main prompt into distinct technical sub-domains, extracts core keyword profiles, and generates an array of flat, plain-text search phrases specifically formatted to get the highest hit rates from public academic APIs.

***StructuringAgent (The Data Extractor):*** What it does: Acts as an ultra-precise technical data miner that reads through the raw text of the verified research papers.

Role: It extracts exact, factual details from the text to populate the comparative matrix—isolating the specific Problem Statement, Methodology Framework, Key Findings, Limitations, and the true Publication Venue for each document without hallucinating outside facts.

***EvaluationAgent (The Quality Auditor):*** What it does: Serves as an internal peer reviewer that acts as a quality assurance check on the pipeline's final output.

Role: It cross-examines the generated literature reviews against the source data matrix, calculates a completeness quality score out of 10, and appends a warning list if any technical claims feel thin or unsupported.

****Agent Workflow Summary****

The system follows a step-by-step pipeline managed through a shared state object. First, the Query Agent expands the research topic and retrieves relevant papers. A validation stage then checks each paper and removes unreadable or low-quality files before replacing them with better candidates. Next, the Structuring Agent extracts key information and builds a comparison table. The Synthesis Engine uses this data to generate literature reviews, and finally, the Evaluation Agent reviews and scores the output before the results are presented to the user.

### Rationale Behind Architectural Design Decisions

* The system stores and tracks all active processing information in memory while it is running. The user interface automatically checks for updates every 2.5 seconds, allowing progress bars, statistics, and analysis results to appear in real time.

* To improve performance and stay within AI processing limits, text inputs are restricted to a maximum of 12,000 characters. For question-answering and retrieval tasks, the system only selects the two most relevant text sections, helping maintain speed while keeping important information from research papers available.

* Security is enhanced by restricting the server to run only on the local machine (127.0.0.1), preventing access from external networks. Uploaded filenames are automatically cleaned and shortened to remove special characters and reduce the risk of file path and directory traversal attacks.

***Error Handling***

* API failures are isolated so one failed source does not stop the system.
* Corrupted or invalid PDFs are automatically detected, removed, and replaced.
* LLM output errors are cleaned and repaired using fallback parsing methods.
* Large requests are truncated to avoid API token limit errors.
* Missing folders and file access issues are automatically handled.

***Performance Optimization***

* Parallel searches speed up paper discovery.
* Chunk-based file uploads reduce memory usage.
* Text truncation lowers processing costs and improves stability.
* Lightweight Python-based retrieval enables fast searches without external databases or GPUs.

***Challenges & Solutions***

* Fixed API search failures by converting complex Boolean queries into simple keywords.
* Solved token limit issues by reducing context size and optimizing retrieval.
* Eliminated extraction failures by filtering out scanned, image-only, and non-research PDFs automatically.

# Project Architecture

```text
academic_research_assistant/         # Unified Structural Workspace Root
├── backend/                         # Core Python Analytical Engine Workspace
│   ├── main.py                      # REST Endpoint Router & Orchestration Pipeline Controller
│   ├── config.py                    # Global Path Resolution & Environment Parameter Definitions
│   ├── requirements.txt             # Asynchronous Package Dependency Resolution Blueprint
│   ├── .env                         # Critical Protected System Authorization Credentials
│   │
│   ├── agents/                      # Cognitive Agent LLM Processing Matrix Group
│   │   ├── __init__.py              # Python Packaging Namespace Anchor
│   │   ├── query_agent.py           # Objective Interpreter & Flat-Phrase Search Query Builder
│   │   ├── structuring_agent.py     # Document Analytical Text Parser & JSON Entity Extractor
│   │   └── evaluation_agent.py      # Quality Auditor & Completeness Score Review System
│   │
│   ├── services/                    # Infrastructure & Data Manipulation Core Services
│   │   ├── __init__.py              # Python Packaging Namespace Anchor
│   │   ├── retrieval_service.py     # Concurrent API Consumer for arXiv, SemScholar, OpenAlex
│   │   ├── pdf_service.py           # Document Ingestion Manager, Text Extractor & Word Chunker
│   │   ├── synthesis_service.py     # Text Synthesizer for Thematic & Camera-Ready Reviews
│   │   └── rag_service.py           # Pure-Python Keyword Density Matrix & Context Chat Copilot
│   │
│   └── data/                        # Local Storage Persistence Cache Area
│       ├── papers/                  # Local folder for downloaded and bulk-uploaded PDFs
│       ├── metadata.json            # Unified JSON registry tracking active document records
│       └── vectorstore/             # Local text index store for the RAG chat component
│
└── frontend/                        # Web Interface Layer UI Workspace
    ├── package.json                 # Node Package Ecosystem Control Manifest
    ├── public/                      # Static Document Ingestion Layout Assets
    └── src/                         # React Operational Codebase Component Group
        ├── App.js                   # Unified Single Page Application UI & Workspace Stylesheet
        └── index.js                 # Virtual DOM Web Interface Root Bootstrapper
```

# Tech Stack

### Frontend Core

* React
* Inline Fluid CSS Grid

### Backend Core

* FastAPI Framework
* Uvicorn WSGI Web Server

***Third-Party APIs, Toolkits, & Libraries***

* Groq Cloud Infrastructure Layer: Provides ultra-fast LLM inference capabilities using specialized hardware arrays, executing 70B parameter models (LLaMA 3) completely on a free tier.

* LangChain Integration Core Utilities: Simplifies communication with LLM endpoints, prompt mapping, structural schema definitions, and context injection rules.

* PyMuPDF Extraction Library (fitz): A fast, C-backed text extraction library that parses raw text out of complex document styles, tracking multi-page files for layout compilation tasks.

# How to Setup & Run

### Prerequisites

* Python 3.10 or higher installed on your system.
* Node.js (v18 or higher) & npm installed.
* A free Groq API Key (obtainable from the Groq Console).

### 1. Configure the Backend

Navigate to the backend directory, construct a virtual environment, activate it, and install all dependencies:

```bash
cd backend
python -m venv venv

# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Construct an environment file named .env in your backend/ root directory and add your access key:

```bash
GROQ_API_KEY=gsk_your_actual_free_groq_api_key_goes_here
```

Start the local backend API server:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Configure the Frontend

Open a new terminal screen, navigate to the frontend folder, install the required node packages, and run the interface application:

```bash
cd frontend
npm install
npm start
```

The browser will automatically launch the workspace workspace layout at <http://localhost:3000>

# Usage Instructions

***Configure Parameters:*** Paste your core target objective into the Research Topic text input field. Adjust the Paper Limit Ceiling parameter to state your exact targeted reference allocation (e.g., 3).

***Upload Local Files (Optional):*** Click and upload stored papers from your local. The pipeline prioritizes processing these local documents first.

***Execute Pipeline Processing:*** Click the Launch Operations button. The dashboard input parameters will lock, and progress badges will light up sequentially as tasks complete.

***Explore the Workspace Matrix:*** Once processing wraps up, explore the comparative matrix grid. If a paper passed structural text validation, its fields will exhibit real-world technical findings paired with its verified publication venue.

***Review and Export Material:*** Toggle between the narrative Thematic Review tab and the continuous Direct Camera-Ready Text tab. Click Download Plain (.txt), Download Camera-Ready (.txt), or Export Spreadsheet (.xls) to save your results.

***Query the Local RAG Copilot:*** Click the floating conversation action button (💬) pinned in the bottom right corner. Enter highly specific domain questions to chat with your document library using clear source references.

***Reset Infrastructure Environment:*** Click Purge Environment at the top right to erase cached text files, clean system indices, and prepare the workspace for a brand new research task.

<div align="center"> <img src="backend\Resources\screen3.png" alt="Interface" width="800"> </div>

### Limitations & Future Enhancements

* **Free-Tier & Context Caps:** Free cloud API rate limits restrict processing to ~20 papers per run. Text context is truncated at 12,000 characters per document, which can clip deep appendices.
* **Non-OCR PDF Rejection:** Scanned or image-only PDFs are automatically rejected by the look-ahead structural filter because local OCR functionality is not currently available.
* **Volatile Session States:** Pipeline progress and active states are stored in temporary runtime memory, meaning all active workflows are cleared if the backend server restarts.
* **Keyword-Only RAG Retrieval:** The system relies on a pure-Python keyword-density engine. It does not generate query or document embedding vectors, meaning it lacks semantic, meaning-based similarity search.
* **Infrastructure Core Upgrades (Roadmap):** Implementing an embedded SQLite layer will retain project history across sessions, while localized OCR will enable text extraction from scanned PDFs.
* **Advanced Visuals & Semantic RAG (Roadmap):** Upgrades include adding an interactive citation network graph to visualize relationships between papers and transitioning the chat copilot to dense vector embeddings for deep semantic retrieval.

## 💬 Contact

<p align="center">
  <a href="https://github.com/MustafizEmon">
    <img src="https://avatars.githubusercontent.com/u/188073067?v=4" width="120px" style="border-radius: 10%;" alt="Md Mostafizur Rahman"/>
  </a>
  <br />
  <a href="https://www.linkedin.com/in/mdmostafizurrahmanemon" style="text-decoration: none;">
    <strong>👤 Md Mostafizur Rahman</strong>
  </a>
  <br />
  <a href="mailto:mostafizur221cs@gmail.com">📧 mostafizur221cs@gmail.com</a>
</p>

##

<p align="center">
  <sub>⭐️Arigatou Gozaimas!</sub>
</p>