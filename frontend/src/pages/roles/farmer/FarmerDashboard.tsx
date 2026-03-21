import React from 'react'
import FarmMap from '@features/farms/components/FarmMap'
import WeatherWidget from '@features/weather/components/WeatherWidget'
import OrderInbox from '@features/orders/components/OrderInbox'

const FarmerDashboard: React.FC = () => {
  return (
    <div className="space-y-6 p-4 pt-20 pb-24">
      {/* Dashboard Tabs */}
      <div className="flex bg-white rounded-lg p-1 shadow-sm border border-gray-100">
        <button className="flex-1 py-2 text-sm font-bold bg-green-800 text-white rounded-md shadow-sm">Agronomy</button>
        <button className="flex-1 py-2 text-sm font-bold text-gray-500">Market</button>
        <button className="flex-1 py-2 text-sm font-bold text-gray-500">Logistics</button>
      </div>

      <section>
        <WeatherWidget />
      </section>

      <section className="bg-white rounded-xl shadow-sm border border-orange-100 p-4">
        <h2 className="text-lg font-bold text-orange-900 flex items-center gap-2 mb-4">
          ⚠️ Action Required
        </h2>
        <OrderInbox />
      </section>

      <section className="bg-white rounded-xl shadow-sm border border-green-100 overflow-hidden">
        <div className="p-4 border-b border-green-50">
          <h2 className="text-lg font-bold text-green-900">Farm Overview</h2>
        </div>
        <div className="h-[300px] relative">
          <FarmMap />
        </div>
      </section>

      <div className="grid grid-cols-3 gap-4">
        <button className="flex flex-col items-center justify-center p-4 bg-green-800 text-white rounded-xl shadow-md transition-transform hover:scale-95 active:scale-90">
          <span className="text-2xl">➕</span>
          <span className="text-[10px] font-bold mt-2">TASK</span>
        </button>
        <button className="flex flex-col items-center justify-center p-4 bg-green-700 text-white rounded-xl shadow-md transition-transform hover:scale-95 active:scale-90">
          <span className="text-2xl">📸</span>
          <span className="text-[10px] font-bold mt-2">AI SCAN</span>
        </button>
        <button className="flex flex-col items-center justify-center p-4 bg-green-600 text-white rounded-xl shadow-md transition-transform hover:scale-95 active:scale-90">
          <span className="text-2xl">📝</span>
          <span className="text-[10px] font-bold mt-2">LOG</span>
        </button>
      </div>
    </div>
  )
}

export default FarmerDashboard
