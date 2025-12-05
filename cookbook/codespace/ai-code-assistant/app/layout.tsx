import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Code Assistant - Powered by AgentBay',
  description: 'Execute Python code in the cloud with AI assistance',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-gray-950 text-white antialiased">{children}</body>
    </html>
  );
}
