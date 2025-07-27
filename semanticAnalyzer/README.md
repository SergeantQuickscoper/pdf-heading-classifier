# How To Use main.py

## Giving Input

- Put your PDF files in the `./pdfs` folder (make sure the names match what you put in the input JSON)
- Make an `input.json` in the same folder as main.py
- The input JSON should look like this (just copy and change the filenames and titles if you want):

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

## What Happens When You Run It

- It checks your PDF filenames and renames them if they have spaces (so everything works)
- It runs the Java extractor on every PDF in the pdfs folder (makes a CSV for each one in ./csvs)
- It reads those CSVs and pulls out the big text blocks (like headings and sections)
- It uses a transformer model to get embeddings and does some semantic stuff (finds important sections, groups similar stuff, etc)
- It writes the results to `semantic_output.json` (you get a list of extracted sections, some analysis, and metadata about your input)

## What You Get Out

- A `semantic_output.json` file with stuff like:
  - Which PDFs you gave it
  - The persona and job you set
  - A list of extracted sections (with document name, section title, importance rank, page number)
  - Some grouped or refined text blocks for each doc

## How To Run

Just do

```
python main.py
```

(Make sure you have the requirements installed, and your PDFs and input.json are in the right place)
