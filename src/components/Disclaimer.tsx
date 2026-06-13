// A16 — 면책 조항(Responsible AI). AI 산출물은 검토 대상임을 고지.
export default function Disclaimer() {
  return (
    <footer
      style={{
        marginTop: "2rem",
        paddingTop: "1rem",
        borderTop: "1px solid #d0d7de",
        color: "#57606a",
        fontSize: "0.8rem",
      }}
    >
      ⚠️ 본 결과는 AI가 생성한 보조 자료입니다. 중요한 의사결정 전 사람의 검토가 필요하며,
      VAMOS는 결과의 정확성·완전성을 보증하지 않습니다. (A16 Responsible AI)
    </footer>
  );
}
