import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "../contexts/ThemeContext";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const playfairDisplay = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Circularity Nexus - Tokenize Trash. Earn Wealth. Heal the Planet.",
  description: "Revolutionary waste-to-wealth tokenization platform powered by Hedera blockchain. Transform your trash into tradeable tokens, carbon credits, and real rewards while healing our planet.",
  keywords: ["blockchain", "sustainability", "waste management", "tokenization", "carbon credits", "circular economy", "hedera", "defi"],
  authors: [{ name: "Circularity Nexus Team" }],
  creator: "Circularity Nexus",
  publisher: "Circularity Nexus",
  robots: "index, follow",
  openGraph: {
    title: "Circularity Nexus - Tokenize Trash. Earn Wealth. Heal the Planet.",
    description: "Revolutionary waste-to-wealth tokenization platform powered by Hedera blockchain.",
    type: "website",
    locale: "en_US",
    siteName: "Circularity Nexus",
  },
  twitter: {
    card: "summary_large_image",
    title: "Circularity Nexus - Tokenize Trash. Earn Wealth. Heal the Planet.",
    description: "Revolutionary waste-to-wealth tokenization platform powered by Hedera blockchain.",
  },
  viewport: "width=device-width, initial-scale=1",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#10b981" },
    { media: "(prefers-color-scheme: dark)", color: "#064e3b" },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${playfairDisplay.variable} antialiased transition-colors duration-200`}
      >
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
