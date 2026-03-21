import React from 'react'
import MobileNav from './MobileNav'
import Header from './Header'

interface AppLayoutProps {
  children: React.ReactNode
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-[#f8f9fa]">
      <Header />
      <main className="flex-1 pb-20">
        {children}
      </main>
      <MobileNav />
    </div>
  )
}

export default AppLayout
