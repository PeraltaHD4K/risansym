import type { NodePosition } from '@/lib/schema';
import styles from './Visualizer.module.css';
import { PADDING_X } from './constants';

interface LifelineLayerProps {
  nodes: NodePosition[];
  totalWidth: number;
}

/** Renders horizontal dashed lines for each node (lifelines). */
export default function LifelineLayer({ nodes, totalWidth }: LifelineLayerProps) {
  return (
    <>
      {nodes.map(node => (
        <g key={`lifeline-${node.id}`}>
          <text x={10} y={node.y + 5} className={styles.nodeLabel}>N{node.id}</text>
          <line
            x1={PADDING_X} y1={node.y}
            x2={totalWidth - 50} y2={node.y}
            className={styles.lifeline}
            strokeDasharray="4,4"
          />
        </g>
      ))}
    </>
  );
}
