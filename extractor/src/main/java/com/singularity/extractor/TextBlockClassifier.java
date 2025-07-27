package com.singularity.extractor;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

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
        float dy = Math.abs(a.y1 - b.y0);
        float dy1 = Math.abs(a.y0 - b.y1);
        if(dy>dy1)dy=dy1;
        float dx = Math.abs(a.x0 - b.x0);
        float dx1 = Math.abs(a.x1 - b.x1);
        if(dx>dx1)dx=dx1;

        float df = Math.abs(a.avgFontSize - b.avgFontSize);

        return dy <= verticalTolerance * avgFont &&
               dx <= horizontalTolerance * avgFont &&
               df <= fontSizeTolerance;
    }

}
