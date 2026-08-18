from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all origins, methods, and headers
CORS(app, resources={r"/*": {"origins": "*"}})

# In-memory game state
sessions = {}

PLANT_DATA = {
    "sunflower": {"cost": 50, "hp": 300},
    "peashooter": {"cost": 100, "hp": 300},
    "wallnut": {"cost": 50, "hp": 4000},
}


@app.route("/", methods=["GET"])
def index():
  return jsonify(
      {"status": "PlantsVsZombies PaaS Backend is Live", "version": "1.0"}
  )


@app.route("/api/session/start", methods=["GET", "POST"])
def start_session():
  data = request.get_json(silent=True) or {}
  player_id = data.get("player_id", "player_1")
  sessions[player_id] = {
      "sun": 150,
      "wave": 1,
      "score": 0,
      "grid": [[None for _ in range(9)] for _ in range(5)],
  }
  return jsonify({"success": True, "state": sessions[player_id]})


@app.route("/api/game/plant", methods=["POST", "OPTIONS"])
def plant():
  if request.method == "OPTIONS":
    return jsonify({"status": "ok"}), 200

  data = request.get_json(silent=True) or {}
  player_id = data.get("player_id", "player_1")

  # Auto-initialize session if it doesn't exist yet
  if player_id not in sessions:
    sessions[player_id] = {
        "sun": 150,
        "wave": 1,
        "score": 0,
        "grid": [[None for _ in range(9)] for _ in range(5)],
    }

  session = sessions[player_id]
  row = data.get("row")
  col = data.get("col")
  plant_type = data.get("plant_type", "peashooter")

  plant_info = PLANT_DATA.get(plant_type)
  if not plant_info:
    return jsonify({"error": "Invalid plant type"}), 400

  if session["sun"] < plant_info["cost"]:
    return jsonify({"success": False, "message": "Not enough sun!"}), 400

  if session["grid"][row][col] is not None:
    return jsonify({"success": False, "message": "Tile already occupied!"}), 400

  # Deduct sun and update grid
  session["sun"] -= plant_info["cost"]
  session["grid"][row][col] = plant_type

  return jsonify({"success": True, "state": session})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
