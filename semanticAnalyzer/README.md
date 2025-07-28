# Program flow

This section does semantic analysis on your PDFs. It finds the most important sections and groups similar blocks, so you get the summary of your documents.

## Giving Input (ENSURE INPUT.JSON AND THE PDFS ARE IN THE SAME INPUT FOLDER)

- Put your PDF files in the `./input` folder (make sure the names match what you put in the input JSON)
- Make an `input.json` in the `./input` folder
- The input JSON should be the one in the Adobe case briefing (like below):

```
{
    "challenge_info": {
        "challenge_id": "round_1b_002",
        "test_case_name": "travel_planner",
        "description": "France Travel"
    },
    "documents": [
        {
            "filename": "South of France - Cities.pdf",
            "title": "South of France - Cities"
        }
        // ... more docs
    ],
    "persona": {
        "role": "Travel Planner"
    },
    "job_to_be_done": {
        "task": "Plan a trip of 4 days for a group of 10 college friends."
    }
}
```

## Model Used

- This uses the `all-MiniLM-L6-v2` model from Sentence Transformers
- You need to download this model offline before running (the script expects it to be available locally, so make sure you have it cached or downloaded if you have no internet), if youre using outside the document container, SentenceTransformers should download automatically if you just mention the model

## What Happens When You Run It

- It checks your PDF filenames and renames them if they have spaces (so everything works)
- It runs the Java extractor on every PDF in the input folder (makes a CSV for each one in ./csvs)
- It reads those CSVs and pulls out the big text blocks (like headings and sections)
- It uses the transformer model to get embeddings and does some semantic ranking (finds important sections, groups similar stuff, etc)
- It writes the results to `output/output.json` (you get a list of extracted sections, some analysis, and metadata about your input)

## What You Get Out

- A `output.json` file in the output folder with stuff like:
  - Which PDFs you gave it
  - The persona and job you set
  - A list of extracted sections (with document name, section title, importance rank, page number)
  - Some grouped or refined text blocks for each doc

## How To Run (outside container)

Simply run:

```
python main.py
```

Authored by: Don Roy Chacko <donisepic30@gmail.com>
