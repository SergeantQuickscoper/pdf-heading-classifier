#!/bin/bash

set -e

if [ $# -ne 2 ]; then
  echo "Usage: $0 <input-pdf-path> <output-directory>"
  exit 1
fi

INPUT_PDF="$1"
OUTPUT_DIR="$2"

if [ ! -f "$INPUT_PDF" ]; then
  echo "Error: PDF file '$INPUT_PDF' does not exist."
  exit 1
fi

if [ ! -d "$OUTPUT_DIR" ]; then
  echo "Error: Output directory '$OUTPUT_DIR' does not exist."
  exit 1
fi

echo "Input PDF: $INPUT_PDF"
echo "Output directory: $OUTPUT_DIR"

mvn exec:java -Dexec.mainClass="your.package.PdfExtractor" -Dexec.args="$INPUT_PDF"

INPUT_PDF="test.pdf"
BASENAME=$(basename "$INPUT_PDF" .pdf)
CSV_PATH="../csvs/${BASENAME}.csv"

cd model
python inference.py --input $CSV_PATH
cd ..

mv model/outline.json "$OUTPUT_DIR/outline.json"

echo "Pipeline completed. Outline saved to $OUTPUT_DIR/outline.json"
