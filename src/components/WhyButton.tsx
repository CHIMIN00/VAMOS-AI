// A22 — [왜?] 투명성 버튼. reasoning_trace / gates를 펼쳐 보인다(D6 metadata 틀).
import { useState } from "react";

interface Props {
  gates?: Record<string, unknown>;
}

export default function WhyButton({ gates }: Props) {
  const [open, setOpen] = useState(false);
  const reasoning = gates?.["reasoning_trace"];
  return (
    <div style={{ marginTop: "0.5rem" }}>
      <button onClick={() => setOpen((v) => !v)} aria-expanded={open}>
        {open ? "▼ 왜?" : "▶ 왜?"}
      </button>
      {open && (
        <pre
          style={{
            background: "#f6f8fa",
            padding: "0.75rem",
            borderRadius: 6,
            overflowX: "auto",
            fontSize: "0.8rem",
          }}
        >
          {reasoning !== undefined
            ? JSON.stringify(reasoning, null, 2)
            : gates !== undefined
              ? JSON.stringify(gates, null, 2)
              : "추론 추적 미제공 (V0 stub — reasoning_trace는 V1에서 채워짐)"}
        </pre>
      )}
    </div>
  );
}
