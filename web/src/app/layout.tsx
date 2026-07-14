import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { TraceProvider } from "@/lib/TraceContext";
import { PlaybackProvider } from "@/lib/PlaybackContext";
import ErrorBoundary from "@/components/ErrorBoundary";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Risansym | Distributed Systems Simulator",
  description: "A premium visualizer for discrete event simulation traces.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${outfit.variable}`}>
        <ErrorBoundary>
          <TraceProvider>
            <PlaybackProvider>
              {children}
            </PlaybackProvider>
          </TraceProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
