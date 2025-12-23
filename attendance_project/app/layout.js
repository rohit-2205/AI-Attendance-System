// src/app/layout.js
import { Geist, Geist_Mono } from "next/font/google";
import './globals.css'; // Ensure global styles are imported
import { ThemeProvider } from "./ThemeProvider"; // Directly from the package

// Import Google Fonts for custom typography
const geistSans = Geist({
  variable: "--font-geist-sans", // Define a custom CSS variable for the font
  subsets: ["latin"], // Define the subsets for the font
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono", // Define a custom CSS variable for the mono font
  subsets: ["latin"], // Define the subsets for the font
});

// Metadata for the page (title, description, etc.)
export const metadata = {
  title: "My Next.js App", // Customize your app title here
  description: "A web app built with Next.js and Firebase", // Customize your app description
};

export default function layout({ children }) {
  return (
    <>
      <html lang="en" suppressHydrationWarning>
        <head />
        <body>
          <ThemeProvider
            attribute="class" // Use the "class" attribute to toggle dark mode
            defaultTheme="light" // Use system default theme
            enableSystem // Enable system theme detection (light or dark)
            disableTransitionOnChange // Disable transition animations during theme switch
          >
            {children}
          </ThemeProvider>
        </body>
      </html>
    </>
  );
}