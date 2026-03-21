import React from 'react'

const FarmMap: React.FC = () => {
  return (
    <div className="w-full h-full bg-slate-100 flex items-center justify-center relative">
      <div className="absolute inset-0 opacity-20 bg-[url('https://www.transparenttextures.com/patterns/graphy.png')]" />
      
      {/* Schematic Map Representation */}
      <div className="relative w-4/5 h-4/5 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
        <div className="absolute top-4 left-4 w-20 h-20 bg-green-500/50 border border-green-700 flex items-center justify-center text-[10px] font-bold text-green-900">
          NORTH
        </div>
        <div className="absolute bottom-4 right-4 w-24 h-24 bg-yellow-500/50 border border-yellow-700 flex items-center justify-center text-[10px] font-bold text-yellow-900">
          EAST
        </div>
        <div className="w-4 h-4 bg-red-600 rounded-full shadow-[0_0_10px_rgba(220,38,38,0.5)] animate-pulse" />
        <span className="text-[10px] absolute translate-y-6 font-bold text-red-700">YOU</span>
      </div>
      
      <div className="absolute bottom-2 right-2 bg-white/80 backdrop-blur-sm px-2 py-1 rounded text-[8px] font-mono border border-gray-200">
        Lat: 9.0123 / Lng: 38.7654
      </div>
    </div>
  )
}

export default FarmMap
