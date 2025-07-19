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
    public void writeString(String string, List<TextPosition> textPositions) throws IOException {
        // TODO: Add column and X value detection (though i dont think it matters)
        // Group text positions by line
        Map<Float, List<TextPosition>> lines = new TreeMap<>(Collections.reverseOrder());
        float lineThreshold = 2.0f; // experimental line threshold yolo
        
        for (TextPosition tp : textPositions) {
            float y = tp.getYDirAdj();
            boolean added = false;

            for (Float key : lines.keySet()) {
                if (Math.abs(key - y) < lineThreshold) {
                    lines.get(key).add(tp);
                    added = true;
                    break;
                }
            }

            if (!added) {
                lines.put(y, new ArrayList<>(List.of(tp)));
            }
        }

        for (List<TextPosition> line : lines.values()) {
            line.sort(Comparator.comparing(TextPosition::getXDirAdj)); 

            StringBuilder textBuilder = new StringBuilder();
            float avgFontSize = 0;
            float xMin = Float.MAX_VALUE, xMax = 0, y = 0, height = 0;

            for (TextPosition tp : line) {
                textBuilder.append(tp.getUnicode());
                avgFontSize += tp.getFontSizeInPt();
                xMin = Math.min(xMin, tp.getXDirAdj());
                xMax = Math.max(xMax, tp.getXDirAdj() + tp.getWidthDirAdj());
                y = tp.getYDirAdj();
                height = Math.max(height, tp.getHeightDir());
            }

        avgFontSize /= line.size();
        
        // Write features for export
        Map<String, Object> lineFeatures = new LinkedHashMap<>();
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
