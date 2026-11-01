from datetime import date

def verify(documents):
    today=date.today().isoformat()
    out=[]
    for d in documents:
        status=(d.get('approval_status') or '').lower()
        superseded_by=[x['name'] for x in documents if x.get('supersedes') and x['supersedes'].lower() in d['name'].lower()]
        effective=not d.get('effective_date') or d['effective_date']<=today
        reasons=[]
        if status=='draft': reasons.append('Draft; not approved for policy decisions.')
        if superseded_by: reasons.append('Explicitly superseded by '+', '.join(superseded_by)+'.')
        if not effective: reasons.append('Effective date is in the future.')
        if status=='approved' and effective and not superseded_by: reasons.append('Approved and effective; no explicit superseding document found.')
        out.append({'id':d['id'],'name':d['name'],'approved':status=='approved','draft':status=='draft','effective':effective,'superseded_by':superseded_by,'usable':status=='approved' and effective and not superseded_by,'reason':' '.join(reasons)})
    return out
