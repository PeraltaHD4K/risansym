export const downloadSVG = (topologyName?: string) => {
  const svgElement = document.getElementById('visualizer-svg');
  if (!svgElement) {
    alert("No se encontró el lienzo del visualizador.");
    return;
  }

  const clonedSvg = svgElement.cloneNode(true) as SVGSVGElement;
  const serializer = new XMLSerializer();
  let source = serializer.serializeToString(clonedSvg);

  if (!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)) {
    source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
  }
  
  // Inject styles directly so the downloaded SVG looks identical
  const styleString = `
    <style>
      :root {
        --bg-color: #0f111a;
        --panel-border: rgba(255, 255, 255, 0.2);
        --text-primary: #e2e8f0;
        --text-secondary: #94a3b8;
        --danger-color: #ef4444;
        --font-outfit: system-ui, sans-serif;
        --font-inter: system-ui, sans-serif;
      }
      svg { background-color: var(--bg-color); }
      [class*="nodeLabel"] { font-family: var(--font-outfit); font-weight: 600; fill: var(--text-primary); font-size: 14px; }
      [class*="lifeline"] { stroke: var(--panel-border); stroke-width: 1; }
      [class*="timeAxis"] { stroke: var(--text-secondary); stroke-width: 2; }
      [class*="timeTick"] { fill: var(--text-secondary); font-size: 10px; font-family: var(--font-inter); text-anchor: middle; }
      [class*="messageLabel"] { font-family: var(--font-inter); font-size: 10px; font-weight: 600; text-anchor: middle; }
      [class*="playhead"] { stroke: var(--danger-color); stroke-width: 2; stroke-dasharray: 6,4; }
    </style>
  `;
  
  source = source.replace('>', `>${styleString}`);

  const blob = new Blob([source], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `traza_${topologyName || 'export'}.svg`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};
