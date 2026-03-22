#!/bin/bash
# PreToolUse Hook: EA JSON 저장 시 결정론적 검증기 실행
# exit 0 = 허용, exit 2 = 차단
#
# stdin으로 JSON이 들어옴: {"tool_name": "Write", "tool_input": {"file_path": "...", "content": "..."}}

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)
FILE_PATH=$(echo "$INPUT" | python -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)

# Write 도구가 아니면 패스
if [ "$TOOL_NAME" != "Write" ]; then
    exit 0
fi

# EA JSON 파일이 아니면 패스
if ! echo "$FILE_PATH" | grep -q "v13_EA.*\.json$"; then
    exit 0
fi

# content를 임시 파일에 저장하여 검증
TEMP_FILE=$(mktemp /tmp/ea_validate_XXXXXX.json)
echo "$INPUT" | python -c "
import sys, json
data = json.load(sys.stdin)
content = data.get('tool_input', {}).get('content', '')
with open('$TEMP_FILE', 'w', encoding='utf-8') as f:
    f.write(content)
" 2>/dev/null

# 결정론적 검증기 실행 (DV-1~DV-9)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULT=$(python "$SCRIPT_DIR/deterministic_validator.py" "$TEMP_FILE" 2>&1)
EXIT_CODE=$?

# 임시 파일 정리
rm -f "$TEMP_FILE"

if [ $EXIT_CODE -eq 2 ]; then
    echo "[HOOK 차단] EA JSON이 결정론적 검증(DV-1~DV-9)을 통과하지 못했습니다:" >&2
    echo "$RESULT" | grep "CRITICAL" >&2
    echo "" >&2
    echo "CRITICAL 오류를 수정한 후 다시 저장하세요." >&2
    exit 2
fi

# 통과
exit 0