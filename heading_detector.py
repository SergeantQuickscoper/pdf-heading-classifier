def classify_level(block):
    size = block["font_size"]
    if size >= 16:
        return "Title"
    elif size >= 14:
        return "H1"
    elif size >= 12:
        return "H2"
    elif size >= 10:
        return "H3"
    else:
        return None

def generate_outline(blocks):
    title = None
    outline = []

    for b in blocks:
        level = classify_level(b)
        if level:
            if level == "Title" and not title:
                title = b["text"]
            else:
                outline.append({
                    "level": level,
                    "text": b["text"],
                    "page": b["page"]
                })

    return {
        "title": title or "Untitled Document",
        "outline": outline
    }