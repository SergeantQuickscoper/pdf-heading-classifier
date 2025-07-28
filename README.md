# PDF Heading Analyzer 

A offline tool to extract PDF text data, classify titles as H1, H2, H3, and semantically analyze them based on a job and persona.

## Project Overview

This repo has two main folders:

- **extractor**: This is where the PDF text extraction and heading classifier pipeline lives. It uses Java (for the extractor) and Python (for the heading classifier). There's a Dockerfile in this folder for running the whole pipeline in a container. Make sure to `cd extractor` before building or running Docker commands for this part.

- **semanticAnalyzer**: This is the semantic analysis and smart section ranking part. It's all in Python and uses Sentence Transformers. There's a separate Dockerfile in the root directory for running the semantic analyzer in a container. *As the semanticAnalyzer depends on the extractor engine, please run this dockerfile from the root directory ONLY.* Ignore any warnings that my pop up during the docker run, as they are mostly related to my installing of cpu only libraries of pytorch. ENSURE input.json AND all the pdfs ARE IN THE SAME INPUT FOLDER

## Running each deliverable and expected execution
The project follows the recommended execution format in the brief:
Change into the folder you want to work with before running Docker build or run commands.
In a nutshell:

- for deliverable A: build and run docker from `cd extractor` 
- for deliverable B: build and run docker from `the root dir`

Please use mounted input and output folders similar to below (for powershell)
docker run --rm -v "${PWD}//input:/app/input:ro" -v "${PWD}/output:/app/output" --network none mysolutionname:somerandomidentifier

For deliverable A, simply put your pdfs inside the mounted input folder.

For deliverable B, put your input.json AND all your PDFs in the mounted input folder, no nested directories.

Authored by: Don Roy Chacko <donisepic30@gmail.com>