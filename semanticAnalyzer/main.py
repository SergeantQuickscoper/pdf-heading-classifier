from sentence_transformers import SentenceTransformer, util
import pandas as pd
import json
import glob
import os
from datetime import datetime
import subprocess
import shutil
import re
from collections import defaultdict
# MODIFYING THESE FOR DOCKER
# if running locally modify these (ill make an env later dw)
csv_dir = "/app/semanticAnalyzer/csvs"
input_json_path = "/app/semanticAnalyzer/input/input.json"
output_json_path = "/app/semanticAnalyzer/output/output.json"
font_size_thresh = 8  # tune this

model = SentenceTransformer("./model/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf/")

# MODIFYING THESE FOR DOCKER
# if running locally modify these
def sanitize_pdf_filenames(pdf_dir="/app/semanticAnalyzer/input/"):
    renamed_files = {}
    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith(".pdf") and " " in filename:
            original_path = os.path.join(pdf_dir, filename)
            sanitized_name = filename.replace(" ", "")
            sanitized_path = os.path.join(pdf_dir, sanitized_name)
            os.rename(original_path, sanitized_path)
            renamed_files[filename] = sanitized_name
            print(f"Renamed: {filename} → {sanitized_name}")
    return renamed_files

# MODIFYING THESE FOR DOCKER
# if running locally modify these
def run_java_extractor(pdf_dir="/app/semanticAnalyzer/input/", extractor_dir="/app/extractor", output_csv_dir="./csvs"):
    os.makedirs(output_csv_dir, exist_ok=True)
    pdf_paths = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    if not pdf_paths:
        print("No PDF files found in ./pdfs/")
        return
    for pdf_path in pdf_paths:
        abs_pdf_path = os.path.abspath(pdf_path)
        print(f"\n🔧 Extracting: {abs_pdf_path}")
        arg_str = f'"{abs_pdf_path} 1.25 1.25 1.25"'  # quotes around PDF path
        
        cmd = f'mvn exec:java -Dexec.args={arg_str}'
        try:
            subprocess.run(cmd, cwd=os.path.abspath(extractor_dir), check=True, shell=True)
            print("Extraction complete.")
        except subprocess.CalledProcessError:
            print(f"Failed to extract {pdf_path}")
            continue
        src_csv_dir = os.path.join(extractor_dir, "csvs")
        for csv_file in glob.glob(os.path.join(src_csv_dir, "*.csv")):
            shutil.move(csv_file, os.path.join(output_csv_dir, os.path.basename(csv_file)))
def normalize_filename(name):
    return re.sub(r"\s+", "", name)
def extract_sections_from_csvs(csv_dir, documents, font_size_thresh=8):
    all_sections = []
    for doc in documents:
        filename = doc["filename"]
        base = normalize_filename(os.path.splitext(filename)[0])
        csv_path = os.path.join(csv_dir, base + ".csv")
        if not os.path.exists(csv_path):
            print(f"Missing CSV for {filename}")
            continue
        df = pd.read_csv(csv_path)
        df["avgFontSize"] = pd.to_numeric(df["avgFontSize"], errors="coerce")
        df["isBold"] = df["isBold"].fillna(0).astype(int)
        df = df.dropna(subset=["avgFontSize"])
        for _, row in df.iterrows():
            text = str(row.get("content", "")).strip()
            if not text or len(text) < 10:
                continue
            if row["avgFontSize"] >= font_size_thresh or row["isBold"]:
                all_sections.append({
                    "document": filename,
                    "title": text,
                    "page_number": int(row.get("page", 1))
                })
    return all_sections
def group_adjacent_blocks_for_subsections(csv_dir, documents):
    all_blocks = []
    for doc in documents:
        filename = doc["filename"]
        base = normalize_filename(os.path.splitext(filename)[0])
        csv_path = os.path.join(csv_dir, base + ".csv")
        if not os.path.exists(csv_path):
            continue
        df = pd.read_csv(csv_path)
        df = df.sort_values(by=["page", "block"])
        current_group = []
        current_page = None
        last_block = None
        for _, row in df.iterrows():
            page = int(row.get("page", 1))
            block = int(row.get("block", -1))
            text = str(row.get("content", "")).strip()
            if not text:
                continue
            if (current_page != page) or (last_block is not None and block != last_block + 1):
                if current_group:
                    grouped_text = " ".join(current_group).replace("\n", " ").strip()
                    all_blocks.append({
                        "document": filename,
                        "refined_text": grouped_text,
                        "page_number": current_page
                    })
                    current_group = []
                current_page = page
            current_group.append(text)
            last_block = block
        if current_group:
            grouped_text = " ".join(current_group).replace("\n", " ").strip()
            all_blocks.append({
                "document": filename,
                "refined_text": grouped_text,
                "page_number": current_page
            })
    return all_blocks
sanitize_pdf_filenames()
run_java_extractor()
with open(input_json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
persona = data.get("persona", {}).get("role", "Persona")
job = data.get("job_to_be_done", {}).get("task", "Some job")
query = f"{persona}. Task: {job}"
query_emb = model.encode(query, convert_to_tensor=True)
doc_sections = extract_sections_from_csvs(csv_dir, data["documents"], font_size_thresh)
titles = [s["title"] for s in doc_sections]
if not titles:
    raise ValueError("No headings extracted. Check font/bold threshold or data quality.")
title_embeddings = model.encode(titles, convert_to_tensor=True)
cos_scores = util.cos_sim(query_emb, title_embeddings)[0]

scored_sections = list(zip(doc_sections, cos_scores.tolist()))

MIN_SCORE_THRESHOLD = 0.25 
scored_sections = [(sec, score) for sec, score in scored_sections if score >= MIN_SCORE_THRESHOLD]

scored_sections = sorted(scored_sections, key=lambda x: x[1], reverse=True)

sections_by_doc = defaultdict(list)
for sec, score in scored_sections:
    sections_by_doc[sec["document"]].append((sec, score))

seen_titles = set()
final_sections = []
section_limit = 8

while len(final_sections) < section_limit:
    added = False
    for doc, section_list in sections_by_doc.items():
        if len(final_sections) >= section_limit:
            break
        while section_list:
            sec, score = section_list.pop(0)
            key = (sec["document"], sec["title"])
            if key in seen_titles:
                continue
            seen_titles.add(key)
            final_sections.append(sec)
            added = True
            break
    if not added:
        break

output = {
    "metadata": {
        "input_documents": [doc["filename"] for doc in data["documents"]],
        "persona": persona,
        "job_to_be_done": job,
        "processing_timestamp": datetime.now().isoformat()
    },
    "extracted_sections": [],
    "subsection_analysis": []
}

# Step 5: Assign ranked output
for rank, sec in enumerate(final_sections, 1):
    output["extracted_sections"].append({
        "document": sec["document"],
        "section_title": sec["title"],
        "importance_rank": rank,
        "page_number": sec["page_number"]
    })

grouped_blocks = group_adjacent_blocks_for_subsections(csv_dir, data["documents"])
block_texts = [blk["refined_text"] for blk in grouped_blocks]
block_embeddings = model.encode(block_texts, convert_to_tensor=True)
block_scores = util.cos_sim(query_emb, block_embeddings)[0]
ranked_blocks = sorted(zip(grouped_blocks, block_scores.tolist()), key=lambda x: x[1], reverse=True)


doc_weights = defaultdict(lambda: 1) 
for i, section in enumerate(output["extracted_sections"]):
    doc = section["document"]
    doc_weights[doc] = max(6 - i, 1)


grouped_by_doc = defaultdict(list)
for blk, score in ranked_blocks:
    grouped_by_doc[blk["document"]].append((blk, score))

# Step 3: Select top 5 blocks using weighted round-robin
seen_blocks = set()
final_blocks = []

while len(final_blocks) < 8:
    added = False
    for doc, weight in sorted(doc_weights.items(), key=lambda x: -x[1]):
        if len(final_blocks) >= 8:
            break
        if not grouped_by_doc[doc]:
            continue
        blk, _ = grouped_by_doc[doc].pop(0)
        key = (blk["document"], blk["refined_text"])
        if key in seen_blocks:
            continue
        seen_blocks.add(key)
        final_blocks.append(blk)
        added = True
    if not added:
        break

output["subsection_analysis"] = final_blocks

with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print("Output written to", output_json_path)