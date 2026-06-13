// IPC 응답 타입 (V0 — 백엔드 stub 봉투. 정본 스키마는 shared/types/vamos.ts).

export interface DecisionResult {
  method?: string;
  trace_id?: string;
  v0_stub?: boolean;
  conclusion?: string;
  locked?: boolean;
  // A25 신뢰도 (V1에서 채워짐 — V0 stub은 부재 가능)
  confidence_score?: number; // 0.0~1.0
  confidence_level?: "HIGH" | "MEDIUM" | "LOW" | "REFUSE";
  // A22 투명성 (gates.reasoning_trace 등)
  gates?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface WorkflowResult {
  trace_id?: string;
  user_response?: string;
  evidence_summary?: string;
  v0_stub?: boolean;
  [key: string]: unknown;
}
