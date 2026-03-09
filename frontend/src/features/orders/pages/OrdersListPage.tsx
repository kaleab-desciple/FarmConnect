/**
 * Orders List Page
 * FarmConnect - AgriManagement
 * 
 * Displays orders for farmers and merchants with filtering and status tracking
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import { ordersAPI, Order, OrderStatus } from '../services/orders-api';
import { useAuthStore } from '../../../app/store/useAuthStore';
import { Spinner } from '../../../shared/components/ui/Spinner';

/**
 * Orders List Page Component
 */
export const OrdersListPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<OrderStatus | 'ALL'>('ALL');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  // Load orders
  useEffect(() => {
    loadOrders();
  }, [filter, page]);
  
  const loadOrders = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params: any = { page, page_size: 10 };
      if (filter !== 'ALL') {
        params.status = filter;
      }
      
      const response = await ordersAPI.list(params);
      setOrders(response.items || []);
      setTotalPages(Math.ceil((response.total || 0) / 10));
    } catch (err: any) {
      setError(err.response?.data?.detail || t('orders.errors.loadFailed'));
    } finally {
      setLoading(false);
    }
  };
  
  // Get status badge color
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'PENDING_PAYMENT':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'PAYMENT_FAILED':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      case 'FUNDED':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
      case 'PROCESSING':
        return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400';
      case 'PICKED_UP':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400';
      case 'IN_TRANSIT':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400';
      case 'DELIVERED':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'COMPLETED':
        return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400';
      case 'CANCELLED':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400';
      case 'DISPUTED':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400';
    }
  };
  
  // Format currency
  const formatCurrency = (amount?: number | string | null) => {
    if (!amount) return '—';
    const num = typeof amount === 'string' ? parseFloat(amount) : amount;
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
  };
  
  // Format date
  const formatDate = (dateStr?: string | null) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString();
  };
  
  // Get role-specific labels
  const isFarmer = user?.roles?.includes('FARMER');
  const otherPartyLabel = isFarmer ? t('orders.merchant') : t('orders.farmer');
  
  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">
          {t('orders.title')}
        </h1>
        <Link
          to="/orders/new"
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          {t('orders.newOrder')}
        </Link>
      </div>
      
      {/* Filters */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {(['ALL', 'PENDING_PAYMENT', 'FUNDED', 'PROCESSING', 'IN_TRANSIT', 'DELIVERED', 'COMPLETED'] as const).map((status) => (
          <button
            key={status}
            onClick={() => { setFilter(status); setPage(1); }}
            className={`px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              filter === status
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            {status === 'ALL' ? t('orders.filters.all') : t(`orders.status.${status.toLowerCase()}`)}
          </button>
        ))}
      </div>
      
      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center h-64">
          <Spinner size="lg" />
        </div>
      )}
      
      {/* Error State */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">{error}</p>
          <button
            onClick={loadOrders}
            className="mt-2 text-sm text-red-600 dark:text-red-400 hover:underline"
          >
            {t('common.retry')}
          </button>
        </div>
      )}
      
      {/* Orders List */}
      {!loading && !error && (
        <>
          {orders.length === 0 ? (
            <div className="text-center py-12">
              <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {t('orders.empty.title')}
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                {t('orders.empty.description')}
              </p>
              <Link
                to="/orders/new"
                className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                {t('orders.createFirst')}
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {orders.map((order) => (
                <Link
                  key={order.id}
                  to={`/orders/${order.id}`}
                  className="block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-green-500 dark:hover:border-green-500 transition-colors"
                >
                  <div className="p-4">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {t('orders.orderId')}: #{order.id?.slice(0, 8)}
                        </p>
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {order.product_name || order.product_id}
                        </p>
                      </div>
                      {order.status && (
                        <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getStatusColor(order.status)}`}>
                          {t(`orders.status.${order.status.toLowerCase()}`)}
                        </span>
                      )}
                    </div>
                    
                    {/* Details Grid */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500 dark:text-gray-400">{otherPartyLabel}</p>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {isFarmer ? order.merchant_id?.slice(0, 8) : order.farmer_id?.slice(0, 8)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500 dark:text-gray-400">{t('orders.quantity')}</p>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {order.quantity} {order.unit}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500 dark:text-gray-400">{t('orders.total')}</p>
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {formatCurrency(order.total_price)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500 dark:text-gray-400">{t('orders.date')}</p>
                        <p className="text-gray-900 dark:text-white">
                          {formatDate(order.created_at)}
                        </p>
                      </div>
                    </div>
                    
                    {/* Escrow Status */}
                    {order.escrow_id && (
                      <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                        <div className="flex items-center gap-2">
                          <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                          </svg>
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            {t('orders.escrowActive')}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 disabled:opacity-50"
              >
                {t('common.previous')}
              </button>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 disabled:opacity-50"
              >
                {t('common.next')}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default OrdersListPage;
