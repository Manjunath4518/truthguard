import re

NUM_RE = re.compile(r"\b(\d+(?:\.\d+)?)\s*(days?|months?|weeks?|hours?|%)?\b", re.I)

def analyze(passages, question=''):
    claims=[]
    for p in passages:
        text=' '.join(p['text'].split())
        if NUM_RE.search(text) or any(k in text.lower() for k in ('must','cannot','eligible','qualify','allowed','requires','proposes')):
            claims.append({'source':p['name'],'text':text,'approval_status':p['approval_status'],'doc_type':p['doc_type'],'version':p['version']})
    values={}
    for c in claims:
        for m in NUM_RE.finditer(c['text']):
            unit=(m.group(2) or '').lower().rstrip('s')
            if not unit:
                continue
            key=unit
            values.setdefault(key,[]).append((m.group(1),c))
    conflicts=[]
    for unit, entries in values.items():
        distinct={v for v,_ in entries}
        if len(distinct)>1:
            conflicts.append({'topic':unit,'claims':[{'value':v,'source':c['source'],'text':c['text'],'approval_status':c['approval_status'],'doc_type':c['doc_type']} for v,c in entries]})
    return {'claims':claims,'conflicts':conflicts}
