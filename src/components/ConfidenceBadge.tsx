// A25 — 예측 신뢰도 표시 (confidence_score 0~100% + level). 임계 0.85/0.60/0.30 (config LOCK).
interface Props {
  score?: number;
  level?: string;
}

const LEVEL_COLOR: Record<string, string> = {
  HIGH: "#1a7f37",
  MEDIUM: "#9a6700",
  LOW: "#bc4c00",
  REFUSE: "#cf222e",
};

export default function ConfidenceBadge({ score, level }: Props) {
  if (score === undefined || level === undefined) {
    return <span style={{ color: "#666" }}>신뢰도: N/A (V0 stub)</span>;
  }
  const pct = Math.round(score * 100);
  return (
    <span
      style={{
        padding: "0.15rem 0.5rem",
        borderRadius: 4,
        color: "#fff",
        background: LEVEL_COLOR[level] ?? "#666",
        fontSize: "0.85rem",
      }}
      title="A25 예측 신뢰도 (임계 0.85/0.60/0.30 — config LOCK)"
    >
      신뢰도 {pct}% · {level}
    </span>
  );
}
