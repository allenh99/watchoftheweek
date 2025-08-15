import type { Metadata } from "next";
import { Inter, Montserrat, Roboto, Open_Sans, DM_Serif_Display, Source_Serif_4 } from "next/font/google";
import Navbar from '../components/Navbar';
import "./globals.css";

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

const montserrat = Montserrat({
  variable: "--font-montserrat",
  subsets: ["latin"],
  display: 'swap',
});

const roboto = Roboto({
  weight: ['300', '400', '500', '700'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto',
});

const openSans = Open_Sans({
  weight: ['300', '400', '500', '600', '700'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-open-sans',
});

const dmSerifDisplay = DM_Serif_Display({
  weight: ['400'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-dm-serif-display',
});

const sourceSerif = Source_Serif_4({
  weight: ['400'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-source-serif',
});
export const metadata: Metadata = {
  title: "Movie Recommendation Engine",
  description: "Get personalized movie recommendations based on your ratings",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="m-0 p-0">
      <body className={`${openSans.className} ${montserrat.variable} ${roboto.variable} ${dmSerifDisplay.variable} ${sourceSerif.variable} antialiased m-0 p-0 bg-gray-900`}>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
