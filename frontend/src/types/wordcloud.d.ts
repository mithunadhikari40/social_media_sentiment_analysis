declare module 'wordcloud' {
  interface WordCloudOptions {
    list: Array<[string, number]>;
    gridSize?: number;
    weightFactor?: number;
    fontFamily?: string;
    color?: string | (() => string);
    backgroundColor?: string;
    rotateRatio?: number;
    rotationSteps?: number;
    minSize?: number;
    drawOutOfBound?: boolean;
  }

  function WordCloud(canvas: HTMLCanvasElement, options: WordCloudOptions): void;
  export = WordCloud;
}
