import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/components/providers/QueryProvider";

export const metadata: Metadata = {
  title: "Awesome List Crawler",
  description: "Discover awesome GitHub repositories with terminal-style browsing",
  icons: {
    icon: [
      {
        url: "data:image/svg+xml,%3Csvg width='32' height='32' viewBox='0 0 32 32' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='32' height='32' fill='%23000000' stroke='%2300ff41' stroke-width='1'/%3E%3Ctext x='2' y='12' font-family='monospace' font-size='8' fill='%2300ff41'%3E%24%3C/text%3E%3Crect x='10' y='6' width='6' height='8' fill='%2300ff41'/%3E%3Ctext x='2' y='24' font-family='monospace' font-size='6' fill='%2300ff41'%3Eawesome%3C/text%3E%3C/svg%3E",
        type: "image/svg+xml",
        sizes: "32x32"
      }
    ]
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-terminal-bg text-terminal-text font-mono antialiased">
        <QueryProvider>
          {children}
        </QueryProvider>
      </body>
    </html>
  );
}
