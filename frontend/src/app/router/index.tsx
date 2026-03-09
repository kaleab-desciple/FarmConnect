import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { UserRole } from '../config/roles';
import { Spinner } from '../../shared/components/ui/Spinner';
import { AuthGuard } from './guards';
import { useMemo } from 'react';

// Lazy load pages for code splitting
const LoginPage = lazy(() => import('../../features/auth/pages/LoginPage'));

// Farmer pages
const FarmerDashboard = lazy(() => import('../../features/farms/pages/FarmerDashboard'));
const FieldsListPage = lazy(() => import('../../features/farms/pages/FieldsListPage'));
const CropCyclesListPage = lazy(() => import('../../features/farms/pages/CropCyclesListPage'));

// Harvest pages
const HarvestListPage = lazy(() => import('../../features/harvest/pages/HarvestListPage'));

// Orders pages
const OrdersListPage = lazy(() => import('../../features/orders/pages/OrdersListPage'));

// Admin pages
const AdminDashboard = lazy(() => import('../../features/admin/pages/AdminDashboard'));

// Loading fallback
const PageLoader = () => (
  <div className="flex min-h-screen items-center justify-center">
    <Spinner size="lg" />
  </div>
);

// Route definitions
interface RouteConfig {
  path: string;
  component: ReturnType<typeof lazy>;
  roles?: UserRole[];
  requiresAuth?: boolean;
}

const routes: RouteConfig[] = [
  // Public routes
  { path: '/', component: LoginPage },
  { path: '/login', component: LoginPage },
  
  // Farmer routes
  { 
    path: '/farmer', 
    component: FarmerDashboard, 
    roles: [UserRole.FARMER],
    requiresAuth: true 
  },
  { 
    path: '/farmer/fields', 
    component: FieldsListPage, 
    roles: [UserRole.FARMER],
    requiresAuth: true 
  },
  { 
    path: '/farmer/crop-cycles', 
    component: CropCyclesListPage, 
    roles: [UserRole.FARMER],
    requiresAuth: true 
  },
  { 
    path: '/farmer/harvests', 
    component: HarvestListPage, 
    roles: [UserRole.FARMER],
    requiresAuth: true 
  },
  
  // Merchant routes
  { 
    path: '/merchant/orders', 
    component: OrdersListPage, 
    roles: [UserRole.MERCHANT],
    requiresAuth: true 
  },
  
  // Admin routes
  { 
    path: '/admin', 
    component: AdminDashboard, 
    roles: [UserRole.ADMIN],
    requiresAuth: true 
  },
  
  // Default redirect
  { path: '*', component: LoginPage },
];

export function Router() {
  const location = useLocation();
  const { isAuthenticated, user } = useAuthStore();
  
  // Filter routes based on auth and permissions
  const filteredRoutes = useMemo(() => {
    return routes.map((route) => {
      // Check auth requirement
      if (route.requiresAuth && !isAuthenticated) {
        return { ...route, component: () => <Navigate to="/login" state={{ from: location }} replace /> };
      }
      
      // Check role requirement
      if (route.roles && user) {
        if (!route.roles.includes(user.role)) {
          return { ...route, component: () => <Navigate to="/login" replace /> };
        }
      }
      
      return route;
    });
  }, [isAuthenticated, user, location]);
  
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {filteredRoutes.map((route, index) => (
          <Route
            key={route.path + index}
            path={route.path}
            element={
              <AuthGuard
                requireAuth={route.requiresAuth ?? false}
                allowedRoles={route.roles}
                fallbackPath={route.requiresAuth === false ? undefined : '/login'}
              >
                <route.component />
              </AuthGuard>
            }
          />
        ))}
      </Routes>
    </Suspense>
  );
}

export default Router;
