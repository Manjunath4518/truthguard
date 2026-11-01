from .answer_auditor import audit

def critique(answer, selected, rejected, unresolved):
    findings=[]
    if not selected: findings.append('No approved supporting citation selected.')
    if rejected: findings.append(f"Excluded {len(rejected)} draft, superseded, or otherwise unusable source(s).")
    if unresolved: findings.append(f"Reviewed {len(unresolved)} detected numerical disagreement(s).")
    citation_check=audit(answer,selected)
    if citation_check['unsupported_numeric_claims']:
        findings.append('Unsupported numeric claim(s): '+', '.join(citation_check['unsupported_numeric_claims'])+'.')
    elif selected and not any(' '.join(p['text'].split()).lower() in answer.lower() for p in selected) and len(answer.split())>10:
        findings.append('Answer is a rule-based synthesis; numeric claims were checked against citations.')
    if not findings: findings.append('No unsupported source override found in the selected evidence.')
    return {'rounds':2,'findings':findings,'passed':bool(selected) and not unresolved and citation_check['passed']}
