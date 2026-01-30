from enum import Enum


class UserRole(str, Enum):
    FARMER = "FARMER"
    MERCHANT = "MERCHANT"
    DELIVERY = "DELIVERY"
    AGENT = "AGENT"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


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
    # Assuming some categories
    VEGETABLES = "VEGETABLES"
    FRUITS = "FRUITS"
    GRAINS = "GRAINS"


class Unit(str, Enum):
    KG = "KG"
    TON = "TON"
    LITER = "LITER"


class QualityGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"


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