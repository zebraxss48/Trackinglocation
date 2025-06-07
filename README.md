## 📍 **About This Tool: Hacker Tracker Dashboard**

This is a **Flask-based real-time location tracker** designed for cybersecurity research, red teaming, or internal monitoring. It uses a public **Ngrok tunnel** to expose your local Flask app to the internet and allows you to:

* Generate a tracking URL (`/click`)
* Capture:

  * Visitor’s IP address
  * Device/browser (User-Agent)
  * City & Country (via reverse geolocation)
  * Latitude & Longitude (if location permission is granted)
* View all results on a live **dashboard with a map and table UI**

---

## ✅ **How to Use**

1. **Install Required Packages**
   Make sure Python is installed. Then run:

   ```bash
   pip install flask flask-cors pyngrok
   ```

2. **Start the App**
   Save your script as `app.py` and run:

   ```bash
   python app.py
   ```

   On start, it will:

   * Launch a Flask server at `http://localhost:5000`
   * Automatically open an Ngrok tunnel like `https://abc123.ngrok.io`

3. **Send Tracking URL**
   Share this link with your target or test user:

   ```
   https://abc123.ngrok.io/click
   ```

   Once someone clicks:

   * Location data will be collected and logged.
   * Results are displayed live at your dashboard root URL (`/`).

---

## 📌 **Requirements**

| Component         | Description                                                         |
| ----------------- | ------------------------------------------------------------------- |
| **Python 3.7+**   | Required to run the Flask app                                       |
| **Flask**         | Web server framework                                                |
| **Flask-CORS**    | To allow cross-origin requests from frontend JS                     |
| **pyngrok**       | To expose local Flask app to the internet securely                  |
| **Ngrok Account** | *(Optional but recommended)* Add your auth token for stable tunnels |

---

## 🛠️ Optional Improvements (Recommended for Production)

* Use HTTPS tunnel with verified Ngrok auth token.
* Store visit logs to a database (SQLite, MongoDB, etc.).
* Add authentication for dashboard access.
* Obfuscate or encode the tracking URL (for stealth).
* Host the script on a VPS or cloud server to avoid relying on Ngrok.

---

