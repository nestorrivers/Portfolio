from public_data.domains.weather.services import fetch_weather

source = BbcWeatherSource(location_code="2643123", location_name="Nottingham")
entries = fetch_weather(source)

for e in entries:
    print(e.day, e.avg_temp_c, e.description)
