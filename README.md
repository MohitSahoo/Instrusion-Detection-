# 🛡️ Cyber Security Analysis Platform

A unified web application that combines **Intrusion Detection System** and **String Matching Algorithms** for cybersecurity analysis, all running on a single port.

## 🚀 Features

### 🔍 Intrusion Detection System

- **Real-time log analysis** with multiple string matching algorithms
- **File upload capability** for log files (.log, .txt)
- **Multiple algorithm support**: Naive, Horspool, Boyer-Moore
- **Detailed detection results** with step-by-step algorithm visualization
- **Performance metrics** and execution time tracking

### 🔗 String Matching Algorithms

- **Interactive algorithm visualization** with step-by-step analysis
- **Multiple algorithm comparison** (Naive, Boyer-Moore, Horspool)
- **Performance benchmarking** with scalability analysis
- **Attack pattern detection** with pre-defined security patterns
- **Real-time pattern matching** with visual feedback

### 🔄 Integration Features

- **Seamless navigation** between both applications
- **Text sharing** from intrusion detection to string matching
- **Attack pattern dropdown** with common security patterns
- **Smart pattern suggestions** based on loaded text
- **Unified interface** running on a single port

## 📋 Prerequisites

- Python 3.7+
- pip (Python package installer)

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   cd "/Users/aamiribrahim/Downloads/DAA lab el togther"
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements_unified.txt
   ```

## 🚀 Quick Start

1. **Run the unified application**
   ```bash
   python unified_app.py
   ```
2. **Access the application**
   - **Main Page**: http://localhost:5000
   - **Intrusion Detection**: http://localhost:5000/intrusion-detection
   - **String Matching**: http://localhost:5000/string-matching

## 📁 Project Structure

```
DAA lab el togther/
├── unified_app.py              # Main unified application
├── requirements_unified.txt    # Python dependencies
├── README.md                   # This file
├── templates/                  # HTML templates
│   ├── unified_index.html     # Main landing page
│   ├── intrusion_detection.html
│   └── string_matching.html
├── static/                     # CSS, JS, and other static files
│   ├── css/
│   └── js/
├── intrusion-detection-web/    # Original intrusion detection app
│   ├── app.py
│   ├── backend.py
│   └── templates/
└── string_match/              # Original string matching app
    ├── app.py
    ├── string_matching_algorithms.py
    └── templates/
```

## 🎯 How to Use

### Intrusion Detection

1. Navigate to `/intrusion-detection`
2. Enter log entries or upload a log file
3. Select an algorithm (Naive, Horspool, Boyer-Moore)
4. Click "🔍 Detect Intrusions"
5. View detailed results with algorithm steps

### String Matching

1. Navigate to `/string-matching`
2. Enter text to analyze
3. Choose a pattern or select from attack patterns dropdown
4. Select an algorithm and run analysis
5. View step-by-step visualization and results

### Integration Workflow

1. Start with intrusion detection and enter log data
2. Click "🔗 Open String Matching Analysis" to send text to string matching
3. Use the attack pattern dropdown to select security patterns
4. Compare different algorithms and view performance benchmarks

## 🔧 Supported Algorithms

### String Matching Algorithms

- **Naive Search**: Simple pattern matching
- **Boyer-Moore**: Efficient with bad character rule
- **Horspool**: Simplified Boyer-Moore variant

### Attack Patterns Detected

- SQL Injection: `' OR '1'='1`, `'--`
- XSS: `<script>`
- Path Traversal: `../../`
- Command Injection: `wget`, `curl`, `nc`

## 🔧 Troubleshooting

### Import Errors

- Ensure you're in the correct directory
- Verify all subdirectories (`intrusion-detection-web`, `string_match`) are present
- Check that all dependencies are installed

### Port Already in Use

- The application runs on port 5000 by default
- If the port is busy, modify the port in `unified_app.py`

## 📝 License

This project is created for educational purposes in the context of DAA (Design and Analysis of Algorithms) lab work.


# How to Run this Project

cd "/Users/aamiribrahim/Downloads/DAA lab el togther"

-> Install dependencies (one-time setup)
pip install -r requirements_unified.txt

-> Run the app
python unified_app.py

-> Access in browser
-> http://localhost:5000

---

**🚀 Happy analyzing!** 🛡️
