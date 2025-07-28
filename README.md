markdown
# Ollama Model Benchmark Tool

![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A professional benchmarking tool for evaluating Ollama language models, featuring a PyQt5 GUI with dark theme, concurrent testing capabilities, and comprehensive performance metrics.

![Ollama Benchmark Tool Screenshot](screenshot.png) *(Placeholder - add your screenshot here)*

## Features

- 🚀 **Concurrent Benchmarking** - Test models with up to 10 concurrent requests
- 📊 **Performance Metrics** - Measure:
  - Latency per request
  - Tokens/second
  - Throughput (tasks/second)
  - Total execution time
- 🌙 **Dark Theme UI** - Eye-friendly interface with professional styling
- 🔧 **Customizable Tests**:
  - Select from 100+ diverse prompts
  - Adjust number of tasks (1-200)
  - Control concurrency levels
- 📈 **Results Visualization**:
  - Summary table with aggregate metrics
  - Detailed task-level performance
  - Color-coded performance indicators
- 💾 **Automatic Saving** - Results exported to JSON on exit

## Installation

1. **Prerequisites**:
   - Python 3.7+
   - Ollama running locally (`http://localhost:11434`)
   - Installed Ollama models

2. **Install dependencies**:
```bash
pip install PyQt5 requests
Run the application:

bash
python app.py
Usage
Select a model from the dropdown (refresh if needed)

Set task count (default: 100 tasks)

Click Start Benchmark

View real-time progress in status bar

Analyze results in summary and details tabs

💡 The tool automatically runs warm-up iterations before benchmarking for accurate results

Configuration
Modify these constants in app.py for customization:

python
OLLAMA_HOST = "http://localhost:11434"  # Change if using remote instance
WARMUP_RUNS = 1                         # Initial warm-up iterations
CONCURRENCY_LEVEL = 10                  # Max concurrent requests
BENCHMARK_PROMPTS = [...]               # Edit to customize test prompts
Technical Details
Concurrency Model: Uses ThreadPoolExecutor for parallel requests

Metrics Collected:

API Latency

Evaluation Duration

Token Count

Tokens/Second

Error Handling: Comprehensive error reporting with UI notifications

Data Persistence: JSON auto-save on exit with timestamped filenames

FAQ
Q: Why am I getting "No models found" error?
A: Ensure Ollama is running and models are installed. Check connection to OLLAMA_HOST.

Q: Can I test remote Ollama instances?
A: Yes! Modify OLLAMA_HOST in the code to point to your remote instance.

Q: How are tokens/second calculated?
A: Calculated using Ollama's eval_count and eval_duration from API response.

Contributing
Contributions are welcome! Please open an issue or PR for:

Bug reports

Feature requests

Performance improvements

Additional test prompts

License
This project is licensed under the MIT License - see the LICENSE file for details.

Optimize your language model selection with data-driven performance metrics!

text

Key elements included:
1. Professional badges for Python/PyQt5 versions and license
2. Clear feature list with emoji visual markers
3. Step-by-step installation/usage instructions
4. Configuration section for advanced users
5. Technical implementation details
6. FAQ for common troubleshooting
7. Contribution guidelines
8. License information

To complete the README:
1. Add a screenshot named `screenshot.png` in your repo
2. Create a `LICENSE` file with MIT license text
3. Adjust any configuration details specific to your environment

The README is optimized for GitHub with proper markdown formatting, clear section organization, and emoji-enhanced readability.
