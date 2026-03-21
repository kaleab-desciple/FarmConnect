import React from 'react'
import { NavLink } from 'react-router-dom'

const MobileNav: React.FC = () => {
  return (
    <nav className="fixed bottom-0 left-0 right-0 h-20 bg-white border-t-2 border-green-800 flex items-center justify-around px-2 z-[100]">
      <NavLink 
        to="/farmer/dashboard" 
        className={({ isActive }) => `flex flex-col items-center gap-1 touch-target ${isActive ? 'text-green-800' : 'text-gray-500'}`}
      >
        <span className="text-xl">🏠</span>
        <span className="text-[10px] uppercase font-bold">Home</span>
      </NavLink>
      <NavLink 
        to="/farmer/fields" 
        className={({ isActive }) => `flex flex-col items-center gap-1 touch-target ${isActive ? 'text-green-800' : 'text-gray-500'}`}
      >
        <span className="text-xl">🌾</span>
        <span className="text-[10px] uppercase font-bold">Fields</span>
      </NavLink>
      <NavLink 
        to="/farmer/inventory" 
        className={({ isActive }) => `flex flex-col items-center gap-1 touch-target ${isActive ? 'text-green-800' : 'text-gray-500'}`}
      >
        <span className="text-xl">📦</span>
        <span className="text-[10px] uppercase font-bold">Inventory</span>
      </NavLink>
      <NavLink 
        to="/farmer/orders" 
        className={({ isActive }) => `flex flex-col items-center gap-1 touch-target ${isActive ? 'text-green-800' : 'text-gray-500'}`}
      >
        <span className="text-xl">🛒</span>
        <span className="text-[10px] uppercase font-bold">Orders</span>
      </NavLink>
    </nav>
  )
}

export default MobileNav
