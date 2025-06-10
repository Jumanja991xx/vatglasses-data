import os
import json
from typing import List, Dict, Any
from flask import Flask, jsonify, abort

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Maps from pre code to positions
pre_to_positions: Dict[str, List[Dict[str, Any]]] = {}
# Store airport info
airport_info: Dict[str, Dict[str, Any]] = {}
# Map from airport code to relevant codes
airport_to_codes: Dict[str, List[str]] = {}


def load_data() -> None:
    """Load all JSON files under DATA_DIR into lookup tables."""
    for root, _, files in os.walk(DATA_DIR):
        for fname in files:
            if not fname.endswith('.json'):
                continue
            path = os.path.join(root, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                # Skip invalid JSON files
                continue
            if not isinstance(data, dict):
                continue
            # Positions
            for pid, pos in data.get('positions', {}).items():
                pre_list = pos.get('pre', [])
                if not isinstance(pre_list, list):
                    pre_list = [pre_list]
                info = {
                    'id': pid,
                    'callsign': pos.get('callsign'),
                    'frequency': pos.get('frequency'),
                    'type': pos.get('type'),
                }
                for code in pre_list:
                    pre_to_positions.setdefault(str(code), []).append(info)
            # Airports
            for icao, info in data.get('airports', {}).items():
                airport_info[icao] = info
                codes: List[str] = []
                for key in ('pre', 'topdown', 'sector', 'major'):
                    val = info.get(key)
                    if not val:
                        continue
                    if isinstance(val, list):
                        codes.extend(str(v) for v in val)
                    else:
                        codes.append(str(val))
                airport_to_codes[icao] = codes


def get_controllers(airport: str) -> List[Dict[str, Any]]:
    """Return list of controllers for given airport ICAO."""
    icao = airport.upper()
    codes = airport_to_codes.get(icao, []) + [icao]
    controllers = []
    seen = set()
    for code in codes:
        for pos in pre_to_positions.get(code, []):
            key = (pos['id'], pos.get('frequency'))
            if key in seen:
                continue
            seen.add(key)
            controllers.append({
                'id': pos['id'],
                'callsign': pos.get('callsign'),
                'frequency': pos.get('frequency'),
                'type': pos.get('type'),
            })
    return controllers


def create_app() -> Flask:
    load_data()
    app = Flask(__name__)

    @app.route('/airport/<icao>')
    def airport_endpoint(icao: str):
        controllers = get_controllers(icao)
        if not controllers:
            abort(404)
        return jsonify({'airport': icao.upper(), 'controllers': controllers})

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8000)
