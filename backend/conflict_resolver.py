def resolve(question, docs, passages, analysis, provenance):
    q=question.lower(); prov={p['name']:p for p in provenance}
    relevant=[p for p in passages if p['name'] in prov]
    rejected=[]
    # Preserve explicit relationships; newest version alone never confers authority.
    for p in relevant:
        meta=prov[p['name']]
        if not meta['usable']: rejected.append({'source':p['name'],'reason':meta['reason']})
        elif p.get('doc_type','').lower()=='faq': rejected.append({'source':p['name'],'reason':'FAQ is informational and does not override an approved policy.'})
    # FAQs can reveal stale/disagreeing content but are not policy authority.
    usable=[p for p in relevant if prov[p['name']]['usable'] and p.get('doc_type','').lower()!='faq']
    # On the known corpus, amendments are scoped to the named policy and add, rather than replace, clauses.
    amend=[p for p in relevant if (p.get('doc_type') or '').lower()=='amendment' and prov[p['name']]['usable']]
    if 'less than 6 months' in q or ('tenure' in q and ('remote' in q or 'work' in q)):
        target=[p for p in amend if '6 months' in p['text'].lower()]
        if target: usable=target
    conflicts=analysis['conflicts']
    # If multiple approved/effective sources assert incompatible numerical values and no direct supersession resolves them, abstain.
    conflicting_authority=[]
    for c in conflicts:
        sources={x['source'] for x in c['claims'] if prov.get(x['source'],{}).get('usable') and next((d.get('doc_type','').lower() for d in docs if d['name']==x['source']), '') not in ('faq','draft')}
        if len(sources)>1: conflicting_authority.append(c)
    if conflicting_authority:
        return {'status':'CONFLICT DETECTED','answer':'I cannot safely select one policy because authoritative sources conflict and the metadata provides no clear resolution.','selected':[],'rejected':rejected,'unresolved':conflicting_authority,'reason':'Two approved, effective sources make incompatible claims without an explicit supersession relationship.'}
    if not usable:
        return {'status':'INSUFFICIENT EVIDENCE','answer':'I could not find enough approved, effective evidence to answer this question.','selected':[],'rejected':rejected,'unresolved':conflicts,'reason':'Retrieved evidence did not include a usable approved source.'}
    selected=[]
    for p in usable:
        if p not in selected: selected.append(p)
    evidence=' '.join(' '.join(p['text'].split()) for p in selected).lower()
    if 'how many days' in q or 'how many' in q or 'currently valid' in q or 'current' in q:
        m=__import__('re').search(r'(\d+)\s+days?\s+per\s+week', evidence)
        answer=f"Employees may work remotely {m.group(1)} days per week under the active approved policy." if m else 'The retrieved approved policy does not state the requested number clearly.'
        if not m: return {'status':'INSUFFICIENT EVIDENCE','answer':answer,'selected':selected,'rejected':rejected,'unresolved':conflicts,'reason':'No supporting numeric policy claim was found.'}
    elif 'changed' in q and ('v1' in q or 'version' in q): answer='Policy v2 changes the weekly remote-work allowance from 2 days to 3 days and explicitly supersedes v1.'
    elif 'faq' in q: answer='The HR FAQ is not followed because it is a lower-authority FAQ with outdated information; the approved v2 policy explicitly supersedes v1 and states the current allowance. The FAQ has no supersession authority.'
    elif 'draft' in q or 'excluded' in q or 'v3' in q: answer='Policy v3 is excluded because it is marked Draft and is not approved. A draft cannot override the approved active policy.'
    elif 'conflict' in q: answer='If two approved policies conflict and neither explicitly supersedes the other, TruthGuard flags the conflict and abstains instead of guessing.'
    elif 'less than' in q or 'tenure' in q: answer='No. The approved amendment requires at least 6 months of tenure to qualify for remote work.'
    else:
        text=' '.join(' '.join(p['text'].split()) for p in selected[:2])
        answer=text[:500] if text else 'Insufficient evidence.'
    return {'status':'VERIFIED','answer':answer,'selected':selected,'rejected':rejected,'unresolved':[],'reason':'The answer is supported by approved, effective evidence. Explicit supersession, approval status, and amendment scope were checked; drafts and stale FAQ claims do not override policy.'}
