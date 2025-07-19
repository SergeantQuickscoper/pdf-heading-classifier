package com.singularity.extractor;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.TextPosition;
import org.apache.pdfbox.text.PDFTextStripper;
import java.io.File;
import java.io.IOException;
import java.util.*;

public class PdfFeatureExtractor extends PDFTextStripper {

    public PdfFeatureExtractor() throws IOException {
        super.setSortByPosition(true);
    }

    @Override
    public void writeString(String string, List < TextPosition > textPositions) throws IOException {
        // this is too bloated, i should implement something like a text block class, but that might impact performance
        
        Map<Float, List<TextPosition>> lines = new TreeMap<>(Collections.reverseOrder());
        float lineThreshold = 2.0f; // y distance to group into same line
        float xThreshold = 100.0f; // x distance to group into same chunk

        // Group text into lines based on y coordinate
        for(TextPosition tp: textPositions) {
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
                lines.put(y, new ArrayList < > (List.of(tp)));
            }
        }

        // Process each line
        for(List<TextPosition> line: lines.values()) {
            // Sort text left to right
            line.sort(Comparator.comparing(TextPosition::getXDirAdj));
            List <List<TextPosition>> chunks = new ArrayList <>();
            List <TextPosition> currentChunk = new ArrayList <>();

            for (int i = 0; i < line.size(); i++) {
                TextPosition tp = line.get(i);

                if (currentChunk.isEmpty()) {
                    currentChunk.add(tp);
                } else {
                    TextPosition last = currentChunk.get(currentChunk.size() - 1);
                    float gap = tp.getXDirAdj() - (last.getXDirAdj() + last.getWidthDirAdj());

                    if (gap > xThreshold) {
                        chunks.add(currentChunk);
                        currentChunk = new ArrayList < > ();
                    }
                    currentChunk.add(tp);
                }
            }

            if (!currentChunk.isEmpty()) {
                chunks.add(currentChunk);
            }

            // Feature extraction per chunk
            for (List < TextPosition > chunk: chunks) {
                StringBuilder textBuilder = new StringBuilder();
                float avgFontSize = 0;
                float xMin = Float.MAX_VALUE, xMax = 0, y = 0, height = 0;

                for (TextPosition tp: chunk) {
                    textBuilder.append(tp.getUnicode());
                    avgFontSize += tp.getFontSizeInPt();
                    xMin = Math.min(xMin, tp.getXDirAdj());
                    xMax = Math.max(xMax, tp.getXDirAdj() + tp.getWidthDirAdj());
                    y = tp.getYDirAdj();
                    height = Math.max(height, tp.getHeightDir());
                }

                avgFontSize /= chunk.size();

                Map < String, Object > lineFeatures = new LinkedHashMap < > ();
                lineFeatures.put("text", textBuilder.toString().trim());
                lineFeatures.put("avg_font_size", avgFontSize);
                lineFeatures.put("x0", xMin);
                lineFeatures.put("x1", xMax);
                lineFeatures.put("y", y);
                lineFeatures.put("height", height);
                lineFeatures.put("width", xMax - xMin);
                lineFeatures.put("text_length", textBuilder.toString().trim().length());
        // TODO: Add more features
        // TODO: Write to JSON/CSV
                System.out.println(lineFeatures);
            }
        }
    }


    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.err.println("do java PdfFeatureExtractor <path>");
            return;
        }
        File pdfFile = new File(args[0]);
        try (PDDocument document = PDDocument.load(pdfFile)) {
            PdfFeatureExtractor stripper = new PdfFeatureExtractor();
            stripper.setStartPage(1);
            stripper.setEndPage(document.getNumberOfPages());
            stripper.getText(document);
            document.close();
        }
    }
}
