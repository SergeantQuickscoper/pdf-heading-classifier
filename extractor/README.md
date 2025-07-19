# Basic Program Flow

You give the program a pdf file and
it makes a new csv file in the csvs folder named after your pdf
for each page in the pdf
  - it grabs all the little text pieces with their positions and font info
  - it groups these pieces into lines based on how close they are vertically
  - for each line it splits the text into chunks if theres a big enough horizontal gap
  - it makes a TextChunk for each chunk which knows its text position and font details
after all chunks for the page are made it sorts them from top to bottom then left to right
it groups similar chunks into blocks like paragraphs or headings using rules about how close they are and how similar their font size is and the closeness depends on the font size too (a function i came up with just based on vibes)
for each block it figures out if most of the text is bold or italic
it writes a row to the csv for each block with info like page number block number the text font size size of the block if its bold or italic and where it is on the page
it does this for every page adding to the same csv
when its done you have a csv with all the text blocks and their features ready for whatever you want to do next

it uses a basic bfs search algorithm with some tolerance conditions on position and font size to decide whether to group or not. THats especially why it kinda sucks rn. Might need to look into other algorithms before formal training of the model.

# Running it Yourself

`mvn compile` - to compile it
`mvn exec:java -Dexec.args=./pdfs/yourPDfNameHere.pdf` - with the correct path to get the csv

then check the csvs folder for your csv result

Authored by: Don Roy Chacko <donisepic30@gmail.com>
