import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "MYTH CHASER",
    description: "Your AI-powered anti-scam and myth-busting assistant",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body>{children}</body>
        </html>
    );
}
