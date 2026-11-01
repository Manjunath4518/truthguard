from pathlib import Path

def extract_text(filename: str, data: bytes) -> tuple[str, list[str]]:
    if filename.lower().endswith('.txt'):
        return data.decode('utf-8', errors='replace'), []
    if filename.lower().endswith('.pdf'):
        try:
            import fitz
        except ImportError as e:
            raise ValueError('PDF extraction requires PyMuPDF. Install requirements.txt.') from e
        pdf = fitz.open(stream=data, filetype='pdf')
        pages = [p.get_text() for p in pdf]
        return '\n'.join(pages), pages
    raise ValueError('Only PDF and TXT files are supported.')

def chunks(text, pages=None, size=850):
    # Keep passages reasonably small and retain PDF page attribution where possible.
    result=[]
    if pages:
        for n, page in enumerate(pages, 1):
            for start in range(0, len(page), size):
                part=page[start:start+size].strip()
                if part: result.append({'text':part,'page':n})
    else:
        for start in range(0, len(text), size):
            part=text[start:start+size].strip()
            if part: result.append({'text':part,'page':None})
    return result
