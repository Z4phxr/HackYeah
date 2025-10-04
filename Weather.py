from geopy.geocoders import Nominatim
from pyowm import OWM

# --- CONFIGURATION ---
OWM_API_KEY = "ae3c191e1f8e13cc34955c04c4dbba66"

# --- USER INPUT ---
city = input("Enter a city name: ")

# --- LOCATION LOOKUP ---
geolocator = Nominatim(user_agent="travel_app")
location = geolocator.geocode(city)

if not location:
    print("❌ City not found. Try again.")
    exit()

latitude = location.latitude
longitude = location.longitude
print(f"📍 {city}: {latitude}, {longitude}")

# --- WEATHER DATA ---
owm = OWM(OWM_API_KEY)
mgr = owm.weather_manager()
weather = mgr.weather_at_coords(latitude, longitude).weather

temp = weather.temperature('celsius')["temp"]
status = weather.detailed_status
print(f"🌦 Weather: {status}, {temp}°C")

# --- GOOGLE MAPS LINK ---
maps_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
print(f"🌐 Open in Google Maps: {maps_url}")
