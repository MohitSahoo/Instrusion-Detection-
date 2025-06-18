# app.py

from flask import Flask, render_template, request, jsonify
from string_matching_algorithms import StringMatchingAlgorithms
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import matplotlib.pyplot as plt
import io
import base64
import seaborn as sns # For nicer plots

app = Flask(__name__)
sma = StringMatchingAlgorithms()

# Define simplified scenarios
CYBER_SCENARIOS = {
    'string_search': {
        'name': 'String Search',
        'description': 'Search for a pattern within a text. This is the fundamental operation for many data processing tasks.',
        'text_label': 'Text',
        'pattern_label': 'Pattern to Search',
        'example_text': 'The quick brown fox jumps over the lazy dog. A quick fox is hard to catch.',
        'example_pattern': 'quick fox'
    }
}


@app.route('/')
def index():
    """Renders the main HTML page."""
    # Pass scenarios to template so JavaScript can access them
    return render_template('index.html', cyber_scenarios=CYBER_SCENARIOS)

@app.route('/api/scenario_data', methods=['GET'])
def get_scenario_data():
    """Returns example text, pattern, labels, and description for a given scenario ID."""
    scenario_id = request.args.get('id')
    scenario = CYBER_SCENARIOS.get(scenario_id)
    if scenario:
        return jsonify({
            'example_text': scenario['example_text'],
            'example_pattern': scenario['example_pattern'],
            'text_label': scenario['text_label'],
            'pattern_label': scenario['pattern_label'],
            'description': scenario['description']
        })
    return jsonify({'error': 'Scenario not found'}), 404

@app.route('/api/search', methods=['POST'])
def search():
    """Handles search requests from the frontend."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        text = data.get('text', '')
        pattern = data.get('pattern', '')
        algorithm_name = data.get('algorithm', 'naive')  # Default to naive
        visualize = data.get('visualize', False)

        # Validate inputs
        if not isinstance(text, str) or not isinstance(pattern, str):
            return jsonify({'error': 'Text and pattern must be strings'}), 400

        # Log the request for debugging
        app.logger.info(f"Search request - Algorithm: {algorithm_name}, Text length: {len(text)}, Pattern length: {len(pattern)}")

        try:
            result = sma.run_algorithm(algorithm_name, text, pattern, visualize=visualize)
            if not isinstance(result, dict):
                return jsonify({'error': f'Invalid result type from algorithm: {type(result)}'}), 500
            return jsonify(result)
        except ValueError as e:
            app.logger.error(f"ValueError in algorithm execution: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            app.logger.error(f"Error in algorithm execution: {str(e)}", exc_info=True)
            return jsonify({'error': f'Algorithm execution failed: {str(e)}'}), 500

    except Exception as e:
        app.logger.error(f"Error in /api/search endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/compare', methods=['POST'])
def compare():
    """Handles comparison requests from the frontend."""
    data = request.get_json()
    text = data.get('text', '')
    pattern = data.get('pattern', '')
    algorithms = data.get('algorithms', None)

    try:
        results = sma.compare_algorithms(text, pattern, algorithms=algorithms)
        return jsonify(results)
    except Exception as e:
        app.logger.error(f"Error in /api/compare: {e}", exc_info=True)
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/api/benchmark', methods=['POST'])
def benchmark():
    """Handles benchmark requests and returns plot data."""
    data = request.get_json()
    pattern_size = int(data.get('pattern_size', 5))
    num_trials = int(data.get('num_trials', 3))
    text_sizes_raw = data.get('text_sizes', [100, 500, 1000, 2000, 5000, 10000])
    text_sizes = [int(s) for s in text_sizes_raw]

    try:
        benchmark_results, sizes = sma.benchmark_algorithms(text_sizes, pattern_size, num_trials)

        plt.figure(figsize=(12, 8))
        sns.set_theme(style="whitegrid") # Apply seaborn style
        
        for alg, times in benchmark_results.items():
            valid_times = [t for t in times if t is not None]
            valid_sizes = [s for i, s in enumerate(sizes) if times[i] is not None]
            if valid_times:
                plt.plot(valid_sizes, valid_times, marker='o', label=alg.upper().replace('_', ' '), linewidth=2)

        plt.xlabel('Text Size (characters)', fontsize=12)
        plt.ylabel('Average Execution Time (seconds)', fontsize=12)
        plt.title('String Matching Algorithms Performance in Cybersecurity', fontsize=14)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.yscale('log') # Log scale is often better for performance plots
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return jsonify({
            'benchmark_results': benchmark_results,
            'text_sizes': sizes,
            'plot_image': plot_base64
        })

    except Exception as e:
        app.logger.error(f"Error in /api/benchmark: {e}", exc_info=True)
        return jsonify({'error': f'An unexpected error occurred during benchmarking: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)