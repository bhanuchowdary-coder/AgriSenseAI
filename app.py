
from flask import Flask, render_template, jsonify, request

from services.vegetation import analyze_vegetation
from services.sensors import analyze_sensor
from services.sensor_fusion import filter_sensor_data

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({
        "status": "success",
        "project": "AgriSense AI",
        "message": "Backend connected successfully"
    })


@app.route("/api/vegetation", methods=["POST"])
def vegetation():
    try:
        data = request.get_json(silent=True)

        result = analyze_vegetation(
            float(data["nir"]),
            float(data["red"]),
            float(data["blue"])
        )

        return jsonify({
            "status": "success",
            "data": result
        })

    except (ValueError, KeyError, TypeError) as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400


@app.route("/api/sensors", methods=["POST"])
def sensors():
    try:
        data = request.get_json(silent=True)
        result = analyze_sensor(data)

        return jsonify({
            "status": "success",
            "data": result
        })

    except (ValueError, KeyError, TypeError) as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400


@app.route("/api/sensor-fusion", methods=["POST"])
def sensor_fusion():
    try:
        data = request.get_json(silent=True)
        readings = data["readings"]

        filtered = filter_sensor_data(readings)

        return jsonify({
            "status": "success",
            "raw_readings": readings,
            "filtered_readings": filtered
        })

    except (ValueError, KeyError, TypeError) as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
