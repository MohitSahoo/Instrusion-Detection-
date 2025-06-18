// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('textInput');
    const patternInput = document.getElementById('patternInput');
    const textLabel = document.getElementById('textLabel'); // New
    const patternLabel = document.getElementById('patternLabel'); // New
    const algorithmSelect = document.getElementById('algorithmSelect');
    const visualizeCheckbox = document.getElementById('visualizeCheckbox');
    const analyzeButton = document.getElementById('analyzeButton');
    const compareAllButton = document.getElementById('compareAllButton');
    const resultsOutput = document.getElementById('resultsOutput');

    const visualizationSection = document.querySelector('.visualization-section');
    const visualAlgoName = document.getElementById('visualAlgoName');
    const textDisplay = document.getElementById('textDisplay');
    const patternDisplay = document.getElementById('patternDisplay');
    const messageDisplay = document.getElementById('messageDisplay');
    const extraInfo = document.getElementById('extraInfo');
    const matchesDisplay = document.getElementById('matchesDisplay');

    const prevFrameButton = document.getElementById('prevFrame');
    const nextFrameButton = document.getElementById('nextFrame');
    const frameCounter = document.getElementById('frameCounter');
    const playPauseButton = document.getElementById('playPause');
    const speedSlider = document.getElementById('speedSlider');

    const runBenchmarkButton = document.getElementById('runBenchmarkButton');
    const benchmarkPatternSize = document.getElementById('benchmarkPatternSize');
    const benchmarkNumTrials = document.getElementById('benchmarkNumTrials');
    const benchmarkOutput = document.getElementById('benchmarkOutput');
    const benchmarkPlot = document.getElementById('benchmarkPlot');

    const scenarioSelect = document.getElementById('scenarioSelect'); // New
    const scenarioDescription = document.getElementById('scenarioDescription'); // New

    let visualizationFrames = [];
    let currentFrameIndex = 0;
    let animationInterval = null;
    let isPlaying = false;

    // --- Core Logic ---

    async function analyzeText(compareAll = false) {
        resultsOutput.textContent = 'Analyzing...';
        visualizationSection.style.display = 'none';
        resetVisualization();

        const text = textInput.value;
        const pattern = patternInput.value;
        const algorithm = algorithmSelect.value;
        const visualize = true; // Always visualize

        // Pattern is required for search unless it's a comparison where pattern might be empty for some Z-algo cases
        if (!text || (!pattern && !compareAll)) {
            resultsOutput.textContent = 'Error: Text and Pattern (for single algorithm analysis) cannot be empty.';
            return;
        }

        const endpoint = compareAll ? '/api/compare' : '/api/search';
        const payload = compareAll ? { text, pattern } : { text, pattern, algorithm, visualize };

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            // Check if response is ok before trying to parse JSON
            if (!response.ok) {
                const errorText = await response.text();
                let errorMessage;
                try {
                    const errorJson = JSON.parse(errorText);
                    errorMessage = errorJson.error || 'Unknown server error';
                } catch (e) {
                    errorMessage = `Server error (${response.status}): ${errorText}`;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            
            if (data.error) {
                resultsOutput.textContent = `Error: ${data.error}`;
                console.error('API Error:', data.error);
                return;
            }

            if (compareAll) {
                displayComparisonResults(data);
            } else {
                displaySingleAlgorithmResult(data);
                if (data.visualization_frames && data.visualization_frames.length > 0) {
                    visualizationFrames = data.visualization_frames;
                    visualizationSection.style.display = 'block';
                    setupVisualizationControls();
                    displayFrame(0);
                    
                    // Scroll to visualization section
                    visualizationSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        } catch (error) {
            resultsOutput.textContent = `Error: ${error.message}`;
            console.error('Search error:', error);
            // Clear any previous visualization
            resetVisualization();
        }
    }

    function displaySingleAlgorithmResult(result) {
        let output = `--- ${result.algorithm.replace('_', ' ').toUpperCase()} Results ---\n`;
        output += `Matches found: ${result.matches ? result.matches.length : 0}\n`;
        if (result.matches && result.matches.length > 0) {
            output += `Positions: ${result.matches.join(', ')}\n`;
        }
        output += `Execution Time: ${result.execution_time ? result.execution_time.toFixed(6) : 'N/A'} seconds\n`;
        
        // Add a note about visualization
        if (result.visualization_frames && Array.isArray(result.visualization_frames) && result.visualization_frames.length > 0) {
            output += `\nVisualization available: ${result.visualization_frames.length} steps to show the algorithm's operation.\n`;
            output += `Use the controls below to step through the visualization.\n`;
        } else {
            output += `\nNo visualization available for this run.\n`;
        }
        
        resultsOutput.textContent = output;
    }

    function displayComparisonResults(results) {
        let output = '--- Comparison Results ---\n';
        output += `Algorithm       Matches   Time (s)\n`; // Removed Complexity and Comparisons columns
        output += `------------------------------------\n`;
        for (const algKey in results) {
            const result = results[algKey];
            output += `${result.algorithm.replace('_', ' ').padEnd(15)} ${String(result.matches.length).padEnd(9)} ${result.execution_time.toFixed(6)}\n`;
        }
        resultsOutput.textContent = output;
    }

    // --- Visualization Logic ---

    function resetVisualization() {
        visualizationFrames = [];
        currentFrameIndex = 0;
        clearInterval(animationInterval);
        isPlaying = false;
        playPauseButton.textContent = 'Play';
        textDisplay.innerHTML = '';
        patternDisplay.innerHTML = '';
        messageDisplay.textContent = '';
        extraInfo.innerHTML = '';
        matchesDisplay.textContent = 'Matches found: ';
        frameCounter.textContent = '0 / 0';
        prevFrameButton.disabled = true;
        nextFrameButton.disabled = true;
        playPauseButton.disabled = true;
    }

    function setupVisualizationControls() {
        if (!visualizationFrames || !Array.isArray(visualizationFrames)) {
            console.error('Invalid visualization frames data');
            resetVisualization();
            return;
        }

        const frameCount = visualizationFrames.length;
        if (frameCount === 0) {
            console.error('No visualization frames available');
            resetVisualization();
            return;
        }

        frameCounter.textContent = `1 / ${frameCount}`;
        prevFrameButton.disabled = true;
        nextFrameButton.disabled = frameCount <= 1;
        playPauseButton.disabled = frameCount <= 1;
        
        // Update the algorithm name with a more descriptive title
        const algoName = algorithmSelect.options[algorithmSelect.selectedIndex].text;
        visualAlgoName.textContent = `${algoName} Algorithm Visualization`;
        
        // Add keyboard controls
        document.addEventListener('keydown', handleVisualizationKeyPress);
    }

    function handleVisualizationKeyPress(event) {
        if (!visualizationSection.style.display || visualizationSection.style.display === 'none') {
            return;
        }
        
        // Only handle shortcuts if not typing in an input or textarea
        const tag = event.target.tagName.toLowerCase();
        if (tag === 'input' || tag === 'textarea') {
            return;
        }
        
        switch(event.key) {
            case 'ArrowLeft':
                if (!prevFrameButton.disabled) {
                    displayFrame(currentFrameIndex - 1);
                }
                break;
            case 'ArrowRight':
                if (!nextFrameButton.disabled) {
                    displayFrame(currentFrameIndex + 1);
                }
                break;
            case ' ':
                event.preventDefault();
                if (!playPauseButton.disabled) {
                    togglePlayPause();
                }
                break;
        }
    }

    function displayFrame(index) {
        if (!visualizationFrames || !Array.isArray(visualizationFrames)) {
            console.error('Invalid visualization frames data');
            resetVisualization();
            return;
        }

        if (index < 0 || index >= visualizationFrames.length) {
            console.error(`Invalid frame index: ${index}`);
            return;
        }

        currentFrameIndex = index;
        const frame = visualizationFrames[currentFrameIndex];
        if (!frame) {
            console.error(`Invalid frame data at index ${index}`);
            return;
        }

        frameCounter.textContent = `${currentFrameIndex + 1} / ${visualizationFrames.length}`;

        prevFrameButton.disabled = currentFrameIndex === 0;
        nextFrameButton.disabled = currentFrameIndex === visualizationFrames.length - 1;
        if (isPlaying && currentFrameIndex === visualizationFrames.length - 1) {
            clearInterval(animationInterval);
            isPlaying = false;
            playPauseButton.textContent = 'Play';
        }

        // Update message with more descriptive text
        let message = frame.message || '';
        messageDisplay.textContent = message;

        // Update matches display
        if (frame.matches && Array.isArray(frame.matches)) {
            matchesDisplay.textContent = `Matches found: ${frame.matches.join(', ')}`;
        } else {
            matchesDisplay.textContent = 'Matches found: ';
        }

        // Update text and pattern displays with highlighting
        if (frame.text && frame.pattern) {
            textDisplay.innerHTML = highlightString(
                frame.text,
                frame.text_idx,
                frame.pattern_idx,
                frame.type,
                frame.current_window,
                frame.matches || [],
                frame.text
            );
            patternDisplay.innerHTML = highlightString(
                frame.pattern,
                frame.pattern_idx,
                frame.text_idx,
                frame.type,
                frame.current_window,
                [],
                frame.pattern
            );
        } else {
            textDisplay.innerHTML = '';
            patternDisplay.innerHTML = '';
        }

        // Update extra info if available
        if (frame.bad_char_table || frame.shift_table) {
            let extraInfoHtml = '<div class="extra-info-content">';
            if (frame.bad_char_table) {
                extraInfoHtml += '<div class="table-info">';
                extraInfoHtml += '<h4>Bad Character Table:</h4>';
                extraInfoHtml += '<table><tr><th>Character</th><th>Last Position</th></tr>';
                for (const [char, pos] of Object.entries(frame.bad_char_table)) {
                    extraInfoHtml += `<tr><td>${char}</td><td>${pos}</td></tr>`;
                }
                extraInfoHtml += '</table></div>';
            }
            if (frame.shift_table) {
                extraInfoHtml += '<div class="table-info">';
                extraInfoHtml += '<h4>Shift Table:</h4>';
                extraInfoHtml += '<table><tr><th>Character</th><th>Shift Value</th></tr>';
                for (const [char, shift] of Object.entries(frame.shift_table)) {
                    if (shift !== frame.pattern.length) { // Only show relevant entries
                        extraInfoHtml += `<tr><td>${char}</td><td>${shift}</td></tr>`;
                    }
                }
                extraInfoHtml += '</table></div>';
            }
            extraInfoHtml += '</div>';
            extraInfo.innerHTML = extraInfoHtml;
        } else {
            extraInfo.innerHTML = '';
        }
    }

    function highlightString(str, primaryIdx, secondaryIdx, frameType, currentWindow, matches, originalFullString) {
        let highlightedHtml = '';
        let patternLength = patternInput.value.length;

        for (let i = 0; i < str.length; i++) {
            let char = str[i];
            let classes = [];

            // Highlight matches if applicable
            if (matches && originalFullString === textInput.value) {
                for (const matchPos of matches) {
                    if (i >= matchPos && i < matchPos + patternLength) {
                        classes.push('char-highlight-match');
                    }
                }
            }
            
            // Current window / alignment
            if ((frameType === 'alignment' || frameType === 'rolling_hash' || frameType === 'false_positive' || frameType === 'mismatch_shift') && currentWindow) {
                let windowStart = primaryIdx;
                if (str === patternInput.value) {
                    windowStart = 0;
                }

                if (i >= windowStart && i < windowStart + currentWindow.length) {
                    if (!classes.includes('char-highlight-match')) {
                        classes.push('char-highlight-window');
                    }
                }
            }

            // Comparison points
            if (frameType === 'comparison' || frameType === 'mismatch_shift' || frameType === 'character_check' ) {
                if (i === primaryIdx) {
                    if (frame.match_status !== undefined) {
                        classes.push(frame.match_status ? 'char-highlight-current-match' : 'char-highlight-mismatch');
                    } else {
                        classes.push('char-highlight-current');
                    }
                } else if (i === secondaryIdx && secondaryIdx !== -1) {
                    classes.push('char-highlight-current');
                }
            }
            
            // For KMP's LPS array visualization or Z-algorithm's Z-array computation
            if ((frameType.startsWith('lps_') || frameType.startsWith('z_')) && str === originalFullString) {
                if (frame.current_i !== undefined && i === frame.current_i) {
                     classes.push('char-highlight-current');
                }
            }

            // For Z-algo specific highlighting
            if (frameType.startsWith('z_') && str === frame.combined_string) {
                if (frame.l !== undefined && frame.r !== undefined) {
                    if (i >= frame.l && i <= frame.r) {
                        classes.push('char-highlight-z-box'); // Highlight current Z-box
                    }
                }
                if (frame.current_i !== undefined && i === frame.current_i) {
                    classes.push('char-highlight-current'); // Current index being processed
                }
            }

            if (classes.length > 0) {
                classes = [...new Set(classes)];
                highlightedHtml += `<span class="${classes.join(' ')}">${char}</span>`;
            } else {
                highlightedHtml += char;
            }
        }
        return highlightedHtml;
    }


    function togglePlayPause() {
        if (isPlaying) {
            clearInterval(animationInterval);
            playPauseButton.textContent = 'Play';
        } else {
            if (currentFrameIndex === visualizationFrames.length - 1) {
                currentFrameIndex = 0; // Restart if at end
            }
            animationInterval = setInterval(() => {
                if (currentFrameIndex < visualizationFrames.length - 1) {
                    currentFrameIndex++;
                    displayFrame(currentFrameIndex);
                } else {
                    clearInterval(animationInterval);
                    isPlaying = false;
                    playPauseButton.textContent = 'Play';
                }
            }, Math.max(50, 2000 - speedSlider.value)); // Speed inversely proportional to slider value, min 50ms
            playPauseButton.textContent = 'Pause';
        }
        isPlaying = !isPlaying;
    }

    // --- Benchmark Logic ---

    async function runBenchmark() {
        benchmarkOutput.textContent = 'Running benchmark... This might take a moment (especially for larger data sizes).';
        benchmarkPlot.innerHTML = ''; // Clear previous plot

        const textSizes = [100, 500, 1000, 2000, 5000, 10000, 20000];
        const patternSize = parseInt(benchmarkPatternSize.value);
        const numTrials = parseInt(benchmarkNumTrials.value);

        if (isNaN(patternSize) || patternSize < 1 || isNaN(numTrials) || numTrials < 1) {
             benchmarkOutput.textContent = 'Error: Pattern size and number of trials must be valid positive numbers.';
             return;
        }

        try {
            const response = await fetch('/api/benchmark', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text_sizes: textSizes, pattern_size: patternSize, num_trials: numTrials })
            });
            const data = await response.json();

            if (data.error) {
                benchmarkOutput.textContent = `Error: ${data.error}`;
                return;
            }

            displayBenchmarkResults(data);
            if (data.plot_image) {
                benchmarkPlot.innerHTML = `<img src="data:image/png;base64,${data.plot_image}" alt="Benchmark Plot">`;
            }

        } catch (error) {
            benchmarkOutput.textContent = `Network error: ${error.message}`;
            console.error('Fetch error:', error);
        }
    }

    function displayBenchmarkResults(data) {
        let output = `--- Benchmark Results (Average execution time in seconds, Signature/Pattern Size: ${benchmarkPatternSize.value}) ---\n`;
        output += `Algorithm       `;
        data.text_sizes.forEach(size => {
            output += `${String(size).padEnd(10)}`;
        });
        output += `\n`;
        output += `-`.repeat(15 + data.text_sizes.length * 10) + `\n`;

        for (const algKey in data.benchmark_results) {
            const times = data.benchmark_results[algKey];
            output += `${algKey.replace('_', ' ').padEnd(15)}`;
            times.forEach(time => {
                output += `${time.toFixed(6).padEnd(10)}`;
            });
            output += `\n`;
        }
        benchmarkOutput.textContent = output;
    }

    // --- New Cyber Scenario Logic ---
    async function loadScenario(scenarioId) {
        try {
            const response = await fetch(`/api/scenario_data?id=${scenarioId}`);
            const data = await response.json();
            if (data.error) {
                console.error("Error loading scenario:", data.error);
                return;
            }
            textInput.value = data.example_text;
            patternInput.value = data.example_pattern;
            textLabel.textContent = data.text_label + ':';
            patternLabel.textContent = data.pattern_label + ':';
            scenarioDescription.innerHTML = `<strong>Description:</strong> ${data.description}`;
        } catch (error) {
            console.error("Failed to fetch scenario data:", error);
            // Fallback to default if fetch fails
            textInput.value = 'The quick brown fox jumps over the lazy dog. A quick fox is hard to catch.';
            patternInput.value = 'quick fox';
            textLabel.textContent = 'Text (e.g., File Content, Network Traffic):';
            patternLabel.textContent = 'Pattern (e.g., Malware Signature, Exploit String):';
            scenarioDescription.textContent = 'Error loading scenario description. Using generic example.';
        }
    }


    // --- Event Listeners ---

    analyzeButton.addEventListener('click', () => analyzeText(false));
    compareAllButton.addEventListener('click', () => analyzeText(true));
    prevFrameButton.addEventListener('click', () => displayFrame(currentFrameIndex - 1));
    nextFrameButton.addEventListener('click', () => displayFrame(currentFrameIndex + 1));
    playPauseButton.addEventListener('click', togglePlayPause);
    speedSlider.addEventListener('input', () => {
        if (isPlaying) {
            clearInterval(animationInterval);
            animationInterval = setInterval(() => {
                if (currentFrameIndex < visualizationFrames.length - 1) {
                    currentFrameIndex++;
                    displayFrame(currentFrameIndex);
                } else {
                    clearInterval(animationInterval);
                    isPlaying = false;
                    playPauseButton.textContent = 'Play';
                }
            }, Math.max(50, 2000 - speedSlider.value));
        }
    });

    runBenchmarkButton.addEventListener('click', runBenchmark);

    // New event listener for scenario selection
    scenarioSelect.addEventListener('change', (event) => {
        loadScenario(event.target.value);
    });


    // Initial state setup:
    // Load the default (generic) scenario when the page loads
    loadScenario(scenarioSelect.value);
    resetVisualization();
});