import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const FarmerOrderHistory: React.FC = () => {
  const navigate = useNavigate();
  // Mock ongoing orders
  const [orders] = useState([
    { id: '#882', buyer: 'FreshMart City', items: '800kg Tomatoes', status: 'FUNDED - Wait Dispatch', total: '$1,200.00', date: 'Today, 09:30 AM' },
    { id: '#880', buyer: 'Local Agri CoOp', items: '2000kg Corn', status: 'DELIVERED - Escrow Releasing', total: '$800.00', date: 'Yesterday' },
    { id: '#875', buyer: 'GreenGroce LLC', items: '500kg Romaine', status: 'COMPLETED', total: '$450.00', date: 'Mar 15, 2026' }
  ]);

  return (
    <div className="space-y-4">
      {orders.map((order, idx) => (
        <div key={order.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="flex justify-between items-start mb-2">
            <div>
              <span className="text-xs font-bold text-gray-500">{order.id}</span>
              <h3 className="font-bold text-gray-900 text-sm">{order.buyer}</h3>
            </div>
            <div className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider
              ${order.status.includes('FUNDED') ? 'bg-orange-100 text-orange-800 border border-orange-200' : 
                order.status.includes('DELIVERED') ? 'bg-blue-100 text-blue-800 border border-blue-200' : 
                'bg-green-100 text-green-800 border border-green-200'}`}>
              {order.status}
            </div>
          </div>
          
          <div className="text-sm text-gray-700 mb-3">
            {order.items}
          </div>
          
          <div className="flex justify-between items-end border-t border-gray-100 pt-3">
            <div className="text-xs text-gray-500">{order.date}</div>
            <div className="font-bold text-green-800">{order.total}</div>
          </div>

          {order.status.includes('FUNDED') && (
            <button className="w-full mt-4 bg-green-700 text-white rounded-lg py-2 text-sm font-bold shadow-sm active:scale-95 uppercase tracking-wider">
              Dispatch Driver
            </button>
          )}
        </div>
      ))}
    </div>
  );
};

export default FarmerOrderHistory;
