import React from 'react'

const WeatherWidget: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-blue-400 rounded-xl p-4 text-white shadow-lg overflow-hidden relative">
      <div className="flex justify-between items-start z-10 relative">
        <div>
          <div className="text-sm font-medium opacity-80 uppercase tracking-wider">Agronomic Outlook</div>
          <div className="text-3xl font-bold mt-1">25°C</div>
          <div className="text-xs font-semibold bg-white/20 px-2 py-0.5 rounded-full mt-2 inline-block">
            Excellent Spraying Conditions
          </div>
        </div>
        <div className="text-4xl">⛅</div>
      </div>
      
      <div className="mt-4 flex gap-4 overflow-x-auto pb-2 scrollbar-hide z-10 relative">
        {[14, 15, 16, 17, 18].map((hour) => (
          <div key={hour} className="flex flex-col items-center min-w-[30px]">
            <span className="text-[10px] opacity-70">{hour}:00</span>
            <span className="text-sm my-1">⛅</span>
            <span className="text-[10px] font-bold">24°</span>
          </div>
        ))}
      </div>
      
      {/* Decorative sun flare */}
      <div className="absolute -top-10 -right-10 w-40 h-40 bg-yellow-400/20 blur-3xl rounded-full" />
    </div>
  )
}

export default WeatherWidget
