import re

def audit(answer, evidence):
    citations=[]
    for p in evidence:
        citations.append({'document':p['name'],'version':p['version'],'page':p.get('page'),'quote':' '.join(p['text'].split())})
    cited=' '.join(c['quote'].lower() for c in citations)
    claims=[(n,(u or '').lower().rstrip('s')) for n,u in re.findall(r"\b(\d+(?:\.\d+)?)\s*(days?|months?|weeks?|hours?|%)\b",answer,re.I)]
    unsupported=[f'{n} {u}' for n,u in claims if not re.search(rf"\b{re.escape(n)}\s*{re.escape(u)}s?\b",cited)]
    return {'citation_count':len(citations),'citations':citations,'unsupported_numeric_claims':unsupported,'passed':bool(citations) and not unsupported}
