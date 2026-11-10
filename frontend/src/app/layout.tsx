import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

export const metadata: Metadata = {
  title: "Kartavya AI — Pass on what matters, with proof",
  description: "Evidence-linked, permission-aware knowledge handover platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-[#F6F0E6] text-[#222B25]">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
