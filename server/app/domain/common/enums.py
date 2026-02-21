from enum import Enum


class UserRole(str, Enum):
    FARMER = "FARMER"
    MERCHANT = "MERCHANT"
    DELIVERY = "DELIVERY"
    AGENT = "AGENT"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    AGRONOMIST = "AGRONOMIST"
    FIELD_ANALYST = "FIELD_ANALYST"
    AGGREGATOR = "AGGREGATOR"

class OrderStatus(str, Enum):
    CREATED = "CREATED"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    FUNDED = "FUNDED"
    CONFIRMED = "CONFIRMED"
    IN_DELIVERY = "IN_DELIVERY"
    DELIVERED = "DELIVERED"
    DELIVERY_FAILED = "DELIVERY_FAILED"
    RETURNED = "RETURNED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class InventoryMovementType(str, Enum):
    STOCK_IN = "STOCK_IN"
    RESERVATION = "RESERVATION"
    RESERVATION_RELEASE = "RESERVATION_RELEASE"
    SALE_CONFIRMED = "SALE_CONFIRMED"
    SPOILAGE = "SPOILAGE"
    RETURN = "RETURN"
    ADJUSTMENT = "ADJUSTMENT"
    EXPIRY = "EXPIRY"


class ProductStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    LOW_STOCK = "LOW_STOCK"
    SOLD_OUT = "SOLD_OUT"
    EXPIRED = "EXPIRED"
    DISCONTINUED = "DISCONTINUED"


class EscrowState(str, Enum):
    CREATED = "CREATED"
    FUNDED = "FUNDED"
    RELEASED = "RELEASED"
    REFUNDED = "REFUNDED"
    DISPUTED = "DISPUTED"
    SETTLED = "SETTLED"
    REVERSED = "REVERSED"


class LoanState(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    DISBURSED = "DISBURSED"
    ACTIVE = "ACTIVE"
    OVERDUE = "OVERDUE"
    CLOSED = "CLOSED"
    DEFAULTED = "DEFAULTED"


class DisputeState(str, Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    REOPENED = "REOPENED"


class DisputeResolution(str, Enum):
    RELEASE = "RELEASE"
    PARTIAL_RELEASE = "PARTIAL_RELEASE"
    REFUND = "REFUND"


class Category(str, Enum):
    VEGETABLES = "VEGETABLES"
    FRUITS = "FRUITS"
    GRAINS = "GRAINS"
    DAIRY = "DAIRY"
    MEAT = "MEAT"
    SPICES = "SPICES"
    OTHER = "OTHER"


class Unit(str, Enum):
    KG = "KG"
    TON = "TON"
    LITER = "LITER"
    UNIT = "UNIT"
    CRATE = "CRATE"
    BAG = "BAG"


class QualityGrade(str, Enum):
    GRADE_A = "GRADE_A"
    GRADE_B = "GRADE_B"
    GRADE_C = "GRADE_C"
    PREMIUM = "PREMIUM"
    STANDARD = "STANDARD"
    A = "A"  # Legacy
    B = "B"  # Legacy
    C = "C"  # Legacy


class Provider(str, Enum):
    BANK = "BANK"
    WALLET = "WALLET"


class RuleType(str, Enum):
    PLATFORM_FEE = "PLATFORM_FEE"
    DELIVERY = "DELIVERY"
    QUALITY = "QUALITY"
    DISTANCE = "DISTANCE"


class FeeType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED = "FIXED"


# Agricultural Management Enums

class CropCycleStatus(str, Enum):
    PLANNED = "PLANNED"
    PLANTED = "PLANTED"
    GROWING = "GROWING"
    HARVESTED = "HARVESTED"
    PARTIALLY_HARVESTED = "PARTIALLY_HARVESTED"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"


class NDVISource(str, Enum):
    SENTINEL_2 = "SENTINEL_2"
    LANDSAT_8 = "LANDSAT_8"
    LANDSAT_9 = "LANDSAT_9"
    MODIS = "MODIS"
    MANUAL = "MANUAL"


class StressLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SoilReadingSource(str, Enum):
    IOT_SENSOR = "IOT_SENSOR"
    MANUAL_TEST = "MANUAL_TEST"
    LAB_ANALYSIS = "LAB_ANALYSIS"
    ESTIMATED = "ESTIMATED"


class SeverityLevel(str, Enum):
    TRACE = "TRACE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


class RecommendationSource(str, Enum):
    AGRONOMIST = "AGRONOMIST"
    SYSTEM = "SYSTEM"
    AI_MODEL = "AI_MODEL"
    COMMUNITY = "COMMUNITY"


class TaskType(str, Enum):
    LAND_PREPARATION = "LAND_PREPARATION"
    SOWING = "SOWING"
    PLANTING = "PLANTING"
    IRRIGATION = "IRRIGATION"
    FERTILIZATION = "FERTILIZATION"
    WEEDING = "WEEDING"
    PEST_CONTROL = "PEST_CONTROL"
    DISEASE_CONTROL = "DISEASE_CONTROL"
    PRUNING = "PRUNING"
    THINNING = "THINNING"
    HARVESTING = "HARVESTING"
    POST_HARVEST = "POST_HARVEST"
    INSPECTION = "INSPECTION"
    MAINTENANCE = "MAINTENANCE"
    OTHER = "OTHER"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"
    OVERDUE = "OVERDUE"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class WeatherSource(str, Enum):
    NOAA_GFS = "NOAA_GFS"
    NOAA_HRRR = "NOAA_HRRR"
    OPEN_METEO = "OPEN_METEO"
    LOCAL_STATION = "LOCAL_STATION"
    MANUAL = "MANUAL"


class RiskType(str, Enum):
    FROST = "FROST"
    FREEZE = "FREEZE"
    HEAT_STRESS = "HEAT_STRESS"
    DROUGHT = "DROUGHT"
    HEAVY_RAIN = "HEAVY_RAIN"
    FLOOD = "FLOOD"
    HAIL = "HAIL"
    STRONG_WIND = "STRONG_WIND"
    STORM = "STORM"
    HURRICANE = "HURRICANE"
    TORNADO = "TORNADO"
    WILDFIRE = "WILDFIRE"
    PEST_OUTBREAK = "PEST_OUTBREAK"
    DISEASE_OUTBREAK = "DISEASE_OUTBREAK"


class RiskLevel(str, Enum):
    MINIMAL = "MINIMAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(str, Enum):
    WEATHER_WARNING = "WEATHER_WARNING"
    FROST_ALERT = "FROST_ALERT"
    DROUGHT_ALERT = "DROUGHT_ALERT"
    PEST_DETECTED = "PEST_DETECTED"
    DISEASE_DETECTED = "DISEASE_DETECTED"
    NDVI_ANOMALY = "NDVI_ANOMALY"
    SOIL_MOISTURE_LOW = "SOIL_MOISTURE_LOW"
    SOIL_MOISTURE_HIGH = "SOIL_MOISTURE_HIGH"
    TASK_OVERDUE = "TASK_OVERDUE"
    HARVEST_READY = "HARVEST_READY"
    LOAN_RISK = "LOAN_RISK"
    PAYMENT_DUE = "PAYMENT_DUE"
    ESCROW_HOLD = "ESCROW_HOLD"
    PRICE_ALERT = "PRICE_ALERT"
    SYSTEM_NOTIFICATION = "SYSTEM_NOTIFICATION"


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class AdvisoryStatus(str, Enum):
    REQUESTED = "REQUESTED"
    SCHEDULED = "SCHEDULED"
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class AdvisoryTopic(str, Enum):
    CROP_SELECTION = "CROP_SELECTION"
    PEST_MANAGEMENT = "PEST_MANAGEMENT"
    DISEASE_MANAGEMENT = "DISEASE_MANAGEMENT"
    SOIL_HEALTH = "SOIL_HEALTH"
    IRRIGATION = "IRRIGATION"
    FERTILIZATION = "FERTILIZATION"
    HARVEST_TIMING = "HARVEST_TIMING"
    POST_HARVEST = "POST_HARVEST"
    MARKET_ADVICE = "MARKET_ADVICE"
    FINANCIAL_PLANNING = "FINANCIAL_PLANNING"
    GENERAL = "GENERAL"


class MessageType(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    DOCUMENT = "DOCUMENT"
    VOICE = "VOICE"
    VIDEO = "VIDEO"
    LOCATION = "LOCATION"
    SYSTEM = "SYSTEM"


# Aggregator Reconciliation & Settlement Enums

class ReconciliationStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DISPUTED = "DISPUTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class SettlementStatus(str, Enum):
    PENDING = "PENDING"
    PREPARED = "PREPARED"
    APPROVED = "APPROVED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SettlementMethod(str, Enum):
    BY_WEIGHT = "BY_WEIGHT"          # Proportional by delivered weight
    BY_VALUE = "BY_VALUE"            # Proportional by crop value
    FIXED_RATE = "FIXED_RATE"       # Fixed rate per unit
    TIERED = "TIERED"                # Tiered based on quality grade


class WeighmentType(str, Enum):
    INITIAL = "INITIAL"              # Initial weighment at aggregator
    VERIFICATION = "VERIFICATION"     # Re-weighment for verification
    FINAL = "FINAL"                  # Final weighment after processing


class SmallholderPaymentStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    FAILED = "FAILED"


# QC/Grading Enums


class QCGrade(str, Enum):
    """Quality grade for QC evaluation."""
    GRADE_A = "GRADE_A"
    GRADE_B = "GRADE_B"
    GRADE_C = "GRADE_C"
    REJECT = "REJECT"


class BatchQCState(str, Enum):
    """Batch QC status states."""
    QC_PENDING = "QC_PENDING"
    QC_PASSED = "QC_PASSED"
    QC_FAILED = "QC_FAILED"


class CertificationType(str, Enum):
    """Certification types for products."""
    ORGANIC = "ORGANIC"
    FAIRTRADE = "FAIRTRADE"
    RAINFOREST_ALLIANCE = "RAINFOREST_ALLIANCE"
    GLOBALGAP = "GLOBALGAP"
    OTHER = "OTHER"

