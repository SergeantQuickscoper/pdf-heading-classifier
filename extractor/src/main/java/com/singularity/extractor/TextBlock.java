package com.singularity.extractor;

import java.util.*;

public class TextBlock {
    public final List<TextChunk> chunks;
    public final float x0, x1, y0, y1;
    public final float avgFontSize;

    public TextBlock(List<TextChunk> chunks) {
        this.chunks = chunks;
        this.x0 = (float) chunks.stream().mapToDouble(c -> c.x0).min().orElse(0);
        this.x1 = (float) chunks.stream().mapToDouble(c -> c.x1).max().orElse(0);
        this.y0 = (float) chunks.stream().mapToDouble(c -> c.y0).min().orElse(0);
        this.y1 = (float) chunks.stream().mapToDouble(c -> c.y1).max().orElse(0);
        this.avgFontSize = (float) chunks.stream().mapToDouble(c -> c.avgFontSize).average().orElse(0);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (TextChunk chunk : chunks) {
            sb.append(chunk.text).append(" ");
        }
        String content = sb.toString().trim();
        int textLength = content.length();
        float width = x1 - x0;
        float height = y1 - y0;
        return String.format(
            "TextBlock{content=\"%s\", avgFontSize=%.2f, height=%.2f, width=%.2f, textLength=%d, bbox=[x0=%.2f, y0=%.2f, x1=%.2f, y1=%.2f]}",
            content, avgFontSize, height, width, textLength, x0, y0, x1, y1
        );
    }
}

