import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  title: "AI Loan Assistant", // Updated title
  description: "AI-powered loan assistant application", // Updated description
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      {/* Apply the background and minimum height to the body */}
      <body className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-900 flex flex-col">
          <Header />
          <main className="flex-1 container mx-auto px-4 py-6 md:py-8">
            {children}
          </main>
          <Footer />
      </body>
    </html>
  );
}