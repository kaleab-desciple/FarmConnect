import React from 'react'

const Header: React.FC = () => {
  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 flex items-center px-4 z-50 md:pl-64">
      <div className="text-xl font-bold text-green-800">FarmConnect</div>
      <div className="flex-1" />
      <div className="flex items-center gap-4">
        <button className="touch-target">🔔</button>
        <div className="w-8 h-8 rounded-full bg-green-200 border border-green-800 flex items-center justify-center text-xs font-bold transition-all hover:scale-105 cursor-pointer">
          JD
        </div>
      </div>
    </header>
  )
}

export default Header
