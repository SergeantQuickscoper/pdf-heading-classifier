import os
import json
from extractor.pdf_reader import extract_text_blocks
from extractor.heading_detector import generate_outline

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "input", "sample2.pdf")
    output_path = os.path.join(base_dir, "output", "sample2.json")

    print("Looking for:", input_path)
    if not os.path.exists(input_path):
        print("❌ sample2.pdf not found in input/")
        exit()

    blocks = extract_text_blocks(input_path)
    outline = generate_outline(blocks)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(outline, f, indent=2)

    print("✅ Outline extracted and saved to:", output_path)