#!/bin/bash
set -e

INPUT_DIR="/app/input"
OUTPUT_DIR="/app/output"
CSV_DIR="/app/csvs"
MODEL_DIR="/app/model"

mkdir -p "$CSV_DIR"
mkdir -p "$OUTPUT_DIR"

outlines=()

for pdf in "$INPUT_DIR"/*.pdf; do
  [ -e "$pdf" ] || continue
  fname=$(basename "$pdf" .pdf)
  echo "Processing $pdf"
  mvn exec:java -Dexec.mainClass="com.singularity.extractor.PdfFeatureExtractor" -Dexec.args="$pdf" || continue
  csv_file="$CSV_DIR/$fname.csv"
  if [ -f "$csv_file" ]; then
    python3 "$MODEL_DIR/inference.py" --input "$csv_file"
    if [ -f outline.json ]; then
      mv outline.json "$OUTPUT_DIR/$fname.json"
      outlines+=("$OUTPUT_DIR/$fname.json")
    fi
  fi
done

# Merge all outlines into output.json if any
if [ ${#outlines[@]} -gt 0 ]; then
  echo '[' > "$OUTPUT_DIR/output.json"
  first=1
  for f in "${outlines[@]}"; do
    if [ $first -eq 0 ]; then echo ',' >> "$OUTPUT_DIR/output.json"; fi
    cat "$f" >> "$OUTPUT_DIR/output.json"
    first=0
  done
  echo ']' >> "$OUTPUT_DIR/output.json"
fi

exit 0 