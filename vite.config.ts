import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Tauri 2.0 데스크톱 셸용 Vite 설정 (V0-STEP-1).
// Tauri는 고정 포트의 dev 서버 + ../dist 정적 빌드를 기대한다.
export default defineConfig({
  plugins: [react()],
  // Tauri는 정적 자산을 상대 경로로 로드 → base 상대화
  base: "./",
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
  },
  build: {
    outDir: "dist",
    target: "es2020",
    emptyOutDir: true,
  },
});
