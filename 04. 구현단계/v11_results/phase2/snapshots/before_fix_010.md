# Before Fix 010 — FG-H06: 코드블록 deprecated API 수정
# Snapshot at: 2026-03-12

## L1025-1026 (§2 STEP-4 LangGraph set_entry_point/set_finish_point)
```
graph.set_entry_point("intake")
graph.set_finish_point("deliver")
```

## L840-841 (§2 STEP-3 Rust HashMap::get → Option, map_err 불가)
```
    state.config.read().get(&key)
        .map_err(|e| e.to_string())
```
