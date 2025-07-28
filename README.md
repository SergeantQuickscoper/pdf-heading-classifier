# PDF Heading Analyzer 

A offline tool to extract PDF text data, classify titles as H1, H2, H3, and semantically analyze them based on a job and persona.

## Project Overview

This repo has two main folders:

- **extractor**: This is where the PDF text extraction and heading classifier pipeline lives. It uses Java (for the extractor) and Python (for the heading classifier). There's a Dockerfile in this folder for running the whole pipeline in a container. Make sure to `cd extractor` before building or running Docker commands for this part.

- **semanticAnalyzer**: This is the semantic analysis and smart section ranking part. It's all in Python and uses Sentence Transformers. There's a separate Dockerfile here for running the semantic analyzer in a container. Make sure to `cd semanticAnalyzer` before building or running Docker for this part. It does however rely on the Java extractor module from the other folder, but don't worry this is handled in code and the docker container.

Each folder is self contained, so always change into the folder you want to work with before running Docker build or run commands.

Authored by: Don Roy Chacko <donisepic30@gmail.com>