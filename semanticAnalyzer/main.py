from sentence_transformers import SentenceTransformer, util
import pandas as pd
import json
import glob
import os
from datetime import datetime
from collections import defaultdict
import subprocess
import shutil
import re
import numpy as np

csv_dir = "./csvs"
input_json_path = "./input.json"
output_json_path = "./semantic_output.json"
font_size_thresh = 8  # You can tune this

model = SentenceTransformer("all-MiniLM-L6-v2")

def sanitize_pdf_filenames(pdf_dir="./pdfs"):
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

def run_java_extractor(pdf_dir="./pdfs", extractor_dir="../extractor", output_csv_dir="./csvs"):
    os.makedirs(output_csv_dir, exist_ok=True)
    pdf_paths = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    if not pdf_paths:
        print("❌ No PDF files found in ./pdfs/")
        return
    for pdf_path in pdf_paths:
        abs_pdf_path = os.path.abspath(pdf_path)
        print(f"\n🔧 Extracting: {abs_pdf_path}")
        try:
            subprocess.run([
                "mvn", "exec:java", f"-Dexec.args={abs_pdf_path} 1.25 1.25 1.25"
            ], cwd=os.path.abspath(extractor_dir), check=True, shell=True)
            print("✅ Extraction complete.")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to extract {pdf_path}")
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
            print(f"⚠️ Missing CSV for {filename}")
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

# Main execution
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
    raise ValueError("❌ No headings extracted. Check font/bold threshold or data quality.")

title_embeddings = model.encode(titles, convert_to_tensor=True)
cos_scores = util.cos_sim(query_emb, title_embeddings)[0]
scored_sections = sorted(zip(doc_sections, cos_scores.tolist()), key=lambda x: x[1], reverse=True)

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

for rank, (sec, _) in enumerate(scored_sections[:5], 1):
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

seen_blocks = set()
for blk, _ in ranked_blocks:
    key = (blk["document"], blk["refined_text"])
    if key in seen_blocks:
        continue
    seen_blocks.add(key)
    output["subsection_analysis"].append(blk)
    if len(output["subsection_analysis"]) >= 5:
        break

with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✅ Output written to", output_json_path)