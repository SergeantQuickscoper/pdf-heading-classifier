# Program Flow

This project contains two parts: the extractor, which will be in the src directory, written in Java.
The other is the ML classifier that uses Random Forest classification, located in the model directory, written in Python.

Below both these sections will be explained:

## The Extractor
You give the program a pdf file and
it makes a new csv file in the csvs folder named after your pdf
for each page in the pdf
  it grabs all the little text pieces with their positions and font info
  it groups these pieces into lines based on how close they are vertically
  for each line it splits the text into chunks if theres a big enough horizontal gap
  it makes a TextChunk for each chunk which knows its text position and font details
after all chunks for the page are made it sorts them from top to bottom then left to right
it groups similar chunks into blocks like paragraphs or headings using rules about how close they are and how similar their font size is and the closeness depends on the font size too
for each block it figures out if most of the text is bold or italic
it writes a row to the csv for each block with info like page number block number the text font size size of the block if its bold or italic and where it is on the page
it does this for every page adding to the same csv
when its done you have a csv with all the text blocks and their features ready for whatever you want to do next

it uses a basic bfs search algorithm with some tolerance conditions on position and font size to decide whether to group or not. THats especially why it kinda sucks rn. Might need to look into other algorithms before formal training of the model.

### Running it Yourself

`mvn compile` - to compile it
`mvn exec:java -Dexec.args=./pdfs/yourPDfNameHere.pdf` - with the correct path to get the csv

## The Classifier
The classifier lives in the model folder. After the csvs are made, it grabs each csv and runs a heading classifier on it. This classifier looks at the features for each block (like font size, bold, italic, position, and more) and tries to guess if a block is a heading (like H1, H2, H3) or just body text. It uses a trained random forest model for this. It then builds an outline for the document by picking out the headings and their levels, and saves that as a json file (outline.json) for each pdf. So you end up with a structured outline for every document, not just a big blob of text.

## Dockerfile Flow

When you build the Docker image, it sets up: Java, Maven, Python, all the requirements, and builds the Java code. When you run the container, it looks in /app/input for all your pdfs. For each pdf, it runs the extractor to make a csv, then runs the classifier to make a json outline. It puts all the jsons in /app/output, and also makes a output.json that has all the outlines together.

Authored by: Don Roy Chacko <donisepic30@gmail.com>
