package com.singularity.extractor;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.TextPosition;
import org.apache.pdfbox.text.PDFTextStripper;
import java.io.File;
import java.io.IOException;
import java.util.*;
import org.apache.pdfbox.pdmodel.PDPage;
import java.io.FileWriter;
import java.io.BufferedWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;

public class PdfFeatureExtractor extends PDFTextStripper {

    // BLOCK CLASSIFICATION TOLERANCES (pixel count as a percentage of fontsize)
    private final float verticalTolerance = 1.5f;
    private final float horizontalTolerance = 1.5f;
    private final float fontSizeTolerance = 1.0f;

    // CHUNK CLASSFICIATION TOLERENCES
    private final float lineThreshold = 2.0f; // y distance to group into same line
    private float xThreshold = 100.0f; // x distance to group into same chunk

    // Collect all TextPositions for the page
    private final List<TextPosition> allPositions = new ArrayList<>();
    private String csvPath = null;
    private boolean headerWritten = false;

    public PdfFeatureExtractor(String pdfFilePath) throws IOException {
        super.setSortByPosition(true);
        String baseName = new File(pdfFilePath).getName().replaceAll("(?i)\\.pdf$", "");
        Path csvDir = Path.of("csvs");
        if (!Files.exists(csvDir)) Files.createDirectories(csvDir);
        csvPath = csvDir.resolve(baseName + ".csv").toString();
        Files.deleteIfExists(Path.of(csvPath));
        headerWritten = false;
    }

    @Override
    public void writeString(String string, List<TextPosition> textPositions) throws IOException {
        allPositions.addAll(textPositions);
    }

    @Override
    protected void endPage(PDPage page) throws IOException {
        // Chunking and block classification logic (was in writeString)
        Map<Float, List<TextPosition>> lines = new TreeMap<>(Collections.reverseOrder());
        // Group text into lines based on y coordinate
        for(TextPosition tp: allPositions) {
            float y = tp.getYDirAdj();
            boolean added = false;
            for(Float key: lines.keySet()) {
                if (Math.abs(key - y) < lineThreshold) {
                    lines.get(key).add(tp);
                    added = true;
                    break;
                }
            }
            if(!added){
                lines.put(y, new ArrayList<>(List.of(tp)));
            }
        }

        List<TextChunk> textChunks = new ArrayList<>();
        // Process each line
        for(List<TextPosition> line: lines.values()) {
            // Sorting within line
            line.sort(Comparator.comparing(TextPosition::getXDirAdj));
            List <List<TextPosition>> chunks = new ArrayList<>();
            List <TextPosition> currentChunk = new ArrayList<>();

            // Dividing lines into chunks
            for (int i = 0; i < line.size(); i++) {
                TextPosition tp = line.get(i);
                if(currentChunk.isEmpty()){
                    currentChunk.add(tp);
                } 
                else{
                    // Todo: this logic may be flawed as hell
                    TextPosition last = currentChunk.get(currentChunk.size() - 1);
                    float gap = tp.getXDirAdj() - (last.getXDirAdj() + last.getWidthDirAdj());
                    if(gap > xThreshold){
                        chunks.add(currentChunk);
                        currentChunk = new ArrayList<>();
                    }
                    currentChunk.add(tp);
                }
            }

            if(!currentChunk.isEmpty()){
                chunks.add(currentChunk);
            }

            // Load Text Chunks
            for (List<TextPosition> chunk : chunks) {
                TextChunk textChunk = new TextChunk(chunk);
                textChunks.add(textChunk);
               
            }
        }

        // Sort chunks by y then x
        textChunks.sort(Comparator.comparing((TextChunk c) -> c.y0).thenComparing(c -> c.x0));

        // Print tolerances and classify blocks once per page
        // System.out.println("Vertical Tolerance: " + verticalTolerance + "\nHorizontoal Tolerance: " + horizontalTolerance + "\nFont Size Tolerance: " + fontSizeTolerance);
        TextBlockClassifier classifier = new TextBlockClassifier(verticalTolerance, horizontalTolerance, fontSizeTolerance);
        List<TextBlock> blocks = classifier.classify(textChunks);
        try (BufferedWriter writer = Files.newBufferedWriter(Path.of(csvPath), StandardOpenOption.CREATE, StandardOpenOption.APPEND)) {
            if (!headerWritten) {
                writer.write("page,block,content,avgFontSize,height,width,textLength,x0,y0,x1,y1,isBold,isItalic\n");
                headerWritten = true;
            }
            int pageNum = getCurrentPageNo();
            int blockNum = 0;
            for (TextBlock block : blocks) {
                String content = block.chunks.stream().map(c -> c.text.replace("\"", "'")).reduce((a, b) -> a + " " + b).orElse("").replaceAll("\n", " ").trim();
                int textLength = content.length();
                String csvContent = String.format("%d,%d,\"%s\",%.2f,%.2f,%.2f,%d,%.2f,%.2f,%.2f,%.2f,%b,%b\n",
                    pageNum, blockNum++,
                    content,
                    block.avgFontSize, block.y1-block.y0, block.x1-block.x0, textLength,
                    block.x0, block.y0, block.x1, block.y1, block.isBold, block.isItalic);
                writer.write(csvContent);
            }
        }
        allPositions.clear();
    }


    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.err.println("do java PdfFeatureExtractor <path>");
            return;
        }
        File pdfFile = new File(args[0]);
        try (PDDocument document = PDDocument.load(pdfFile)) {
            PdfFeatureExtractor stripper = new PdfFeatureExtractor(args[0]);
            stripper.setStartPage(1);
            stripper.setEndPage(document.getNumberOfPages());
            stripper.getText(document);
            document.close();
        }
    }
}
