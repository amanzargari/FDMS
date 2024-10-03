import osmium
import json
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
import urllib.parse
import pickle
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import config

def start_http_server():
    """
    Starts an HTTP server on localhost at port 8000 in a separate daemon thread.

    This function initializes an HTTP server using the SimpleHTTPRequestHandler
    and binds it to the address ('localhost', 8000). The server is then started
    in a new daemon thread, allowing it to run in the background indefinitely.

    Note:
        The server runs in a daemon thread, which means it will automatically
        shut down when the main program exits.

    Returns:
        None
    """
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', 8000), handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()

class OSMHandler(osmium.SimpleHandler):
    """
    OSMHandler is a class that extends osmium.SimpleHandler to process OpenStreetMap (OSM) data.
    Attributes:
        ways (list): A list to store way elements from the OSM data.
    Methods:
        __init__(cache_file=None):
            Initializes the OSMHandler instance. If a cache file is provided, it loads the way elements from the cache file.
            Args:
                cache_file (str, optional): Path to the cache file containing pre-processed OSM data. Defaults to None.
    """
    def __init__(self, cache_file=None):
        super(OSMHandler, self).__init__()
        #self.nodes = []
        self.ways = []
        
        if cache_file:
            with open(config.MAP_FILE, 'rb') as f:
                map_data = pickle.load(f)
            #self.nodes = map_data['nodes']
            self.ways = map_data['ways']
            map_data = None

class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    """
    A custom URL request interceptor for handling specific URL requests.
    Attributes:
        ways (dict): A dictionary containing map data to be served.
    Methods:
        interceptRequest(info):
            Intercepts requests to the "/map_data" URL path and redirects them
            to a data URL containing the JSON-encoded map data.
    """
    def __init__(self, ways):
        super().__init__()
        self.ways = ways

    def interceptRequest(self, info):
        if info.requestUrl().path() == "/map_data":
            data = json.dumps(self.ways)
            info.redirect(QUrl(f"data:application/json,{urllib.parse.quote(data)}"))

def load_map(latitude, longitude):
        """
        Generates an HTML string to display a GPS map with a car icon at the specified latitude and longitude.
        Args:
            latitude (float): The latitude coordinate for the initial map view and car icon position.
            longitude (float): The longitude coordinate for the initial map view and car icon position.
        Returns:
            str: An HTML string that includes the necessary elements and scripts to render a map using Leaflet.js.
                 The map includes a car icon at the specified coordinates and can be updated dynamically with new coordinates,
                 speed, and heading.
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>GPS Map with Car Icon</title>
            <link rel="stylesheet" href="http://localhost:8000/static/css/leaflet.css"/>
            <script src="http://localhost:8000/static/scripts/leaflet.js"></script>
            <script src="http://localhost:8000/static/scripts/leaflet.rotatedMarker.js"></script>
            <style>
                #map {{ height: 100vh; width: 100%; }}
            </style>
        </head>
        <body style="margin:0; padding:0;">
            <div id="map"></div>
            <script>
                const map = L.map('map').setView([{latitude}, {longitude}], 15);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© OpenStreetMap contributors'
                }}).addTo(map);

                const customLayer = L.layerGroup().addTo(map);
                
                // Car icon
                const carIcon = L.icon({{
                    iconUrl: 'http://localhost:8000/static/images/marker.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                }});
                const marker = L.marker([{latitude}, {longitude}], {{icon: carIcon}}).addTo(map);

                fetch('/map_data')
                    .then(response => response.json())
                    .then(data => {{
                        data.forEach(way => {{
                            L.polyline(way.nodes, {{color: '#ff0000', weight: 2}}).addTo(customLayer);
                        }});
                    }});

                window.updateMarker = function(lat, lon, speed, heading) {{
                    marker.setLatLng([lat, lon]);
                    marker.setRotationAngle(heading);
                    map.panTo([lat, lon]);
                }};
            </script>
        </body>
        </html>
        """
        return html