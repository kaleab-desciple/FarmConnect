/**
 * Harvest List Page
 * FarmConnect - AgriManagement
 * 
 * Displays harvest batches for crops with quality tracking
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import api from '../../../app/services/api';
import { Spinner } from '../../../shared/components/ui/Spinner';

/**
 * Harvest Batch Type
 */
interface HarvestBatch {
  id: string;
  crop_cycle_id: string;
  crop_name: string;
  field_name: string;
  harvest_date: string;
  quantity_kg: number;
  quality_grade: 'A' | 'B' | 'C';
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  price_per_kg?: number;
  buyer_id?: string;
  notes?: string;
}

/**
 * Harvest List Page Component
 */
export const HarvestListPage: React.FC = () => {
  const { t } = useTranslation();
  const { farmId, fieldId } = useParams<{ farmId: string; fieldId?: string }>();
  
  const [harvests, setHarvests] = useState<HarvestBatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Load harvests
  useEffect(() => {
    loadHarvests();
  }, [farmId, fieldId]);
  
  const loadHarvests = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = fieldId ? { field_id: fieldId } : {};
      const response = await api.get('/api/v1/harvest/batches', { params });
      setHarvests(response.data.items || response.data || []);
    } catch (err: any) {
      // If endpoint doesn't exist, show empty state
      setHarvests([]);
    } finally {
      setLoading(false);
    }
  };
  
  // Get status badge color
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'IN_PROGRESS':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
      case 'COMPLETED':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'CANCELLED':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400';
    }
  };
  
  // Get quality grade color
  const getGradeColor = (grade?: string) => {
    switch (grade) {
      case 'A':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'B':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
      case 'C':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400';
    }
  };
  
  // Format date
  const formatDate = (dateStr?: string | null) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString();
  };
  
  // Format quantity
  const formatQuantity = (kg?: number | null) => {
    if (!kg) return '—';
    return `${kg.toLocaleString()} kg`;
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }
  
  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">
            {t('harvest.title')}
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {harvests.length} {t('harvest.count', { count: harvests.length })}
          </p>
        </div>
        <Link
          to={`/farms/${farmId}/harvest/new`}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          {t('harvest.newBatch')}
        </Link>
      </div>
      
      {/* Harvests List */}
      {harvests.length === 0 ? (
        <div className="text-center py-12">
          <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2zM10 8.5a.5.5 0 11-1 0 .5.5 0 011 0zm5 5a.5.5 0 11-1 0 .5.5 0 011 0z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {t('harvest.empty.title')}
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            {t('harvest.empty.description')}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {harvests.map((harvest) => (
            <Link
              key={harvest.id}
              to={`/farms/${farmId}/harvest/${harvest.id}`}
              className="block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-green-500 dark:hover:border-green-500 transition-colors"
            >
              <div className="p-4">
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {harvest.crop_name}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {harvest.field_name}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {harvest.quality_grade && (
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getGradeColor(harvest.quality_grade)}`}>
                        Grade {harvest.quality_grade}
                      </span>
                    )}
                    {harvest.status && (
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getStatusColor(harvest.status)}`}>
                        {t(`harvest.status.${harvest.status.toLowerCase()}`)}
                      </span>
                    )}
                  </div>
                </div>
                
                {/* Details Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500 dark:text-gray-400">{t('harvest.date')}</p>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {formatDate(harvest.harvest_date)}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500 dark:text-gray-400">{t('harvest.quantity')}</p>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {formatQuantity(harvest.quantity_kg)}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500 dark:text-gray-400">{t('harvest.price')}</p>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {harvest.price_per_kg ? `$${harvest.price_per_kg}/kg` : '—'}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500 dark:text-gray-400">{t('harvest.value')}</p>
                    <p className="font-semibold text-green-600 dark:text-green-400">
                      {harvest.price_per_kg && harvest.quantity_kg
                        ? `$${(harvest.price_per_kg * harvest.quantity_kg).toLocaleString()}`
                        : '—'}
                    </p>
                  </div>
                </div>
                
                {/* Notes */}
                {harvest.notes && (
                  <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                    <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
                      {harvest.notes}
                    </p>
                  </div>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default HarvestListPage;
