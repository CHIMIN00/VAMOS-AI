#!/bin/bash
# PostToolUse Hook: SOT 파일 수정 감지 및 영향 범위 알림
# SOT 파일이 Edit/Write되면 영향받는 EA/CM을 알려줌
#
# stdin으로 JSON이 들어옴: {"tool_name": "...", "tool_input": {"file_path": "..."}}

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)

# SOT 디렉토리의 파일인지 확인
if ! echo "$FILE_PATH" | grep -qiE "(docs[/\\\\]sot|D2\.0|D3\.0|PART2)"; then
    exit 0
fi

# SOT 파일명 추출
SOT_FILENAME=$(basename "$FILE_PATH")

echo "[HOOK 경고] SOT 파일이 수정되었습니다: $SOT_FILENAME"
echo ""
echo "영향 범위 확인이 필요합니다:"
echo "  1. 이 파일을 참조하는 EA의 source_line/source_text가 무효화될 수 있습니다"
echo "  2. 해당 EA를 참조하는 CM 결과도 영향받습니다"
echo ""
echo "권장 조치:"
echo "  /integrity $SOT_FILENAME  — 영향받는 EA/CM 확인"
echo "  /sot-cache refresh        — 캐시 갱신"
echo ""

# EA 디렉토리에서 해당 SOT 파일을 참조하는 EA 찾기
EA_DIR="D:/VAMOS/04. 구현단계/v13_results/phase0/extraction"
if [ -d "$EA_DIR" ]; then
    AFFECTED_EAS=$(grep -l "$SOT_FILENAME" "$EA_DIR"/v13_EA*.json 2>/dev/null | xargs -I{} basename {} 2>/dev/null)
    if [ -n "$AFFECTED_EAS" ]; then
        echo "영향받는 EA:"
        echo "$AFFECTED_EAS" | while read ea; do echo "  - $ea"; done
        echo ""
        echo "이 EA들의 재추출이 필요할 수 있습니다."
    fi
fi

exit 0
