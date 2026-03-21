import React from 'react'

const OrderInbox: React.FC = () => {
  const alerts = [
    { id: 1, title: 'Order #882: Escrow Funded', action: 'DISPATCH DRIVER', type: 'order' },
    { id: 2, title: 'CropCycle #A2: Stage Check-in', action: 'LOG CHECK-IN', type: 'agri' },
  ]

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <div key={alert.id} className="flex items-center justify-between gap-3 bg-gray-50 p-3 rounded-lg border-l-4 border-orange-500 hover:bg-orange-50 transition-colors">
          <div className="flex-1">
            <p className="text-xs font-bold text-gray-800">{alert.title}</p>
            <p className="text-[10px] text-gray-500 mt-1 uppercase tracking-tighter">Action Required</p>
          </div>
          <button className="bg-orange-600 hover:bg-orange-700 text-white text-[10px] font-black px-3 py-2 rounded shadow-sm whitespace-nowrap active:scale-95 transition-transform uppercase">
            {alert.action}
          </button>
        </div>
      ))}
    </div>
  )
}

export default OrderInbox
