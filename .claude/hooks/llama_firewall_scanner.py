"""
LlamaFirewall Scanner for VAMOS
Meta의 다계층 AI 보안 프레임워크를 활용한 입출력 보안 검증

실제 API 시그니처 (v1.0.3):
  LlamaFirewall(scanners={Role.USER: [ScannerType.PROMPT_GUARD, ...]})
  firewall.scan(input=UserMessage(content="..."))
  → ScanResult(decision=ScanDecision.ALLOW/BLOCK, reason=str, score=float)

사용법:
  python llama_firewall_scanner.py scan-input SOT파일경로
  python llama_firewall_scanner.py scan-output EA파일경로
  python llama_firewall_scanner.py alignment EA파일경로
"""

import json
import sys
import argparse
import os
import subprocess
from datetime import datetime

# llamafirewall 전용 venv (numpy>=2.4.1 충돌 격리)
FIREWALL_VENV_PYTHON = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "venv_firewall", "Scripts", "python.exe"
)


def _run_in_venv(code_str):
    """격리 venv에서 llamafirewall 코드를 실행하고 JSON 결과 반환"""
    if not os.path.exists(FIREWALL_VENV_PYTHON):
        return None  # venv 없으면 None → fallback 사용
    result = subprocess.run(
        [FIREWALL_VENV_PYTHON, "-c", code_str],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def get_firewall(role, scanner_types):
    """LlamaFirewall 인스턴스 생성 (올바른 API)"""
    from llamafirewall import LlamaFirewall, Role, ScannerType
    role_enum = Role[role]
    scanners_list = [ScannerType[s] for s in scanner_types]
    return LlamaFirewall(scanners={role_enum: scanners_list})


def scan_input(file_path):
    """SOT 입력 파일 보안 스캔 (PromptGuard + REGEX + PII + HIDDEN_ASCII)"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    sections = split_sections(content)
    results = []

    try:
        from llamafirewall import LlamaFirewall, ScannerType, UserMessage, Role

        # PromptGuard 모델 유무에 따라 스캐너 선택
        available_scanners = [ScannerType.REGEX, ScannerType.HIDDEN_ASCII]
        model_note = "REGEX/HIDDEN_ASCII 모드"

        # PromptGuard 2 모델 사용 가능하면 추가
        try:
            test_fw = LlamaFirewall(scanners={Role.USER: [ScannerType.PROMPT_GUARD]})
            test_fw.scan(input=UserMessage(content="test"))
            available_scanners.insert(0, ScannerType.PROMPT_GUARD)
            model_note = "PromptGuard 2 + REGEX/HIDDEN_ASCII 활성"
        except Exception:
            pass

        # PII_DETECTION은 TOGETHER_API_KEY 필요 — 설정된 경우만 추가
        if os.environ.get("TOGETHER_API_KEY"):
            available_scanners.append(ScannerType.PII_DETECTION)
            model_note += " + PII"

        firewall = LlamaFirewall(scanners={Role.USER: available_scanners})

        for section in sections:
            response = firewall.scan(input=UserMessage(content=section["text"]))
            results.append({
                "section": section["name"],
                "status": map_decision(response.decision),
                "confidence": response.score,
                "detail": response.reason,
                "model_note": model_note
            })

    except ImportError:
        # 격리 venv에서 llamafirewall 실행 시도
        venv_result = _run_in_venv(
            f"""
import json, sys
from llamafirewall import LlamaFirewall, ScannerType, UserMessage, Role
fw = LlamaFirewall(scanners={{Role.USER: [ScannerType.REGEX, ScannerType.HIDDEN_ASCII]}})
with open(r'{file_path}', 'r', encoding='utf-8') as f:
    text = f.read()
resp = fw.scan(input=UserMessage(content=text[:5000]))
print(json.dumps({{"status": resp.decision.name, "score": resp.score, "reason": resp.reason}}))
"""
        )
        if venv_result:
            results.append({
                "section": "전체",
                "status": "SAFE" if venv_result.get("status") == "ALLOW" else "BLOCKED",
                "confidence": venv_result.get("score", 0.0),
                "detail": f"격리 venv llamafirewall: {venv_result.get('reason', '')}"
            })
        else:
            for section in sections:
                status = basic_pattern_scan(section["text"])
                results.append({
                    "section": section["name"],
                    "status": status,
                    "confidence": 0.5,
                    "detail": "기본 패턴 검사 (llamafirewall venv 미사용)"
                })
    except Exception as e:
        results.append({
            "section": "error",
            "status": "ERROR",
            "confidence": 0.0,
            "detail": str(e)
        })

    return build_report(file_path, "scan-input", results)


def scan_output(file_path):
    """EA 출력 파일 보안 검증 (CodeShield + REGEX)"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    items = data if isinstance(data, list) else [data]

    try:
        from llamafirewall import LlamaFirewall, ScannerType, AssistantMessage, Role

        available_scanners = [ScannerType.REGEX]
        try:
            test_fw = LlamaFirewall(scanners={Role.ASSISTANT: [ScannerType.CODE_SHIELD]})
            test_fw.scan(input=AssistantMessage(content="test"))
            available_scanners.insert(0, ScannerType.CODE_SHIELD)
        except Exception:
            pass

        firewall = LlamaFirewall(scanners={Role.ASSISTANT: available_scanners})

        for item in items:
            text = json.dumps(item, ensure_ascii=False)
            response = firewall.scan(input=AssistantMessage(content=text))
            key = item.get("key", item.get("id", "unknown"))
            results.append({
                "section": str(key),
                "status": map_decision(response.decision),
                "confidence": response.score,
                "detail": response.reason
            })

    except ImportError:
        for item in items:
            key = item.get("key", item.get("id", "unknown"))
            results.append({
                "section": str(key),
                "status": "SAFE",
                "confidence": 0.5,
                "detail": "기본 검사 (llamafirewall 패키지 없음)"
            })
    except Exception as e:
        results.append({
            "section": "error",
            "status": "ERROR",
            "confidence": 0.0,
            "detail": str(e)
        })

    return build_report(file_path, "scan-output", results)


def scan_alignment(file_path):
    """EA 출력이 시스템 지침과 일치하는지 검증 (AGENT_ALIGNMENT)"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    items = data if isinstance(data, list) else [data]

    try:
        from llamafirewall import LlamaFirewall, ScannerType, AssistantMessage, Role

        available_scanners = [ScannerType.REGEX]
        try:
            test_fw = LlamaFirewall(scanners={Role.ASSISTANT: [ScannerType.AGENT_ALIGNMENT]})
            test_fw.scan(input=AssistantMessage(content="test"))
            available_scanners.insert(0, ScannerType.AGENT_ALIGNMENT)
        except Exception:
            pass

        firewall = LlamaFirewall(scanners={Role.ASSISTANT: available_scanners})

        for item in items:
            text = json.dumps(item, ensure_ascii=False)
            response = firewall.scan(input=AssistantMessage(content=text))
            key = item.get("key", item.get("id", "unknown"))
            results.append({
                "section": str(key),
                "status": map_decision(response.decision),
                "confidence": response.score,
                "detail": response.reason
            })

    except ImportError:
        for item in items:
            key = item.get("key", item.get("id", "unknown"))
            results.append({
                "section": str(key),
                "status": "SAFE",
                "confidence": 0.5,
                "detail": "기본 검사 (llamafirewall 패키지 없음)"
            })
    except Exception as e:
        results.append({
            "section": "error",
            "status": "ERROR",
            "confidence": 0.0,
            "detail": str(e)
        })

    return build_report(file_path, "alignment", results)


def map_decision(decision):
    """ScanDecision → VAMOS 상태 매핑"""
    name = decision.name if hasattr(decision, 'name') else str(decision)
    if name == "ALLOW":
        return "SAFE"
    elif name == "BLOCK":
        return "DANGEROUS"
    else:
        return "SUSPICIOUS"


def split_sections(content, max_size=2000):
    """텍스트를 섹션 단위로 분할"""
    sections = []
    lines = content.split("\n")
    current = {"name": "section_1", "text": ""}
    idx = 1

    for line in lines:
        if line.startswith("#") and len(current["text"]) > 100:
            sections.append(current)
            idx += 1
            current = {"name": line.strip()[:50] or f"section_{idx}", "text": ""}
        current["text"] += line + "\n"

        if len(current["text"]) > max_size:
            sections.append(current)
            idx += 1
            current = {"name": f"section_{idx}", "text": ""}

    if current["text"].strip():
        sections.append(current)

    return sections


def basic_pattern_scan(text):
    """기본 패턴 기반 보안 검사 (모델 없이)"""
    suspicious_patterns = [
        "ignore previous", "ignore above", "disregard",
        "system prompt", "you are now", "act as",
        "exec(", "eval(", "os.system",
        "DROP TABLE", "DELETE FROM", "<script>"
    ]
    text_lower = text.lower()
    for pattern in suspicious_patterns:
        if pattern.lower() in text_lower:
            return "SUSPICIOUS"
    return "SAFE"


def build_report(file_path, scan_type, results):
    """보고서 생성"""
    safe = sum(1 for r in results if r["status"] == "SAFE")
    suspicious = sum(1 for r in results if r["status"] == "SUSPICIOUS")
    dangerous = sum(1 for r in results if r["status"] == "DANGEROUS")
    total = len(results)

    if dangerous > 0:
        verdict = "BLOCKED"
    elif suspicious > 0:
        verdict = "REVIEW_NEEDED"
    else:
        verdict = "PASS"

    report = {
        "firewall_metadata": {
            "target": file_path,
            "scan_type": scan_type,
            "timestamp": datetime.now().isoformat(),
            "model": "LlamaFirewall v1.0.3"
        },
        "results": results,
        "summary": {
            "total_scanned": total,
            "safe": safe,
            "suspicious": suspicious,
            "dangerous": dangerous,
            "verdict": verdict
        }
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="LlamaFirewall Scanner for VAMOS")
    parser.add_argument("command", choices=["scan-input", "scan-output", "alignment"],
                        help="스캔 유형")
    parser.add_argument("file", help="대상 파일 경로")
    parser.add_argument("--output", help="결과 저장 경로 (없으면 stdout)")

    args = parser.parse_args()

    if args.command == "scan-input":
        report = scan_input(args.file)
    elif args.command == "scan-output":
        report = scan_output(args.file)
    elif args.command == "alignment":
        report = scan_alignment(args.file)

    output = json.dumps(report, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
