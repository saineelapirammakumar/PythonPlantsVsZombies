import random
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory game state for mobile clients
sessions = {}

# Plant costs from marblexu/PythonPlantsVsZombies
PLANT_DATA = {
    "sunflower": {"cost": 50, "hp": 300},
    "peashooter": {"cost": 100, "hp": 300},
    "wallnut": {"cost": 50, "hp": 4000},
    "cherrybomb": {"cost": 150, "hp": 300},
}


@app.route("/")
def index():
  return jsonify(
      {"status": "PlantsVsZombies PaaS Backend is Live", "version": "1.0"}
  )


@app.route("/api/session/start", methods=["POST"])
def start_session():
  data = request.get_json() or {}
  player_id = data.get("player_id", "player_1")
  sessions[player_id] = {
      "sun": 150,
      "wave": 1,
      "score": 0,
      "grid": [[None for _ in range(9)] for _ in range(5)],
  }
  return jsonify({"success": True, "state": sessions[player_id]})


@app.route("/api/game/plant", methods=["POST"])
def plant():
  data = request.get_json() or {}
  player_id = data.get("player_id", "player_1")
  row = data.get("row")
  col = data.get("col")
  plant_type = data.get("plant_type")

  if player_id not in sessions:
    return jsonify({"error": "Session not found"}), 404

  session = sessions[player_id]
  plant_info = PLANT_DATA.get(plant_type)

  if not plant_info:
    return jsonify({"error": "Invalid plant type"}), 400

  if session["sun"] < plant_info["cost"]:
    return jsonify({"success": False, "message": "Not enough sun"}), 400

  if session["grid"][row][col] is not None:
    return jsonify({"success": False, "message": "Tile already occupied"}), 400

  # Deduct sun and update grid
  session["sun"] -= plant_info["cost"]
  session["grid"][row][col] = plant_type

  return jsonify({"success": True, "state": session})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
