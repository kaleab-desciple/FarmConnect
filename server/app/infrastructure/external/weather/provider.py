"""Weather Provider Interface"""
from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Any


class WeatherProvider(ABC):
    """Abstract weather provider interface"""
    
    @abstractmethod
    async def get_current_weather(
        self, 
        latitude: Decimal, 
        longitude: Decimal
    ) -> Dict[str, Any]:
        """Fetch current weather conditions"""
        pass
    
    @abstractmethod
    async def get_forecast(
        self,
        latitude: Decimal,
        longitude: Decimal,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Fetch weather forecast"""
        pass
    
    @abstractmethod
    async def get_historical(
        self,
        latitude: Decimal,
        longitude: Decimal,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Fetch historical weather data"""
        pass
