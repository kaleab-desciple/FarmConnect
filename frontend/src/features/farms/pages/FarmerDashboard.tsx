/**
 * Farmer Dashboard Page
 * FarmConnect - AgriManagement
 * 
 * Implements the Interactive Map Dashboard from wireframes
 * with floating stats panels and slide-up sheets
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { farmsAPI } from '../services/farms-api';
import { ordersAPI } from '../../orders/services/orders-api';
import { Spinner } from '../../../shared/components/ui/Spinner';
import { Toast } from '../../../shared/components/ui/Toast';

/**
 * Map placeholder component - would integrate with Mapbox/Leaflet
 */
const FarmMap: React.FC<{ onFieldClick?: (fieldId: string) => void }> = ({ onFieldClick }) => {
  const { t } = useTranslation();
  
  return (
    <div className="relative w-full h-64 bg-green-100 rounded-xl overflow-hidden">
      {/* Map Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-green-200 to-green-300">
        {/* Simulated field polygons */}
        <svg className="w-full h-full" viewBox="0 0 400 200">
          {/* Field A - Maize (Yellow) */}
          <polygon
            points="50,80 100,60 150,80 140,130 60,120"
            fill="rgba(234, 179, 8, 0.5)"
            stroke="#ca8a04"
            strokeWidth="2"
            className="cursor-pointer hover:opacity-75 transition-opacity"
            onClick={() => onFieldClick?.('field-a')}
          />
          {/* Field B - Cabbage (Green) */}
          <polygon
            points="160,60 220,50 240,90 200,120 150,100"
            fill="rgba(22, 163, 74, 0.5)"
            stroke="#16a34a"
            strokeWidth="2"
            className="cursor-pointer hover:opacity-75 transition-opacity"
            onClick={() => onFieldClick?.('field-b')}
          />
          {/* Field C - Tomato (Red) */}
          <polygon
            points="60,140 120,130 140,170 80,180"
            fill="rgba(239, 68, 68, 0.5)"
            stroke="#dc2626"
            strokeWidth="2"
            className="cursor-pointer hover:opacity-75 transition-opacity"
            onClick={() => onFieldClick?.('field-c')}
          />
        </svg>
      </div>
      
      {/* Map Controls Overlay */}
      <div className="absolute top-2 right-2 flex flex-col gap-1">
        <button className="p-2 bg-white rounded-lg shadow-md hover:bg-gray-50" aria-label="Zoom in">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>
        <button className="p-2 bg-white rounded-lg shadow-md hover:bg-gray-50" aria-label="Zoom out">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
          </svg>
        </button>
        <button className="p-2 bg-white rounded-lg shadow-md hover:bg-gray-50" aria-label="My location">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
      </div>
      
      {/* Field Labels */}
      <div className="absolute top-2 left-2 bg-white/90 px-2 py-1 rounded text-xs font-medium">
        {t('dashboard.fields')}: 3
      </div>
    </div>
  );
};

/**
 * Stats Card Component
 */
const StatCard: React.FC<{
  icon: React.ReactNode;
  value: string | number;
  label: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
}> = ({ icon, value, label, trend, trendValue }) => {
  const trendColors = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-600'
  };
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg text-green-600 dark:text-green-400">
          {icon}
        </div>
        {trend && trendValue && (
          <span className={`text-xs font-medium ${trendColors[trend]}`}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trendValue}
          </span>
        )}
      </div>
      <div className="mt-2">
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
      </div>
    </div>
  );
};

/**
 * Alert Badge Component
 */
const AlertBadge: React.FC<{ count: number }> = ({ count }) => {
  if (count === 0) return null;
  
  return (
    <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full">
      {count > 9 ? '9+' : count}
    </span>
  );
};

/**
 * Main Dashboard Component
 */
export const FarmerDashboard: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [showStatsSheet, setShowStatsSheet] = useState(false);
  
  // Fetch farms data
  const { data: farmsData, isLoading: farmsLoading } = useQuery({
    queryKey: ['farms'],
    queryFn: farmsAPI.list,
  });
  
  // Fetch orders data
  const { data: ordersData, isLoading: ordersLoading } = useQuery({
    queryKey: ['orders', 'pending'],
    queryFn: () => ordersAPI.list({ status: 'PENDING_PAYMENT' }),
  });
  
  const isLoading = farmsLoading || ordersLoading;
  
  // Calculate stats
  const totalFarms = farmsData?.farms?.length || 0;
  const totalFields = farmsData?.farms?.reduce((acc, farm) => acc + (farm.fields?.length || 0), 0) || 0;
  const activeOrders = ordersData?.orders?.length || 0;
  const pendingHarvest = 2; // Would come from API
  
  // Handle field click on map
  const handleFieldClick = (fieldId: string) => {
    navigate(`/fields/${fieldId}`);
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Page Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {t('dashboard.welcome', { name: 'John' })}
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {new Date().toLocaleDateString(undefined, { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </p>
        </div>
      </div>
      
      {/* Interactive Map */}
      <section>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          {t('dashboard.myFarms')}
        </h2>
        <FarmMap onFieldClick={handleFieldClick} />
      </section>
      
      {/* Quick Stats Overview */}
      <section className="grid grid-cols-2 gap-3">
        <StatCard
          icon={
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          }
          value={totalFields}
          label={t('dashboard.activeCrops')}
        />
        <StatCard
          icon={
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          }
          value={1}
          label={t('dashboard.alerts')}
          trend="down"
          trendValue="1"
        />
        <StatCard
          icon={
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          }
          value={`${pendingHarvest}`}
          label={t('dashboard.harvestReady')}
        />
        <StatCard
          icon={
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          value="$450"
          label={t('dashboard.earnings')}
          trend="up"
          trendValue="12%"
        />
      </section>
      
      {/* Quick Actions */}
      <section className="flex gap-2 overflow-x-auto pb-2">
        <button
          onClick={() => navigate('/fields/new')}
          className="flex-shrink-0 px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          {t('dashboard.addField')}
        </button>
        <button
          onClick={() => navigate('/harvest/log')}
          className="flex-shrink-0 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z" />
          </svg>
          {t('dashboard.logHarvest')}
        </button>
        <button
          onClick={() => navigate('/ai-diagnosis')}
          className="flex-shrink-0 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          {t('dashboard.aiDiagnosis')}
        </button>
      </section>
      
      {/* Recent Activity */}
      <section className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          {t('dashboard.recentActivity')}
        </h3>
        <div className="space-y-3">
          {/* Activity Item */}
          <div className="flex items-start gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-full">
              <svg className="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {t('dashboard.irrigationDone')}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Field A - 2 hours ago</p>
            </div>
          </div>
          
          {/* Alert Item */}
          <div className="flex items-start gap-3">
            <div className="p-2 bg-amber-100 dark:bg-amber-900 rounded-full">
              <svg className="w-4 h-4 text-amber-600 dark:text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {t('dashboard.pestSpotted')}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Field B - 5 hours ago</p>
            </div>
          </div>
          
          {/* Harvest Item */}
          <div className="flex items-start gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-full">
              <svg className="w-4 h-4 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {t('dashboard.harvestLogged')}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Tomatoes - 50kg - Yesterday</p>
            </div>
          </div>
        </div>
      </section>
      
      {/* View More Button */}
      <button
        onClick={() => setShowStatsSheet(true)}
        className="w-full py-3 text-center text-green-600 dark:text-green-400 font-medium hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors"
      >
        {t('dashboard.viewAllStats')}
      </button>
      
      {/* Slide-up Stats Sheet (would be a bottom sheet in real implementation) */}
      {showStatsSheet && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50" onClick={() => setShowStatsSheet(false)}>
          <div className="bg-white dark:bg-gray-800 rounded-t-2xl w-full max-w-md p-4" onClick={e => e.stopPropagation()}>
            <div className="w-12 h-1 bg-gray-300 dark:bg-gray-600 rounded-full mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              {t('dashboard.farmStatistics')}
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">12.5 ha</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{t('dashboard.totalArea')}</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">3</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{t('dashboard.fields')}</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">3</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{t('dashboard.activeCycles')}</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">2</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{t('dashboard.harvestedThisSeason')}</p>
              </div>
            </div>
            <button
              onClick={() => setShowStatsSheet(false)}
              className="w-full mt-4 py-3 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg font-medium"
            >
              {t('common.close')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FarmerDashboard;
