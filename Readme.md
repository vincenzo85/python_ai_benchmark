***

# 🚀 Local AI Benchmark Tool

This Python script performs an automated benchmark on local LLMs managed via **Ollama**. It tests model capabilities across three key pillars:
1.  **Logic** (Identifying logical fallacies)
2.  **Math** (Probability and Bayes' Theorem)
3.  **Coding** (Binary tree algorithms in Python)

## 📋 Prerequisites

*   **OS**: Linux, macOS, or Windows (WSL2 recommended).
*   **Python**: Version 3.8 or higher.
*   **Ollama**: The local server to run the AI models.

***

## 🛠️ Installation

### 1. Install Ollama
If you haven't installed Ollama yet, run this command (Linux/macOS):

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

After installation, start the server (if not already running):
```bash
ollama serve
```

### 2. Configure Python Environment
It is recommended to use a virtual environment to manage dependencies.

```bash
# Create the virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required dependencies
# The script uses 'requests' to talk to the Ollama API
pip install requests
```

***

## 📥 Download Models

Before running the benchmark, you must download the models you wish to test. Here are the commands to download the "Winners" (based on your analysis) and others used in the logs:

### 🏆 The "Magnificent 4" (Recommended)
These models performed best in the Logic, Math, and Coding tests:

```bash
# Llama 3.1 8B (Best for limited hardware)
ollama pull llama3.1:8b

# Qwen 2.5 Coder 32B (Best for Coding & Math - Requires ~20GB VRAM)
ollama pull qwen2.5-coder:32b-instruct-q4_K_M

# DeepSeek R1 32B ("Reasoning" model)
ollama pull deepseek-r1:32b

# Llama 3.2 Vision 11B (Versatile Multimodal)
ollama pull llama3.2-vision:11b
```

### 🧪 Other Models (from your logs)
To replicate your full benchmark run:

```bash
ollama pull sushruth/solar-uncensored
ollama pull jean-luc/cydonia:22b-v1.1-q5_K_M
ollama pull llama3:8b
ollama pull deepseek-coder:6.7b
ollama pull llava:7b
ollama pull gpt-oss:20b
ollama pull granite3.3:latest
ollama pull dolphin-llama3:latest
ollama pull deepseek-r1:8b
# ... add other models as needed
```

***

## 🚀 Usage

Ensure Ollama is running (default port `11434`).

### Basic Run
Benchmarks all installed models (up to the default limit):

```bash
python3 benchmark.py
```

### Specify Ollama URL
If Ollama is running on a different server (e.g., `192.168.1.252`):

```bash
python3 benchmark.py --ollama http://192.168.1.252:11434
```

### Select Specific Models
To test only a specific comma-separated list of models:

```bash
python3 benchmark.py --models "llama3.1:8b,qwen2.5-coder:32b-instruct-q4_K_M"
```

### Increase Limit
To test more than the default 5 models, use the `--limit` flag:

```bash
python3 benchmark.py --limit 100
```

***

## 📊 Results Output

The script creates a directory named `runs_complex/` containing:
*   `full_responses.txt`: The raw text responses from every model.
*   `benchmark_summary.csv`: A summary table with Pass/Fail scores and latency metrics.

You can import the CSV file directly into Excel or Google Sheets for analysis.
