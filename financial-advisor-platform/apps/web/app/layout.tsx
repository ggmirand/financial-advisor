import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Advisor Dashboard",
  description: "Personal financial advisor platform"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <div className="mx-auto max-w-7xl px-4 py-6">{children}</div>
      </body>
    </html>
  );
}
