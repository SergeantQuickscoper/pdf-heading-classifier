import fitz  # PyMuPDF

def extract_text_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    all_blocks = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if block['type'] == 0:  # Text block
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text'].strip()
                        if not text:
                            continue

                        all_blocks.append({
                            "text": text,
                            "font_size": span.get("size", 0),
                            "font": span.get("font", ""),
                            "flags": span.get("flags", 0),
                            "bbox": span.get("bbox", []),
                            "page": page_num + 1
                        })

    return all_blocks