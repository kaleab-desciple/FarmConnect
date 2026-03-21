import axios, { AxiosInstance } from 'axios';
import { mapFarm, mapField, mapCropCycle, mapPaginated } from '@/shared/utils/mappers';
import type {
  // User types
  User, UserCreate, UserUpdate, UserListResponse,
  // Farm types
  Farm, FarmCreate, FarmUpdate, FarmListResponse,
  Field, FieldCreate, FieldUpdate,
  CropCycle, CropCycleCreate, CropCycleUpdate,
  FieldStatusMapResponse,
  // Product types
  Product, ProductCreate, ProductUpdate, ProductListResponse,
  // Order types
  Order, OrderCreate, OrderUpdate, OrderListResponse,
  // Escrow types
  Escrow, EscrowCreate,
  // Delivery types
  Delivery, DeliveryCreate, DeliveryUpdate,
  // Dispute types
  Dispute, DisputeCreate, DisputeUpdate,
  // Weather types
  WeatherForecast, WeatherForecastCreate,
  WeatherSnapshot, WeatherSnapshotCreate,
  Alert, AlertCreate, AlertUpdate, AlertListResponse,
  FieldRiskScore, FieldRiskScoreCreate,
  // Monitoring types
  SoilReading, SoilReadingCreate, SoilReadingUpdate,
  NDVISnapshot, NDVISnapshotCreate,
  PestDiseaseReport, PestDiseaseReportCreate,
  TreatmentRecommendation, TreatmentRecommendationCreate,
  // Harvest types
  HarvestEvent, HarvestEventCreate, HarvestEventUpdate,
  HarvestBatch, HarvestBatchCreate,
  // AI types
  DiagnosisSession, DiagnosisSessionCreate, DiagnosisSessionUpdate,
  // Accounting types
  Account, AccountCreate, AccountBalance,
  JournalEntry, JournalEntryCreate,
  // Pagination
  PaginationParams,
  // Common responses
  ApiResponse, PaginatedResponse, DeleteResponse,
} from '@shared/index';

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============ Auth API ============
export const authApi = {
  login: (credentials: { email: string; password: string }) => 
    api.post<{
      access_token: string;
      refresh_token: string;
      user: User;
    }>('/api/v1/auth/login', credentials),
  
  verify: (token: string) => 
    api.post('/api/v1/auth/verify', null, { params: { token } }),
};

// ============ User API ============
export const userApi = {
  getAll: (params?: PaginationParams) => 
    api.get<PaginatedResponse<User>>('/api/v1/users', { params }),
  
  getById: (id: string) => 
    api.get<User>(`/api/v1/users/${id}`),
  
  create: (data: UserCreate) => 
    api.post<User>('/api/v1/users', data),
  
  update: (id: string, data: Partial<UserUpdate>) => 
    api.patch<User>(`/api/v1/users/${id}`, data),
  
  delete: (id: string) => 
    api.delete<DeleteResponse>(`/api/v1/users/${id}`),
};

// ============ Farm API ============
export const farmApi = {
  getAll: (params?: PaginationParams) => 
    api.get<PaginatedResponse<Farm>>('/api/v1/agri/farms', { params })
      .then(res => ({ ...res, data: mapPaginated(res.data, mapFarm) })),
  
  getById: (id: string) => 
    api.get<Farm>(`/api/v1/agri/farms/${id}`)
      .then(res => ({ ...res, data: mapFarm(res.data) })),
  
  create: (data: FarmCreate) => 
    api.post<Farm>('/api/v1/agri/farms', data)
      .then(res => ({ ...res, data: mapFarm(res.data) })),
  
  update: (id: string, data: Partial<FarmUpdate>) => 
    api.patch<Farm>(`/api/v1/agri/farms/${id}`, data)
      .then(res => ({ ...res, data: mapFarm(res.data) })),
  
  delete: (id: string) => 
    api.delete<DeleteResponse>(`/api/v1/agri/farms/${id}`),
  
  // Field status map endpoint
  getFieldStatusMap: (farmId: string) => 
    api.get<FieldStatusMapResponse>(`/api/v1/agri/farms/${farmId}/field-status-map`),
};

// ============ Field API ============
export const fieldApi = {
  getByFarmId: (farmId: string, params?: PaginationParams) => 
    api.get<PaginatedResponse<Field>>(`/api/v1/agri/fields`, { params: { ...params, farm_id: farmId } })
      .then(res => ({ ...res, data: mapPaginated(res.data, mapField) })),
  
  getById: (id: string) => 
    api.get<Field>(`/api/v1/agri/fields/${id}`)
      .then(res => ({ ...res, data: mapField(res.data) })),
  
  create: (data: FieldCreate) => 
    api.post<Field>(`/api/v1/agri/fields`, data)
      .then(res => ({ ...res, data: mapField(res.data) })),
  
  update: (id: string, data: Partial<FieldUpdate>) => 
    api.patch<Field>(`/api/v1/agri/fields/${id}`, data)
      .then(res => ({ ...res, data: mapField(res.data) })),
  
  delete: (id: string) => 
    api.delete<DeleteResponse>(`/api/v1/agri/fields/${id}`),
};

// ============ Crop Cycle API ============
export const cropCycleApi = {
  getByFieldId: (fieldId: string, params?: PaginationParams) => 
    api.get<PaginatedResponse<CropCycle>>(`/api/v1/agri/crop-cycles`, { params: { ...params, field_id: fieldId } })
      .then(res => ({ ...res, data: mapPaginated(res.data, mapCropCycle) })),
  
  getById: (id: string) => 
    api.get<CropCycle>(`/api/v1/agri/crop-cycles/${id}`)
      .then(res => ({ ...res, data: mapCropCycle(res.data) })),
  
  create: (data: CropCycleCreate) => 
    api.post<CropCycle>(`/api/v1/agri/crop-cycles`, data)
      .then(res => ({ ...res, data: mapCropCycle(res.data) })),
  
  update: (id: string, data: Partial<CropCycleUpdate>) => 
    api.patch<CropCycle>(`/api/v1/agri/crop-cycles/${id}`, data)
      .then(res => ({ ...res, data: mapCropCycle(res.data) })),
  
  delete: (id: string) => 
    api.delete<DeleteResponse>(`/api/v1/agri/crop-cycles/${id}`),
};

// ============ Product API ============
export const productApi = {
  getAll: (params?: PaginationParams) => 
    api.get<PaginatedResponse<Product>>('/api/v1/products', { params }),
  
  getById: (id: string) => 
    api.get<Product>(`/api/v1/products/${id}`),
  
  create: (data: ProductCreate) => 
    api.post<Product>('/api/v1/products', data),
  
  update: (id: string, data: Partial<ProductUpdate>) => 
    api.patch<Product>(`/api/v1/products/${id}`, data),
  
  delete: (id: string) => 
    api.delete<DeleteResponse>(`/api/v1/products/${id}`),
};

// ============ Order API ============
export const orderApi = {
  getAll: (params?: PaginationParams) => 
    api.get<PaginatedResponse<Order>>('/api/v1/orders', { params }),
  
  getById: (id: string) => 
    api.get<Order>(`/api/v1/orders/${id}`),
  
  create: (data: OrderCreate) => 
    api.post<Order>('/api/v1/orders', data),
  
  update: (id: string, data: Partial<OrderUpdate>) => 
    api.patch<Order>(`/api/v1/orders/${id}`, data),
  
  cancel: (id: string, reason: string) => 
    api.post<Order>(`/api/v1/orders/${id}/cancel`, { reason }),
};

// ============ Escrow API ============
export const escrowApi = {
  getByOrderId: (orderId: string) => 
    api.get<Escrow>(`/api/v1/orders/${orderId}/escrow`),
  
  create: (data: EscrowCreate) => 
    api.post<Escrow>('/api/v1/escrow', data),
  
  fund: (escrowId: string, data: { payment_reference: string }) => 
    api.post<Escrow>(`/api/v1/escrow/${escrowId}/fund`, data),
  
  release: (escrowId: string) => 
    api.post<Escrow>(`/api/v1/escrow/${escrowId}/release`),
  
  refund: (escrowId: string, reason: string) => 
    api.post<Escrow>(`/api/v1/escrow/${escrowId}/refund`, { reason }),
};

// ============ Delivery API ============
export const deliveryApi = {
  getByOrderId: (orderId: string) => 
    api.get<Delivery>(`/api/v1/orders/${orderId}/delivery`),
  
  create: (data: DeliveryCreate) => 
    api.post<Delivery>('/api/v1/delivery', data),
  
  update: (id: string, data: Partial<DeliveryUpdate>) => 
    api.patch<Delivery>(`/api/v1/delivery/${id}`, data),
  
  updateStatus: (id: string, status: string, notes?: string) => 
    api.patch<Delivery>(`/api/v1/delivery/${id}/status`, { status, notes }),
};

// ============ Dispute API ============
export const disputeApi = {
  getAll: (params?: PaginationParams) => 
    api.get<PaginatedResponse<Dispute>>('/api/v1/disputes', { params }),
  
  getById: (id: string) => 
    api.get<Dispute>(`/api/v1/disputes/${id}`),
  
  create: (data: DisputeCreate) => 
    api.post<Dispute>('/api/v1/disputes', data),
  
  update: (id: string, data: Partial<DisputeUpdate>) => 
    api.patch<Dispute>(`/api/v1/disputes/${id}`, data),
  
  resolve: (id: string, resolution: string, notes: string) => 
    api.post<Dispute>(`/api/v1/disputes/${id}/resolve`, { resolution, notes }),
  
  escalate: (id: string, escalatedTo: string, note: string) => 
    api.post<Dispute>(`/api/v1/disputes/${id}/escalate`, { escalated_to: escalatedTo, escalation_note: note }),
};

// ============ Weather API ============
export const weatherApi = {
  getForecast: (fieldId: string, params?: { days?: number }) => 
    api.get<WeatherForecast[]>(`/api/v1/agri/fields/${fieldId}/forecast`, { params }),
  
  getSnapshot: (fieldId: string) => 
    api.get<WeatherSnapshot>(`/api/v1/agri/fields/${fieldId}/current`),
  
  createForecast: (data: WeatherForecastCreate) => 
    api.post<WeatherForecast>('/api/v1/weather/forecast', data),
  
  createSnapshot: (data: WeatherSnapshotCreate) => 
    api.post<WeatherSnapshot>('/api/v1/weather/snapshot', data),
};

// ============ Alert API ============
export const alertApi = {
  getAll: (params?: PaginationParams & { acknowledged?: boolean }) => 
    api.get<AlertListResponse>('/api/v1/alerts', { params }),
  
  getById: (id: string) => 
    api.get<Alert>(`/api/v1/alerts/${id}`),
  
  create: (data: AlertCreate) => 
    api.post<Alert>('/api/v1/alerts', data),
  
  update: (id: string, data: Partial<AlertUpdate>) => 
    api.patch<Alert>(`/api/v1/alerts/${id}`, data),
  
  acknowledge: (id: string) => 
    api.post<Alert>(`/api/v1/alerts/${id}/acknowledge`),
};

// ============ Monitoring API ============
export const monitoringApi = {
  // Soil readings
  getSoilReadings: (fieldId: string) => 
    api.get<SoilReading[]>(`/api/v1/agri/soil-readings`, { params: { field_id: fieldId } }),
  
  createSoilReading: (data: SoilReadingCreate) => 
    api.post<SoilReading>('/api/v1/agri/soil-readings', null, { params: data }),
  
  // NDVI snapshots
  getNDVISnapshots: (fieldId: string) => 
    api.get<NDVISnapshot[]>(`/api/v1/agri/ndvi-snapshots`, { params: { field_id: fieldId } }),
  
  createNDVISnapshot: (data: NDVISnapshotCreate) => 
    api.post<NDVISnapshot>('/api/v1/agri/ndvi-snapshots', null, { params: data }),
  
  // Pest/Disease reports
  getPestReports: (fieldId: string) => 
    api.get<PestDiseaseReport[]>(`/api/v1/agri/pest-reports`, { params: { field_id: fieldId } }),
  
  createPestReport: (fieldId: string, data: PestDiseaseReportCreate) => 
    api.post<PestDiseaseReport>('/api/v1/agri/pest-reports', null, { params: { ...data, field_id: fieldId } }),
  
  // Treatment recommendations
  getRecommendations: (reportId: string) => 
    api.get<TreatmentRecommendation[]>(`/api/v1/agri/treatment-recommendations`, { params: { report_id: reportId } }),
  
  createRecommendation: (data: TreatmentRecommendationCreate) => 
    api.post<TreatmentRecommendation>('/api/v1/agri/treatment-recommendations', null, { params: data }),
};

// ============ Harvest API ============
export const harvestApi = {
  getEvents: (params?: PaginationParams) => 
    api.get<PaginatedResponse<HarvestEvent>>('/api/v1/agri/harvests/statistics', { params }), // Using stats as a proxy or need specific GET if added
  
  getEventById: (id: string) => 
    api.get<HarvestEvent>(`/api/v1/harvest/events/${id}`),
  
  createEvent: (data: HarvestEventCreate) => 
    api.post<HarvestEvent>('/api/v1/agri/harvests/', data),
  
  updateEvent: (id: string, data: Partial<HarvestEventUpdate>) => 
    api.patch<HarvestEvent>(`/api/v1/harvest/events/${id}`, data),
  
  // Batch operations
  getBatches: (params?: PaginationParams) => 
    api.get<PaginatedResponse<HarvestBatch>>('/api/v1/harvest/batches', { params }),
  
  getBatchById: (id: string) => 
    api.get<HarvestBatch>(`/api/v1/harvest/batches/${id}`),
  
  createBatch: (data: HarvestBatchCreate) => 
    api.post<HarvestBatch>('/api/v1/harvest/batches', data),
  
  sealBatch: (id: string, sealedBy: string, evidence?: Record<string, unknown>) => 
    api.post<HarvestBatch>(`/api/v1/harvest/batches/${id}/seal`, { sealed_by: sealedBy, seal_evidence: evidence }),
};

// ============ AI Diagnosis API ============
export const aiApi = {
  createSession: (data: DiagnosisSessionCreate) => 
    api.post<DiagnosisSession>('/api/v1/agri/ai/diagnose', data),
  
  getSession: (id: string) => 
    api.get<DiagnosisSession>(`/api/v1/agri/ai/diagnosis/${id}`),
  
  updateSession: (id: string, data: Partial<DiagnosisSessionUpdate>) => 
    api.patch<DiagnosisSession>(`/api/v1/ai/diagnosis/${id}`, data),
  
  getByField: (fieldId: string) => 
    api.get<DiagnosisSession[]>(`/api/v1/ai/fields/${fieldId}/diagnoses`),
};

// ============ Accounting API ============
export const accountingApi = {
  getAccounts: (ownerId: string) => 
    api.get<Account[]>(`/api/v1/accounting/accounts`, { params: { owner_id: ownerId } }),
  
  getBalance: (accountId: string) => 
    api.get<AccountBalance>(`/api/v1/accounting/accounts/${accountId}/balance`),
  
  getJournalEntries: (params?: { reference_type?: string; reference_id?: string }) => 
    api.get<JournalEntry[]>('/api/v1/accounting/journal', { params }),
  
  createJournalEntry: (data: JournalEntryCreate) => 
    api.post<JournalEntry>('/api/v1/accounting/journal', data),
};

// Re-export the base axios instance for custom requests
export { api };

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized - could redirect to login
      console.error('Unauthorized - please login');
    } else if (error.response?.status === 403) {
      console.error('Forbidden - insufficient permissions');
    } else if (error.response?.status === 404) {
      console.error('Resource not found');
    }
    return Promise.reject(error);
  }
);

export default api;
