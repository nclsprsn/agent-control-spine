import type { Metadata } from "next";
import { Poppins, JetBrains_Mono } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { getLocale, getMessages } from "next-intl/server";
import "./globals.css";
import { ConversationSidebar } from "@/components/chat/conversation-sidebar";

const poppins = Poppins({
  variable: "--font-poppins",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400"],
});

export const metadata: Metadata = {
  title: "Spine — Chat",
  description: "Chat with AI agents",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getLocale();
  const messages = await getMessages();

  return (
    <html
      lang={locale}
      className={`${poppins.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <body className="h-full flex bg-background text-foreground font-[family-name:var(--font-poppins)]">
        <NextIntlClientProvider messages={messages}>
          <ConversationSidebar />
          <main className="flex-1 flex flex-col h-full overflow-hidden">{children}</main>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
