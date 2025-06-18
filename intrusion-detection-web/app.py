from flask import Flask, request, jsonify, render_template
from backend import detect_intrusions, attack_patterns
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        content = file.read().decode('utf-8')
        return jsonify({'content': content})

@app.route('/detect', methods=['POST'])
def detect():
    try:
        data = request.get_json()
        if not data or 'logs' not in data:
            return jsonify({'error': 'No logs provided'}), 400
        
        logs = data.get('logs', [])
        algorithm = data.get('algorithm', 'kmp')
        
        if not logs:
            return jsonify({'error': 'Empty logs provided'}), 400
        
        start_time = time.time()
        results = detect_intrusions(logs, attack_patterns, algorithm)
        end_time = time.time()
        
        formatted_results = []
        for log, pattern, steps, indices, count in results:
            formatted_results.append({
                'log': log,
                'pattern': pattern,
                'steps': steps,
                'algorithm': algorithm.upper(),
                'indices': indices,
                'count': count
            })
        
        return jsonify({
            'detections': formatted_results,
            'total_detections': len(results),
            'execution_time': round(end_time - start_time, 6),
            'algorithm_used': algorithm.upper()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)