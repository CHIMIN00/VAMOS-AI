// Tauri IPC 커맨드 5종 래퍼 (V0-STEP-3). 논리명 vamos:* ↔ Rust 함수.
import { invoke } from "@tauri-apps/api/core";

import type { DecisionResult, WorkflowResult } from "./types/ipc";

/** vamos:decision:create → langgraph.decision.create */
export function decisionCreate(input: Record<string, unknown>): Promise<DecisionResult> {
  return invoke<DecisionResult>("decision_create", { input });
}

/** vamos:workflow:start → langgraph.workflow.run */
export function workflowStart(input: Record<string, unknown>): Promise<WorkflowResult> {
  return invoke<WorkflowResult>("workflow_start", { input });
}

/** vamos:ui:log_stream → Tauri 이벤트 구독 */
export function uiLogStream(subscribe: boolean): Promise<unknown> {
  return invoke("ui_log_stream", { subscribe });
}

/** vamos:ui:config_get → Rust 직접 */
export function uiConfigGet(key: string): Promise<unknown> {
  return invoke("ui_config_get", { key });
}

/** vamos:ui:config_set → Rust 직접 */
export function uiConfigSet(key: string, value: string): Promise<unknown> {
  return invoke("ui_config_set", { key, value });
}
