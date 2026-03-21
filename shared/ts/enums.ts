// FarmConnect TypeScript Enums - Mirroring Python DTOs from shared_models
// These enums are used across the platform for type safety

// ============ User & Authentication Enums ============
export enum UserRole {
  FARMER = "FARMER",
  MERCHANT = "MERCHANT",
  DELIVERY = "DELIVERY",
  AGENT = "AGENT",
  MANAGER = "MANAGER",
  ADMIN = "ADMIN",
  MODERATOR = "MODERATOR",
  AGRONOMIST = "AGRONOMIST",
  FIELD_ANALYST = "FIELD_ANALYST",
}

export enum OnboardingStatus {
  PENDING_REVIEW = "PENDING_REVIEW",
  ACTIVE = "ACTIVE",
  REJECTED = "REJECTED",
}

// ============ Order & Payment Enums ============
export enum OrderStatus {
  CREATED = "CREATED",
  PENDING_PAYMENT = "PENDING_PAYMENT",
  FUNDED = "FUNDED",
  CONFIRMED = "CONFIRMED",
  IN_DELIVERY = "IN_DELIVERY",
  DELIVERED = "DELIVERED",
  DELIVERY_FAILED = "DELIVERY_FAILED",
  RETURNED = "RETURNED",
  COMPLETED = "COMPLETED",
  CANCELLED = "CANCELLED",
  EXPIRED = "EXPIRED",
}

export enum EscrowState {
  CREATED = "CREATED",
  FUNDED = "FUNDED",
  RELEASED = "RELEASED",
  DISPUTED = "DISPUTED",
  REFUNDED = "REFUNDED",
  SETTLED = "SETTLED",
  REVERSED = "REVERSED",
}

export enum DisputeState {
  OPEN = "OPEN",
  UNDER_REVIEW = "UNDER_REVIEW",
  ESCALATED_TO_AGENT = "ESCALATED_TO_AGENT",
  ESCALATED_TO_MANAGER = "ESCALATED_TO_MANAGER",
  RESOLVED = "RESOLVED",
  REOPENED = "REOPENED",
}

export enum DisputeResolution {
  RELEASE = "RELEASE",
  PARTIAL_RELEASE = "PARTIAL_RELEASE",
  REFUND = "REFUND",
}

export enum Provider {
  BANK = "BANK",
  WALLET = "WALLET",
}

// ============ Product & Inventory Enums ============
export enum Category {
  GRAINS = "GRAINS",
  VEGETABLES = "VEGETABLES",
  FRUITS = "FRUITS",
  DAIRY = "DAIRY",
  MEAT = "MEAT",
  SPICES = "SPICES",
  OTHER = "OTHER",
}

export enum Unit {
  KG = "KG",
  GRAM = "GRAM",
  TON = "TON",
  LITER = "LITER",
  PIECE = "PIECE",
  CRATE = "CRATE",
  BAG = "BAG",
}

export enum QualityGrade {
  GRADE_A = "GRADE_A",
  GRADE_B = "GRADE_B",
  GRADE_C = "GRADE_C",
  PREMIUM = "PREMIUM",
  STANDARD = "STANDARD",
  A = "A",
  B = "B",
  C = "C",
}

export enum ProductStatus {
  AVAILABLE = "AVAILABLE",
  LOW_STOCK = "LOW_STOCK",
  SOLD_OUT = "SOLD_OUT",
  EXPIRED = "EXPIRED",
  DISCONTINUED = "DISCONTINUED",
}

// ============ Delivery Enums ============
export enum DeliveryStatus {
  ASSIGNED = "ASSIGNED",
  PICKED_UP = "PICKED_UP",
  IN_TRANSIT = "IN_TRANSIT",
  DELIVERED = "DELIVERED",
  FAILED = "FAILED",
  CANCELLED = "CANCELLED",
}

// ============ Farm & Field Enums ============
export enum CropCycleStatus {
  PLANNED = "PLANNED",
  PLANTED = "PLANTED",
  GROWING = "GROWING",
  HARVESTED = "HARVESTED",
  PARTIALLY_HARVESTED = "PARTIALLY_HARVESTED",
  FAILED = "FAILED",
  ABANDONED = "ABANDONED",
}

// ============ Monitoring Enums ============
export enum NDVISource {
  SENTINEL_2 = "SENTINEL_2",
  LANDSAT_8 = "LANDSAT_8",
  LANDSAT_9 = "LANDSAT_9",
  MODIS = "MODIS",
  MANUAL = "MANUAL",
}

export enum StressLevel {
  NONE = "NONE",
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export enum SoilReadingSource {
  IOT_SENSOR = "IOT_SENSOR",
  MANUAL_TEST = "MANUAL_TEST",
  LAB_ANALYSIS = "LAB_ANALYSIS",
  ESTIMATED = "ESTIMATED",
}

export enum SeverityLevel {
  TRACE = "TRACE",
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  SEVERE = "SEVERE",
}

export enum RecommendationSource {
  AGRONOMIST = "AGRONOMIST",
  SYSTEM = "SYSTEM",
  AI_MODEL = "AI_MODEL",
  COMMUNITY = "COMMUNITY",
}

// ============ Task Enums ============
export enum TaskType {
  LAND_PREPARATION = "LAND_PREPARATION",
  SOWING = "SOWING",
  PLANTING = "PLANTING",
  IRRIGATION = "IRRIGATION",
  FERTILIZATION = "FERTILIZATION",
  WEEDING = "WEEDING",
  PEST_CONTROL = "PEST_CONTROL",
  DISEASE_CONTROL = "DISEASE_CONTROL",
  PRUNING = "PRUNING",
  THINNING = "THINNING",
  HARVESTING = "HARVESTING",
  POST_HARVEST = "POST_HARVEST",
  INSPECTION = "INSPECTION",
  MAINTENANCE = "MAINTENANCE",
  OTHER = "OTHER",
}

export enum TaskStatus {
  PENDING = "PENDING",
  SCHEDULED = "SCHEDULED",
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETED = "COMPLETED",
  SKIPPED = "SKIPPED",
  CANCELLED = "CANCELLED",
  OVERDUE = "OVERDUE",
}

export enum TaskPriority {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  URGENT = "URGENT",
}

// ============ Weather Enums ============
export enum WeatherSource {
  NOAA_GFS = "NOAA_GFS",
  NOAA_HRRR = "NOAA_HRRR",
  OPEN_METEO = "OPEN_METEO",
  LOCAL_STATION = "LOCAL_STATION",
  MANUAL = "MANUAL",
}

export enum RiskType {
  FROST = "FROST",
  FREEZE = "FREEZE",
  HEAT_STRESS = "HEAT_STRESS",
  DROUGHT = "DROUGHT",
  HEAVY_RAIN = "HEAVY_RAIN",
  FLOOD = "FLOOD",
  HAIL = "HAIL",
  STRONG_WIND = "STRONG_WIND",
  STORM = "STORM",
  HURRICANE = "HURRICANE",
  TORNADO = "TORNADO",
  WILDFIRE = "WILDFIRE",
  PEST_OUTBREAK = "PEST_OUTBREAK",
  DISEASE_OUTBREAK = "DISEASE_OUTBREAK",
}

export enum RiskLevel {
  MINIMAL = "MINIMAL",
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export enum AlertType {
  WEATHER_WARNING = "WEATHER_WARNING",
  FROST_ALERT = "FROST_ALERT",
  DROUGHT_ALERT = "DROUGHT_ALERT",
  PEST_DETECTED = "PEST_DETECTED",
  DISEASE_DETECTED = "DISEASE_DETECTED",
  NDVI_ANOMALY = "NDVI_ANOMALY",
  SOIL_MOISTURE_LOW = "SOIL_MOISTURE_LOW",
  SOIL_MOISTURE_HIGH = "SOIL_MOISTURE_HIGH",
  TASK_OVERDUE = "TASK_OVERDUE",
  HARVEST_READY = "HARVEST_READY",
  LOAN_RISK = "LOAN_RISK",
  PAYMENT_DUE = "PAYMENT_DUE",
  ESCROW_HOLD = "ESCROW_HOLD",
  PRICE_ALERT = "PRICE_ALERT",
  SYSTEM_NOTIFICATION = "SYSTEM_NOTIFICATION",
}

export enum AlertSeverity {
  INFO = "INFO",
  WARNING = "WARNING",
  CRITICAL = "CRITICAL",
  EMERGENCY = "EMERGENCY",
}

// ============ Advisory Enums ============
export enum AdvisoryStatus {
  REQUESTED = "REQUESTED",
  SCHEDULED = "SCHEDULED",
  OPEN = "OPEN",
  IN_PROGRESS = "IN_PROGRESS",
  RESOLVED = "RESOLVED",
  CLOSED = "CLOSED",
  CANCELLED = "CANCELLED",
}

export enum MessageType {
  TEXT = "TEXT",
  IMAGE = "IMAGE",
  DOCUMENT = "DOCUMENT",
  VOICE = "VOICE",
  VIDEO = "VIDEO",
  LOCATION = "LOCATION",
  SYSTEM = "SYSTEM",
}

// ============ Harvest & QC Enums ============
export enum QCGrade {
  GRADE_A = "GRADE_A",
  GRADE_B = "GRADE_B",
  GRADE_C = "GRADE_C",
  REJECT = "REJECT",
}

export enum BatchQCState {
  QC_PENDING = "QC_PENDING",
  QC_PASSED = "QC_PASSED",
  QC_FAILED = "QC_FAILED",
}

export enum CertificationType {
  ORGANIC = "ORGANIC",
  FAIRTRADE = "FAIRTRADE",
  RAINFOREST_ALLIANCE = "RAINFOREST_ALLIANCE",
  GLOBALGAP = "GLOBALGAP",
  OTHER = "OTHER",
}

// ============ Accounting Enums ============
export enum OwnerType {
  USER = "USER",
  ESCROW = "ESCROW",
  SYSTEM = "SYSTEM",
}

export enum AccountType {
  ASSET = "ASSET",
  LIABILITY = "LIABILITY",
  EQUITY = "EQUITY",
  REVENUE = "REVENUE",
  EXPENSE = "EXPENSE",
}

export enum AggregateType {
  USER = "USER",
  ESCROW = "ESCROW",
  SYSTEM = "SYSTEM",
}

export enum LedgerEventType {
  ESCROW_FUNDED = "ESCROW_FUNDED",
  ESCROW_RELEASED = "ESCROW_RELEASED",
  ESCROW_REFUNDED = "ESCROW_REFUNDED",
  PLATFORM_FEE_COLLECTED = "PLATFORM_FEE_COLLECTED",
  PENALTY_APPLIED = "PENALTY_APPLIED",
  LOAN_DISBURSED = "LOAN_DISBURSED",
  LOAN_REPAID = "LOAN_REPAID",
}

export enum Direction {
  DEBIT = "DEBIT",
  CREDIT = "CREDIT",
}

export enum ReferenceType {
  ORDER = "ORDER",
  ESCROW = "ESCROW",
  DISPUTE = "DISPUTE",
  LOAN = "LOAN",
}

export enum RuleType {
  PLATFORM_FEE = "PLATFORM_FEE",
  DELIVERY = "DELIVERY",
  QUALITY = "QUALITY",
  DISTANCE = "DISTANCE",
}

export enum FeeType {
  PERCENTAGE = "PERCENTAGE",
  FIXED = "FIXED",
}

export enum InventoryMovementType {
  STOCK_IN = "STOCK_IN",
  RESERVATION = "RESERVATION",
  RESERVATION_RELEASE = "RESERVATION_RELEASE",
  SALE_CONFIRMED = "SALE_CONFIRMED",
  SPOILAGE = "SPOILAGE",
  RETURN = "RETURN",
  ADJUSTMENT = "ADJUSTMENT",
  EXPIRY = "EXPIRY",
}

export enum LoanState {
  PROPOSED = "PROPOSED",
  APPROVED = "APPROVED",
  DISBURSED = "DISBURSED",
  ACTIVE = "ACTIVE",
  OVERDUE = "OVERDUE",
  CLOSED = "CLOSED",
  DEFAULTED = "DEFAULTED",
}

// ============ AI Diagnosis Enums ============
export enum Priority {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  URGENT = "URGENT",
}

export enum ReportType {
  PEST = "PEST",
  DISEASE = "DISEASE",
}

export enum TreatmentStatus {
  REPORTED = "REPORTED",
  TREATMENT_RECOMMENDED = "TREATMENT_RECOMMENDED",
  TREATMENT_APPLIED = "TREATMENT_APPLIED",
  RESOLVED = "RESOLVED",
  NO_ACTION = "NO_ACTION",
}
