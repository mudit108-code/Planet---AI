import uuid
import random
from datetime import datetime
from database import get_connection

class ZyndBaseAgent:
    def __init__(self, name, role, trust=0.9):
        
        self.agent_id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.trust = trust
        
        self._register()

    def _register(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO agents VALUES (?,?,?,?)",
            (self.agent_id, self.name, self.role, self.trust)
        )
        conn.commit()
        conn.close()

    
    def send_message(self, msg_type, data):
        return data

# Weather agent
class WeatherAgent(ZyndBaseAgent):
    def produce_weather(self):
        data = {
            "rainfall_mm": random.randint(80, 320),
            "river_level_m": round(random.uniform(2.5, 9.0), 2)
        }
        return self.send_message("weather_data", data)

# Flood prediction agent
class FloodPredictionAgent(ZyndBaseAgent):
    def analyze(self, weather_msg):
        rain = weather_msg["rainfall_mm"]
        river = weather_msg["river_level_m"]

        probability = min(1.0, (rain / 320 + river / 9.0) / 2)

        severity = (
            "Severe" if probability > 0.7 else
            "Moderate" if probability > 0.4 else
            "Low"
        )

        return self.send_message("flood_prediction", {
            "probability": round(probability, 2),
            "severity": severity
        })

# Emergency coordination agent
class EmergencyCoordinationAgent(ZyndBaseAgent):
    def plan(self, flood_msg):
        severity = flood_msg["severity"]

        action = {
            "Severe": "Deploy rescue boats, NDRF teams, medical units",
            "Moderate": "Prepare shelters, keep rescue teams on standby",
            "Low": "Monitor situation"
        }[severity]

        return self.send_message("response_plan", {"action": action})

# Community alert agent
class CommunityAlertAgent(ZyndBaseAgent):
    def broadcast(self, region, flood_msg):
        confidence = round(flood_msg["probability"] * self.trust, 2)
        message = f"⚠ Flood Alert ({flood_msg['severity']}) – Stay safe & follow instructions"

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO alerts VALUES (?,?,?,?)",
            (region, message, confidence, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

        return message, confidence
