from folium import Map, Marker
import folium
import config
import os

icon_path = os.path.join(config.ROOT_DIR, 'static', 'images', 'marker.png')
icon = folium.features.CustomIcon(icon_path, icon_size=(25, 41))

def create_map(lat, lon):
    # Create a folium map centered at the given latitude and longitude
    # Use the 'Stamen Terrain' tiles, which can be cached for offline use
    folium_map = Map(
        location=[lat, lon],
        zoom_start=15,
        tiles='Stamen Terrain'  # Use Stamen Terrain tiles (can be cached offline)
    )

    # Add a marker for the location 
    Marker([lat, lon], popup="Current Location", icon=icon).add_to(folium_map)

    # Return the map as HTML
    return folium_map._repr_html_()