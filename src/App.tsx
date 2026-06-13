// V0 셸 UI (4-3 Should) — 5 커맨드 배선 + A22(왜?)/A25(신뢰도)/A16(면책).
import { useState } from "react";

import ConfidenceBadge from "./components/ConfidenceBadge";
import Disclaimer from "./components/Disclaimer";
import WhyButton from "./components/WhyButton";
import { decisionCreate, workflowStart } from "./ipc";
import type { DecisionResult, WorkflowResult } from "./types/ipc";

// 서버 측 위조 방지를 위해 trace_id는 백엔드 생성이 원칙(A-보안 #3).
// V0 UI는 데모용 placeholder만 전달하며, 정본 trace_id는 백엔드가 채운다.
const DEMO_TRACE = "ui-demo";

export default function App() {
  const [goal, setGoal] = useState("");
  const [decision, setDecision] = useState<DecisionResult | null>(null);
  const [workflow, setWorkflow] = useState<WorkflowResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onDecision() {
    setBusy(true);
    setError(null);
    try {
      const res = await decisionCreate({
        trace_id: DEMO_TRACE,
        intent_frame_ref: "if-demo",
        evidence_pack_ref: "ev-demo",
        output_spec: { format_constraints: "markdown" },
      });
      setDecision(res);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onWorkflow() {
    setBusy(true);
    setError(null);
    try {
      const res = await workflowStart({ trace_id: DEMO_TRACE, user_input: goal });
      setWorkflow(res);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ fontFamily: "system-ui", padding: "2rem", maxWidth: 820, margin: "0 auto" }}>
      <h1>VAMOS</h1>
      <p style={{ color: "#57606a" }}>V0 데스크톱 셸 — IPC JSON-RPC 브릿지 (P4-2).</p>

      <section style={{ marginTop: "1rem" }}>
        <label htmlFor="goal">요청</label>
        <textarea
          id="goal"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          rows={3}
          style={{ display: "block", width: "100%", marginTop: "0.25rem" }}
          placeholder="예: 단일 코드블럭으로 파서 작성"
        />
        <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem" }}>
          <button onClick={onWorkflow} disabled={busy}>
            워크플로우 시작
          </button>
          <button onClick={onDecision} disabled={busy}>
            Decision 생성
          </button>
        </div>
      </section>

      {error && (
        <p style={{ color: "#cf222e", marginTop: "1rem" }}>오류: {error}</p>
      )}

      {workflow && (
        <section style={{ marginTop: "1.5rem" }}>
          <h2>워크플로우 결과</h2>
          <p>{workflow.user_response || "(V0 stub — 응답 본문은 V1)"}</p>
        </section>
      )}

      {decision && (
        <section style={{ marginTop: "1.5rem" }}>
          <h2>Decision</h2>
          <p>
            결론: <strong>{decision.conclusion ?? "—"}</strong> ·{" "}
            <ConfidenceBadge score={decision.confidence_score} level={decision.confidence_level} />
          </p>
          <WhyButton gates={decision.gates} />
        </section>
      )}

      <Disclaimer />
    </main>
  );
}
