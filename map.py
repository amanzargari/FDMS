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
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', 8000), handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()

class OSMHandler(osmium.SimpleHandler):
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
    def __init__(self, ways):
        super().__init__()
        self.ways = ways

    def interceptRequest(self, info):
        if info.requestUrl().path() == "/map_data":
            data = json.dumps(self.ways)
            info.redirect(QUrl(f"data:application/json,{urllib.parse.quote(data)}"))

def load_map(latitude, longitude):
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