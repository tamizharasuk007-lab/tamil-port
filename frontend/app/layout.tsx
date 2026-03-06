import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Quant Signal Dashboard',
  description: 'Real-time >=90% probability trading signals'
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
