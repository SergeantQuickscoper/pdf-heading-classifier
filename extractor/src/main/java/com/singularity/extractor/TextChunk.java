package com.singularity.extractor;


import org.apache.pdfbox.text.TextPosition;
import java.util.List;

public class TextChunk {
    public final String text;
    public final float x0, x1, y0, y1;
    public final float avgFontSize;
    public final float height, width;
    public final int textLength;

    public TextChunk(List<TextPosition> positions) {
        StringBuilder sb = new StringBuilder();
        float xMin = Float.MAX_VALUE, xMax = 0, yMin = Float.MAX_VALUE, yMax = 0, fontSum = 0, maxHeight = 0;
        for (TextPosition tp : positions) {
            sb.append(tp.getUnicode());
            fontSum += tp.getFontSizeInPt();
            xMin = Math.min(xMin, tp.getXDirAdj());
            xMax = Math.max(xMax, tp.getXDirAdj() + tp.getWidthDirAdj());
            yMin = Math.min(yMin, tp.getYDirAdj());
            yMax = Math.max(yMax, tp.getYDirAdj() + tp.getHeightDir());
            maxHeight = Math.max(maxHeight, tp.getHeightDir());
        }
        this.text = sb.toString().trim();
        this.x0 = xMin;
        this.x1 = xMax;
        this.y0 = yMin;
        this.y1 = yMax;
        this.avgFontSize = fontSum / positions.size();
        this.height = maxHeight;
        this.width = xMax - xMin;
        this.textLength = this.text.length();
    }

    public boolean isNearby(TextChunk other, float xThresh, float yThresh) {
        return Math.abs(this.y0 - other.y1) < yThresh && Math.abs(this.x0 - other.x1) < xThresh;
    }

    @Override
    public String toString() {
        return String.format("TextChunk{text='%s', x0=%.2f, x1=%.2f, y0=%.2f, y1=%.2f}", text, x0, x1, y0, y1);
    }
}