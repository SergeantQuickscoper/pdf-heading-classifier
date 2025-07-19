package com.singularity.extractor;

import java.util.*;

public class TextBlockClassifier {

    private float verticalTolerance;
    private float horizontalTolerance;
    private float fontSizeTolerance;

    public TextBlockClassifier(float verticalTolerance, float horizontalTolerance, float fontSizeTolerance) {
        this.verticalTolerance = verticalTolerance;
        this.horizontalTolerance = horizontalTolerance;
        this.fontSizeTolerance = fontSizeTolerance;
    }

    // Uses BFS like search through the chunk array to group similar chunks in a train
    public List<TextBlock> classify(List<TextChunk> chunks) {
        List<TextBlock> blocks = new ArrayList<>();
        boolean[] visited = new boolean[chunks.size()];
        for (int i = 0; i < chunks.size(); i++) {
            if (visited[i]) continue;
            List<TextChunk> blockGroup = new ArrayList<>();
            Queue<Integer> queue = new LinkedList<>();
            queue.add(i);
            visited[i] = true;

            while (!queue.isEmpty()) {
                int current = queue.poll();
                TextChunk base = chunks.get(current);
                blockGroup.add(base);
                for(int j = 0; j < chunks.size(); j++){
                    if (visited[j]) continue;
                    TextChunk other = chunks.get(j);
                    if(areSimilar(base, other)){
                        queue.add(j);
                        visited[j] = true;
                    }
                }
            }

            blocks.add(new TextBlock(blockGroup));
        }

        return blocks;
    }
    
    // Definately should be a function of font size
    private boolean areSimilar(TextChunk a, TextChunk b) {
        float avgFont = (a.avgFontSize + b.avgFontSize) / 2.0f;
        float dy = Math.abs(a.y0 - b.y0);
        float dx = Math.abs(a.x0 - b.x0);
        float df = Math.abs(a.avgFontSize - b.avgFontSize);

        return dy <= verticalTolerance * avgFont &&
               dx <= horizontalTolerance * avgFont &&
               df <= fontSizeTolerance;
    }
}
