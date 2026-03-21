import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ROUTES } from './routes';

// Auth Components
import LoginForm from '@features/auth/components/LoginForm';
import RegisterForm from '@features/auth/components/RegisterForm';

// Farmer Components
import FarmerDashboard from '@/pages/roles/farmer/FarmerDashboard';
import FarmList from '@features/farms/components/FarmList';
import FarmSettingsPage from '@/pages/roles/farmer/FarmSettingsPage';
import FieldsPage from '@/pages/roles/farmer/FieldsPage';
import FieldDetailsPage from '@/pages/roles/farmer/FieldDetailsPage';
import InventoryPage from '@/pages/roles/farmer/InventoryPage';
import StockUpdateForm from '@features/inventory/components/StockUpdateForm';
import FarmerOrderPage from '@/pages/roles/farmer/FarmerOrderPage';
import AIDiagnosticsPage from '@/pages/roles/farmer/AIDiagnosticsPage';
import DailyLogForm from '@features/logs/components/DailyLogForm';





// Placeholder for other roles
const Placeholder = ({ name }: { name: string }) => (
  <div className="p-8 text-center text-gray-500">
    <h2 className="text-xl font-bold mb-2">{name}</h2>
    <p>This page is currently under development.</p>
  </div>
);

const AppRouter: React.FC = () => {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route path={ROUTES.LOGIN} element={<LoginForm />} />
      <Route path={ROUTES.REGISTER} element={<RegisterForm />} />
      
      {/* Farmer Routes */}
      <Route path={ROUTES.FARMER_DASHBOARD} element={<FarmerDashboard />} />
      <Route path={ROUTES.FARMER_FARMS} element={<FarmList />} />
      <Route path={ROUTES.FARMER_FARM_SETTINGS} element={<FarmSettingsPage />} />
      <Route path={ROUTES.FARMER_FIELDS} element={<FieldsPage />} />
      <Route path={ROUTES.FARMER_FIELD_DETAIL} element={<FieldDetailsPage />} />
      <Route path={ROUTES.FARMER_HARVEST_NEW} element={<StockUpdateForm />} />
      <Route path={ROUTES.FARMER_INVENTORY} element={<InventoryPage />} />
      <Route path={ROUTES.FARMER_ORDERS} element={<FarmerOrderPage />} />
      <Route path={ROUTES.FARMER_AI_DIAGNOSIS} element={<AIDiagnosticsPage />} />
      <Route path={ROUTES.FARMER_LOGS_NEW} element={<DailyLogForm />} />
      
      {/* Merchant Routes (Placeholders) */}
      <Route path={ROUTES.MERCHANT_MARKETPLACE} element={<Placeholder name="Merchant Marketplace" />} />
      <Route path={ROUTES.MERCHANT_DASHBOARD} element={<Placeholder name="Merchant Dashboard" />} />
      
      {/* Delivery Routes (Placeholders) */}
      <Route path={ROUTES.DELIVERY_AVAILABLE} element={<Placeholder name="Delivery Job Discovery" />} />
      
      {/* Landing/Default Redirect */}
      <Route path="/" element={<Navigate to={ROUTES.LOGIN} replace />} />
      
      {/* 404 Fallback */}
      <Route path="*" element={<div className="p-8 text-center text-red-500 font-bold underline">404: Page Not Found</div>} />
    </Routes>
  );
};

export default AppRouter;
