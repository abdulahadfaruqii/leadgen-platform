import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LeadGen AI - Enterprise Lead Generation",
  description: "AI-powered multi-agent lead generation platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
