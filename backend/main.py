from pathlib import Path
from datetime import date
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid
from .database import list_documents, get_documents, add_document, delete_document
from .document_processor import extract_text
from .retriever import retrieve
from .claim_analyzer import analyze
from .provenance_verifier import verify
from .conflict_resolver import resolve
from .critic import critique
from .answer_auditor import audit

ROOT=Path(__file__).resolve().parent.parent
app=FastAPI(title='TruthGuard AI',description='Adversarial verification for document Q&A')
app.mount('/static',StaticFiles(directory=ROOT/'frontend'),name='static')

class Ask(BaseModel): question:str

@app.get('/')
def home(): return FileResponse(ROOT/'frontend'/'index.html')

@app.get('/api/documents')
def documents(): return list_documents()

@app.post('/api/upload')
async def upload(file:UploadFile=File(...), version:str=Form('1'), doc_type:str=Form('Policy'), effective_date:str=Form(''), approval_status:str=Form('Approved'), supersedes:str=Form(''), applies_to:str=Form('')):
    data=await file.read()
    try: content,_=extract_text(file.filename or 'document.txt',data)
    except ValueError as e: raise HTTPException(400,str(e))
    if not content.strip(): raise HTTPException(400,'No extractable text found in this document.')
    try: date.fromisoformat(effective_date) if effective_date else None
    except ValueError: raise HTTPException(400,'Effective date must use YYYY-MM-DD format.')
    doc={'name':Path(file.filename or 'document.txt').name,'version':version,'doc_type':doc_type,'effective_date':effective_date,'approval_status':approval_status,'supersedes':supersedes,'applies_to':applies_to,'content':content}
    upload_dir=ROOT/'uploads'; upload_dir.mkdir(exist_ok=True)
    stored=upload_dir/(uuid.uuid4().hex+Path(doc['name']).suffix.lower())
    stored.write_bytes(data); doc['stored_path']=str(stored)
    add_document(doc)
    return {'ok':True,'document':doc['name'],'characters':len(content)}

@app.delete('/api/documents/{doc_id}')
def remove(doc_id:int): delete_document(doc_id); return {'ok':True}

@app.post('/api/samples')
def samples():
    sample_dir=ROOT/'sample_documents'; sample_dir.mkdir(exist_ok=True)
    existing={d['name'] for d in get_documents()}
    sample_meta=[('WFH_Policy_v1.txt','1','Policy','2024-01-01','Approved','',''),('WFH_Policy_v2.txt','2','Policy','2025-01-01','Approved','WFH_Policy_v1.txt',''),('HR_FAQ.txt','1','FAQ','2023-05-01','Approved','',''),('Amendment_2025.txt','A1','Amendment','2025-02-01','Approved','','WFH_Policy_v2.txt'),('WFH_Policy_v3_Draft.txt','3','Policy','2026-01-01','Draft','','')]
    added=[]
    for name,version,kind,effective,status,sup,applies in sample_meta:
        path=sample_dir/name
        if name in existing: continue
        if not path.exists(): raise HTTPException(500,f'Missing sample data file: {name}')
        add_document({'name':name,'version':version,'doc_type':kind,'effective_date':effective,'approval_status':status,'supersedes':sup,'applies_to':applies,'content':path.read_text(encoding='utf8')})
        added.append(name)
    return {'ok':True,'added':added,'documents':list_documents()}

@app.post('/api/ask')
def ask(body:Ask):
    docs=get_documents(); question=body.question.strip()
    if not question: raise HTTPException(400,'Enter a question.')
    # Real stages; retrieval pass two expands coverage when conflicts or a narrow amendment need checking.
    p1=retrieve(question,docs,8)
    stage=[{'name':'Retriever Agent','detail':f'Found {len(p1)} relevant passage(s).','done':True}]
    p2=retrieve(question+' policy amendment supersedes approved draft FAQ version',docs,14) if p1 else []
    passages=[]; seen=set()
    for p in p1+p2:
        key=(p['document_id'],p['text'])
        if key not in seen: seen.add(key); passages.append(p)
    claims=analyze(passages,question); stage.append({'name':'Claim Analyst','detail':f"Compared {len(claims['claims'])} policy claim(s); {len(claims['conflicts'])} disagreement(s) detected.",'done':True})
    provenance=verify(docs); stage.append({'name':'Provenance Verifier','detail':f'Checked approval, effective dates, and explicit supersession across {len(docs)} document(s).','done':True})
    decision=resolve(question,docs,passages,claims,provenance); stage.append({'name':'Resolution Engine','detail':decision['reason'],'done':True})
    critic=critique(decision['answer'],decision['selected'],decision['rejected'],decision['unresolved']); stage.append({'name':'Adversarial Critic','detail':'; '.join(critic['findings']),'done':True})
    audited=audit(decision['answer'],decision['selected']); stage.append({'name':'Answer Auditor','detail':f"Checked {audited['citation_count']} evidence citation(s).",'done':audited['passed']})
    stage.append({'name':'Final Decision','detail':decision['status'],'done':True})
    baseline=' '.join(' '.join(p['text'].split()) for p in p1[:2])[:650] or 'No relevant passage was found.'
    return {'question':question,**decision,'evidence':audited['citations'],'conflicts':claims['conflicts'],'claims':claims['claims'],'provenance':provenance,'critic':critic,'stages':stage,'normal_rag':{'answer':baseline,'evidence':[{'document':p['name'],'version':p['version'],'page':p.get('page'),'quote':' '.join(p['text'].split())} for p in p1[:2]]}}
