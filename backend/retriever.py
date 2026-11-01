import re, math
from collections import Counter
from .document_processor import chunks

def terms(s): return re.findall(r"[a-z0-9]+", s.lower())

def retrieve(question, documents, limit=10):
    q=terms(question)
    if not q: return []
    passages=[]
    for d in documents:
        for part in chunks(d['content']):
            passages.append({**part, 'document_id':d['id'],'name':d['name'],'version':d['version'],'doc_type':d['doc_type'], 'effective_date':d['effective_date'],'approval_status':d['approval_status'],'supersedes':d['supersedes'],'applies_to':d.get('applies_to','')})
    if not passages: return []
    # BM25-style lexical score and lightweight normalized term-overlap vector proxy.
    dfs=Counter(t for p in passages for t in set(terms(p['text'])))
    scored=[]
    for p in passages:
        toks=terms(p['text']); counts=Counter(toks); score=0.0
        for t in set(q):
            if t not in counts: continue
            idf=math.log(1+(len(passages)-dfs[t]+0.5)/(dfs[t]+0.5))
            score += idf * counts[t]*2.2/(counts[t]+1.2*(0.25+0.75*len(toks)/180))
        # Add overlap cosine-like signal to make hybrid behavior explicit.
        overlap=len(set(q)&set(toks))/max(1, math.sqrt(len(set(q))*len(set(toks))))
        score += overlap*2.0
        p['score']=round(score,3)
        if score>0: scored.append(p)
    return sorted(scored,key=lambda p:p['score'],reverse=True)[:limit]
