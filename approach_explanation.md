# Approach Explanation (deliverable)

This project is basically split into two main chunks: the extractor (Java) and the heading classifier + semantic analyzer (Python). The whole point is to take a raw PDF, break it down into something structured, figure out whats a heading and whats not, and then do some semantic analysis on top.

**Extractor (Java):**
You throw a PDF at the extractor and it goes page by page, grabbing every little text piece along with its position and font info. It groups these into lines if they’re close vertically, then splits lines into chunks if there’s a big enough horizontal gap. Each chunk becomes a `TextChunk`—basically just a bundle of text, position, and font details. Once all the chunks for a page are ready, it sorts them top-to-bottom, left-to-right. Then comes the grouping: similar chunks get bundled into blocks (think paragraphs or headings) using some basic BFS logic with tolerances on position and font size. For each block, it checks if most of the text is bold or italic, and then writes a row to a CSV with all the juicy details (page, block, text, font size, bold/italic, position, etc.). This repeats for every page, so you end up with a CSV per doc, ready for the next step. The extractor uses the following features to make its predictions, due to need of getting data ourselves, we overlooked some extra features and had limited data preparation to work with, but the current model gives good results for a hackathon level:
    - relFontSizeComparedToPage
    - relFontSizeComparedToDoc
    - avgFontSize
    - height
    - width
    - textLength
    - x0
    - y0
    - x1
    - y1
    - lineLength
    - bboxHeight
    - area
    - xCenter
    - yCenter
    - isBold
    - isItalic
    - wordCount

**Heading Classifier (Python):**
Once the CSVs are ready, the Python side kicks in. It loads up all the CSVs, checks for the columns it needs, and does a bunch of feature engineering—stuff like relative font size (compared to the page and doc), line length, area, word count, and so on. It handles missing values, encodes labels, and then trains a Random Forest to guess if a block is a heading (H1, H2, H3) or just body text. The model gets saved along with the label encoder and imputer. For inference, it does the same feature engineering on new CSVs, predicts heading levels, and then builds a nice outline (JSON) by picking out the headings and their levels. So you get a clean, structured summary for each doc, not just a wall of text.

**Semantic Analyzer (Python):**
This part is all about using Sentence Transformers (MiniLM-L6-v2) to actually understand what’s important in the docs. It starts by making sure PDF filenames are clean, runs the extractor if needed, and then reads the CSVs to pull out big text blocks (headings, sections, etc.). It encodes these with the transformer model. Given a persona and job-to-be-done (from input JSON), it creates a semantic query embedding and ranks all the sections by similarity. The top ones get picked as most relevant. It also groups adjacent blocks for more context, ranks those, and spits out a JSON with metadata, extracted sections, and grouped/refined blocks. Basically, you get a smart, query-driven summary of your docs.

**Overall:**
Everything’s containerized with Docker for easy setup. Java does the PDF extraction, Python does the ML and NLP, and they talk via CSVs and JSON, in a clean modular way.

Authored by: Don Roy Chacko <donisepic30@gmail.com>