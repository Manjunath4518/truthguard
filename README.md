# TruthGuard AI — working MVP

A small local document Q&A demo that shows hybrid retrieval, claim comparison, provenance checks, explicit supersession, scoped amendment handling, conflict resolution, a deterministic critic, citations, and abstention. The local rule-based mode works without API credentials; no LLM calls are made.

## Run on Windows

From this folder in PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

Open <http://127.0.0.1:8000>. The first launch creates `truthguard.db`. Uploaded text is stored in SQLite for this MVP.

## Public demo deployment (Render)

The repository includes `render.yaml` for a free Render web service. Push this project to a GitHub repository, then in Render choose **New → Blueprint**, connect that repository, and deploy the `truthguard-ai` service. After the deploy passes its health check, Render shows its public `onrender.com` URL. Click **Load HR demo corpus** after opening the URL.

The free service uses an ephemeral filesystem: uploaded documents and SQLite contents can disappear when the instance is replaced or restarted. The sample corpus can be reloaded from the dashboard. Use persistent storage and authentication before sharing sensitive files.

## Hackathon demo

1. Click **Load HR demo corpus**. These five clearly labeled documents are simulated sample content.
2. Ask “How many days can employees work remotely?” TruthGuard should cite approved Policy v2, identify older FAQ/v1 and draft v3 evidence, and return three days.
3. Ask “Can employees with less than 6 months of tenure work remotely?” The approved amendment scoped to v2 provides the eligibility rule.
4. Ask “Why is Policy v3 excluded?” It is marked Draft and cannot replace approved policy.
5. Expand **Compare with Normal RAG baseline** and **Show processing stages** to contrast retrieval alone with provenance verification.
6. Upload a TXT or text-based PDF and supply its version, type, effective date, status, supersession target, and amendment scope.

## Project structure

```text
backend/       FastAPI API and retrieval/verification modules
frontend/      Single-page HTML, CSS, and vanilla JavaScript
sample_documents/  Five simulated HR policy documents
requirements.txt
.env.example
```

## Current limitations

- Retrieval uses BM25-style lexical scoring plus a term-overlap similarity signal. It does not load a transformer embedding model or FAISS, keeping installation fast and offline-capable.
- Claim extraction is deterministic and strongest for numeric policy statements and common eligibility language. Complex paraphrases, tables, scans, and semantic contradictions need a real model/OCR pipeline.
- Supersession and amendment scope rely on metadata entered at upload; validate that metadata in a production system.
- Demo answer phrasing includes rule-based examples for the supplied HR corpus; arbitrary uploaded questions fall back to retrieved text or abstention.
- PDF extraction requires selectable text; scanned PDFs need OCR. The LLM API fields are placeholders for future integration.
- `truthguard.db` is local demo storage. Add authentication, access controls, retention policies, and audit protections before handling sensitive documents.
