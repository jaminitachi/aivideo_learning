import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "VideoEngAI - AI 비디오 아바타 영어 학습",
  description: "AI 비디오 아바타와 실시간으로 대화하며 영어를 학습하세요",
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 5,
    userScalable: true,
    // 모바일에서 전체화면 모드 지원
    viewportFit: "cover",
  },
  // 모바일 브라우저 최적화
  themeColor: "#7c3aed",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
