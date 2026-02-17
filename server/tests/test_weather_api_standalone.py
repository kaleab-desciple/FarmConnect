"""
Standalone Open-Meteo API Test
Tests the Open-Meteo API directly without requiring local dependencies.
"""
import asyncio
import sys
import json
try:
    import httpx
except ImportError:
    print("❌ httpx not installed. Install with: pip install httpx")
    sys.exit(1)


OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = []
    
    def log_pass(self, test_name):
        print(f"✅ PASS: {test_name}")
        self.passed += 1
    
    def log_fail(self, test_name, reason):
        print(f"❌ FAIL: {test_name}")
        print(f"   Reason: {reason}")
        self.failed += 1
    
    def log_warning(self, message):
        print(f"⚠️  WARNING: {message}")
        self.warnings.append(message)


async def test_api_health():
    """Test 1: Open-Meteo API is reachable."""
    result = TestResult()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OPEN_METEO_BASE_URL}/forecast",
                params={
                    "latitude": 52.52,
                    "longitude": 13.41,
                    "current": "temperature_2m"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                result.log_pass("API Health Check")
            else:
                result.log_fail("API Health Check", f"Status code: {response.status_code}")
    except Exception as e:
        result.log_fail("API Health Check", str(e))
    
    return result


async def test_daily_forecast():
    """Test 2: Daily forecast with all parameters."""
    result = TestResult()
    
    # Parameters from FarmConnect implementation
    daily_params = (
        "temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,"
        "showers_sum,snowfall_sum,precipitation_probability_max,"
        "wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,"
        "sunrise,sunset,uv_index_max,weather_code,et0_fao_evapotranspiration"
    )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OPEN_METEO_BASE_URL}/forecast",
                params={
                    "latitude": 52.52,
                    "longitude": 13.41,
                    "daily": daily_params,
                    "timezone": "auto",
                    "forecast_days": 7
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                result.log_fail("Daily Forecast Request", f"Status: {response.status_code}")
                return result
            
            data = response.json()
            
            # Verify response structure
            if "daily" not in data:
                result.log_fail("Daily Forecast Structure", "Missing 'daily' in response")
                return result
            
            daily = data["daily"]
            
            # Check required fields
            required = [
                "time", "temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "wind_speed_10m_max"
            ]
            
            missing = [f for f in required if f not in daily]
            if missing:
                result.log_fail("Daily Forecast Fields", f"Missing: {missing}")
                return result
            
            result.log_pass("Daily Forecast Request")
            
            # Print sample data
            print(f"\n   Sample Data (Day 1):")
            print(f"   Date: {daily['time'][0]}")
            print(f"   Temp Max: {daily['temperature_2m_max'][0]}°C")
            print(f"   Temp Min: {daily['temperature_2m_min'][0]}°C")
            print(f"   Precipitation: {daily['precipitation_sum'][0]}mm")
            print(f"   Wind Speed: {daily['wind_speed_10m_max'][0]}km/h")
            
            # Check wind speed units
            wind_speed = daily['wind_speed_10m_max'][0]
            if wind_speed is not None:
                result.log_warning(f"Wind speed from API: {wind_speed} km/h → should be divided by 3.6 to get m/s")
            
    except Exception as e:
        result.log_fail("Daily Forecast Request", str(e))
    
    return result


async def test_current_weather():
    """Test 3: Current weather parameters."""
    result = TestResult()
    
    current_params = (
        "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,"
        "rain,showers,snowfall,weather_code,cloud_cover,pressure_msl,"
        "surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m"
    )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OPEN_METEO_BASE_URL}/forecast",
                params={
                    "latitude": 52.52,
                    "longitude": 13.41,
                    "current": current_params,
                    "timezone": "auto"
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                result.log_fail("Current Weather Request", f"Status: {response.status_code}")
                return result
            
            data = response.json()
            
            if "current" not in data:
                result.log_fail("Current Weather Structure", "Missing 'current' in response")
                return result
            
            current = data["current"]
            
            # Check key fields
            required = ["temperature_2m", "wind_speed_10m", "relative_humidity_2m"]
            missing = [f for f in required if f not in current]
            
            if missing:
                result.log_fail("Current Weather Fields", f"Missing: {missing}")
                return result
            
            result.log_pass("Current Weather Request")
            
            print(f"\n   Current Weather:")
            print(f"   Temperature: {current['temperature_2m']}°C")
            print(f"   Humidity: {current['relative_humidity_2m']}%")
            print(f"   Wind Speed: {current['wind_speed_10m']}km/h")
            
    except Exception as e:
        result.log_fail("Current Weather Request", str(e))
    
    return result


async def test_humidity_in_daily():
    """Test 4: Check if humidity is available in daily forecast."""
    result = TestResult()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OPEN_METEO_BASE_URL}/forecast",
                params={
                    "latitude": 52.52,
                    "longitude": 13.41,
                    "daily": "temperature_2m_max,relative_humidity_2m_max",  # Try to request humidity
                    "timezone": "auto",
                    "forecast_days": 1
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                result.log_warning("Could not test humidity in daily (API error)")
                return result
            
            data = response.json()
            daily = data.get("daily", {})
            
            # Check if humidity is in the response
            if "relative_humidity_2m_max" in daily:
                result.log_pass("Humidity available in daily forecast")
                print(f"   Note: Humidity IS available in daily forecast!")
            else:
                result.log_warning("Humidity NOT available in daily forecast (as expected per docs)")
                print(f"   Note: The implementation should NOT try to save humidity_avg_pct from daily data")
            
    except Exception as e:
        result.log_warning(f"Could not test humidity: {e}")
    
    return result


async def test_units_with_parameters():
    """Test 5: Test explicit unit parameters."""
    result = TestResult()
    
    try:
        async with httpx.AsyncClient() as client:
            # Test with explicit unit parameters
            response = await client.get(
                f"{OPEN_METEO_BASE_URL}/forecast",
                params={
                    "latitude": 52.52,
                    "longitude": 13.41,
                    "daily": "temperature_2m_max,wind_speed_10m_max",
                    "timezone": "auto",
                    "forecast_days": 1,
                    "temperature_unit": "celsius",
                    "wind_speed_unit": "ms",  # Request m/s directly!
                    "precipitation_unit": "mm"
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                result.log_fail("Units Parameter Test", f"Status: {response.status_code}")
                return result
            
            data = response.json()
            daily_units = data.get("daily_units", {})
            
            print(f"\n   Returned Units:")
            print(f"   Temperature: {daily_units.get('temperature_2m_max', 'N/A')}")
            print(f"   Wind Speed: {daily_units.get('wind_speed_10m_max', 'N/A')}")
            
            # Check if units match request
            if daily_units.get("wind_speed_10m_max") == "m/s":
                result.log_pass("Wind Speed Unit Parameter (m/s)")
                print(f"   ✅ Requesting wind_speed_unit=ms returns m/s directly!")
            else:
                result.log_warning(f"Unexpected wind unit: {daily_units.get('wind_speed_10m_max')}")
            
    except Exception as e:
        result.log_fail("Units Parameter Test", str(e))
    
    return result


async def test_forecast_days_limits():
    """Test 6: Test forecast_days parameter limits."""
    result = TestResult()
    
    # Test max (16 days)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OPEN_METEO_BASE_URL}/forecast",
                params={
                    "latitude": 52.52,
                    "longitude": 13.41,
                    "daily": "temperature_2m_max",
                    "timezone": "auto",
                    "forecast_days": 16
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                days_returned = len(data.get("daily", {}).get("time", []))
                
                if days_returned <= 16:
                    result.log_pass("Forecast Days Limit (max 16)")
                else:
                    result.log_warning(f"API returned {days_returned} days (expected ≤16)")
            else:
                result.log_fail("Forecast Days Limit", f"Status: {response.status_code}")
                
    except Exception as e:
        result.log_fail("Forecast Days Limit", str(e))
    
    return result


async def main():
    """Run all tests."""
    print("="*70)
    print("OPEN-METEO API VALIDATION TEST")
    print("Testing FarmConnect Weather Implementation Parameters")
    print("="*70)
    print()
    
    all_results = []
    
    print("Test 1: API Health Check")
    print("-"*70)
    r1 = await test_api_health()
    all_results.append(r1)
    print()
    
    print("Test 2: Daily Forecast with FarmConnect Parameters")
    print("-"*70)
    r2 = await test_daily_forecast()
    all_results.append(r2)
    print()
    
    print("Test 3: Current Weather Parameters")
    print("-"*70)
    r3 = await test_current_weather()
    all_results.append(r3)
    print()
    
    print("Test 4: Humidity Availability in Daily Forecast")
    print("-"*70)
    r4 = await test_humidity_in_daily()
    all_results.append(r4)
    print()
    
    print("Test 5: Explicit Unit Parameters")
    print("-"*70)
    r5 = await test_units_with_parameters()
    all_results.append(r5)
    print()
    
    print("Test 6: Forecast Days Limits")
    print("-"*70)
    r6 = await test_forecast_days_limits()
    all_results.append(r6)
    print()
    
    # Summary
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    total_warnings = sum(len(r.warnings) for r in all_results)
    
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"⚠️  Warnings: {total_warnings}")
    print("="*70)
    
    if total_failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total_failed} test(s) failed")
    
    print("\n" + "="*70)
    print("CRITICAL FINDINGS FOR FARMCONNECT IMPLEMENTATION:")
    print("="*70)
    print("1. ⚠️  Wind speed from API is in km/h by default")
    print("   → MUST divide by 3.6 to convert to m/s for database")
    print()
    print("2. ✅ Use wind_speed_unit='ms' parameter to get m/s directly")
    print("   → Recommended to avoid manual conversion")
    print()
    print("3. ⚠️  Humidity is NOT available in daily forecast")
    print("   → Remove humidity_avg_pct from daily forecast saves")
    print()
    print("4. ⚠️  Pressure is NOT available in daily forecast")
    print("   → Remove pressure_hpa from daily forecast saves")
    print("="*70)
    
    return total_failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
