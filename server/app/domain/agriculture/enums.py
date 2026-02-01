"""Agricultural Intelligence Enums"""
from enum import Enum


class CropCycleStatus(str, Enum):
    """Crop cycle status"""
    PLANNED = "PLANNED"
    PLANTED = "PLANTED"
    GROWING = "GROWING"
    HARVESTED = "HARVESTED"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"


class NDVISource(str, Enum):
    """NDVI data source"""
    SENTINEL_2 = "SENTINEL_2"
    LANDSAT_8 = "LANDSAT_8"
    LANDSAT_9 = "LANDSAT_9"
    MODIS = "MODIS"
    MANUAL = "MANUAL"


class StressLevel(str, Enum):
    """Crop stress level"""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SoilReadingSource(str, Enum):
    """Soil reading source"""
    IOT_SENSOR = "IOT_SENSOR"
    MANUAL_TEST = "MANUAL_TEST"
    LAB_ANALYSIS = "LAB_ANALYSIS"
    ESTIMATED = "ESTIMATED"


class SeverityLevel(str, Enum):
    """Pest/disease severity level"""
    TRACE = "TRACE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


class RecommendationSource(str, Enum):
    """Treatment recommendation source"""
    AGRONOMIST = "AGRONOMIST"
    SYSTEM = "SYSTEM"
    AI_MODEL = "AI_MODEL"
    COMMUNITY = "COMMUNITY"


class TaskType(str, Enum):
    """Farm task type"""
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
    """Farm task status"""
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"
    OVERDUE = "OVERDUE"


class TaskPriority(str, Enum):
    """Task priority"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class WeatherSource(str, Enum):
    """Weather data source"""
    NOAA_GFS = "NOAA_GFS"
    NOAA_HRRR = "NOAA_HRRR"
    OPEN_METEO = "OPEN_METEO"
    LOCAL_STATION = "LOCAL_STATION"
    MANUAL = "MANUAL"


class RiskType(str, Enum):
    """Risk type"""
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
    """Risk level"""
    MINIMAL = "MINIMAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(str, Enum):
    """Alert type"""
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
    """Alert severity"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class AdvisoryStatus(str, Enum):
    """Advisory session status"""
    REQUESTED = "REQUESTED"
    SCHEDULED = "SCHEDULED"
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class AdvisoryTopic(str, Enum):
    """Advisory topic"""
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
    """Message type"""
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    DOCUMENT = "DOCUMENT"
    VOICE = "VOICE"
    VIDEO = "VIDEO"
    LOCATION = "LOCATION"
    SYSTEM = "SYSTEM"
