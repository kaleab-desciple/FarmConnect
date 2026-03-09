/**
 * Crop Cycles List Page
 * FarmConnect - AgriManagement
 * 
 * Displays all crop cycles for a field with status tracking
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { farmsAPI, CropCycle } from '../services/farms-api';
import { Spinner } from '../../../shared/components/ui/Spinner';

/**
 * Crop Cycle with display helpers
 */
interface CropCycleDisplay extends CropCycle {
  statusLabel?: string;
  daysUntilHarvest?: number;
  progressPercent?: number;
}

/**
 * Crop Cycles List Page Component
 */
export const CropCyclesListPage: React.FC = () => {
  const { t } = useTranslation();
  const { farmId, fieldId } = useParams<{ farmId: string; fieldId: string }>();
  
  const [cycles, setCycles] = useState<CropCycleDisplay[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Load crop cycles
  useEffect(() => {
    if (fieldId) {
      loadCropCycles();
    }
  }, [fieldId]);
  
  const loadCropCycles = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await farmsAPI.listCropCycles(fieldId!);
      
      // Enrich with calculated fields
      const enriched = response.map(cycle => {
        const statusLabel = t(`crops.status.${cycle.status?.toLowerCase() || 'unknown'}`);
        
        // Calculate days until harvest
        let daysUntilHarvest: number | undefined;
        if (cycle.expected_harvest_date) {
          const harvestDate = new Date(cycle.expected_harvest_date);
          const today = new Date();
          daysUntilHarvest = Math.ceil((harvestDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
        }
        
        // Calculate progress based on status
        let progressPercent: number | undefined;
        switch (cycle.status) {
          case 'PLANNED':
            progressPercent = 0;
            break;
          case 'PLANTED':
            progressPercent = 10;
            break;
          case 'GROWING':
            progressPercent = 50;
            break;
          case 'HARVESTED':
            progressPercent = 100;
            break;
          default:
            progressPercent = undefined;
        }
        
        return {
          ...cycle,
          statusLabel,
          daysUntilHarvest,
          progressPercent,
        };
      });
      
      setCycles(enriched);
    } catch (err: any) {
      setError(err.response?.data?.detail || t('crops.errors.loadFailed'));
    } finally {
      setLoading(false);
    }
  };
  
  // Get status badge color
  const getStatusColor = (status?: string) => {
    switch (status?.toUpperCase()) {
      case 'PLANNED':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400';
      case 'PLANTED':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
      case 'GROWING':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'HARVESTED':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400';
      case 'PARTIALLY_HARVESTED':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'FAILED':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400';
    }
  };
  
  // Format date
  const formatDate = (dateStr?: string | null) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString();
  };
  
  // Get yield display
  const getYieldDisplay = (expected?: number | null, actual?: number | null) => {
    if (!expected && !actual) return '—';
    const exp = expected ? `${expected.toLocaleString()} kg` : '';
    const act = actual ? ` / ${actual.toLocaleString()} kg` : '';
    return exp + act;
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-4">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">{error}</p>
          <button
            onClick={loadCropCycles}
            className="mt-2 text-sm text-red-600 dark:text-red-400 hover:underline"
          >
            {t('common.retry')}
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">
            {t('crops.title')}
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {cycles.length} {t('crops.count', { count: cycles.length })}
          </p>
        </div>
        <Link
          to={`/farms/${farmId}/fields/${fieldId}/crops/new`}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          {t('crops.addCycle')}
        </Link>
      </div>
      
      {/* Crop Cycles List */}
      {cycles.length === 0 ? (
        <div className="text-center py-12">
          <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {t('crops.empty.title')}
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            {t('crops.empty.description')}
          </p>
          <Link
            to={`/farms/${farmId}/fields/${fieldId}/crops/new`}
            className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            {t('crops.addFirstCycle')}
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {cycles.map((cycle) => (
            <Link
              key={cycle.id}
              to={`/farms/${farmId}/fields/${fieldId}/crops/${cycle.id}`}
              className="block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-green-500 dark:hover:border-green-500 transition-colors"
            >
              <div className="p-4">
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {cycle.crop_name}
                    </h3>
                    {cycle.variety && (
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {cycle.variety}
                      </p>
                    )}
                  </div>
                  {cycle.status && (
                    <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getStatusColor(cycle.status)}`}>
                      {cycle.statusLabel}
                    </span>
                  )}
                </div>
                
                {/* Progress Bar (for active cycles) */}
                {cycle.progressPercent !== undefined && cycle.status !== 'HARVESTED' && (
                  <div className="mb-3">
                    <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-green-500 rounded-full transition-all duration-300"
                        style={{ width: `${cycle.progressPercent}%` }}
                      />
                    </div>
                  </div>
                )}
                
                {/* Info Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500 dark:text-gray-400">{t('crops.plantingDate')}</p>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {formatDate(cycle.planting_date)}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500 dark:text-gray-400">{t('crops.expectedHarvest')}</p>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {formatDate(cycle.expected_harvest_date)}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500 dark:text-gray-400">{t('crops.yield')}</p>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {getYieldDisplay(cycle.expected_yield_kg, cycle.actual_yield_kg)}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500 dark:text-gray-400">{t('crops.daysLeft')}</p>
                    <p className={`font-medium ${
                      cycle.daysUntilHarvest !== undefined && cycle.daysUntilHarvest < 0
                        ? 'text-red-600 dark:text-red-400'
                        : cycle.daysUntilHarvest !== undefined && cycle.daysUntilHarvest <= 7
                        ? 'text-yellow-600 dark:text-yellow-400'
                        : 'text-gray-900 dark:text-white'
                    }`}>
                      {cycle.daysUntilHarvest !== undefined 
                        ? cycle.daysUntilHarvest >= 0 
                          ? `${cycle.daysUntilHarvest} ${t('crops.days')}`
                          : t('crops.overdue')
                        : '—'
                      }
                    </p>
                  </div>
                </div>
                
                {/* Quality Grade (if harvested) */}
                {cycle.yield_quality_grade && (
                  <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {t('crops.qualityGrade')}:
                      </span>
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                        cycle.yield_quality_grade === 'A'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                          : cycle.yield_quality_grade === 'B'
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                      }`}>
                        Grade {cycle.yield_quality_grade}
                      </span>
                    </div>
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

export default CropCyclesListPage;
