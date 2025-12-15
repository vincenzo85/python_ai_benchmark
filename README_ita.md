Ecco un file `README.md` completo e pronto all'uso. Include le istruzioni per configurare l'ambiente Python, installare Ollama (il server) e scaricare i modelli che hai testato.

***

# 🚀 Local AI Benchmark Tool

Questo script Python esegue un benchmark automatizzato su modelli LLM locali gestiti tramite **Ollama**. Testa le capacità dei modelli in tre aree chiave:
1.  **Logica** (Identificazione di fallacie logiche)
2.  **Matematica** (Probabilità e Teorema di Bayes)
3.  **Coding** (Algoritmi su alberi binari in Python)

## 📋 Prerequisiti

*   **Sistema Operativo**: Linux, macOS o Windows (con WSL2 consigliato).
*   **Python**: Versione 3.8 o superiore.
*   **Ollama**: Il server locale per eseguire i modelli AI.

***

## 🛠️ Installazione

### 1. Installare Ollama
Se non hai ancora installato Ollama, esegui questo comando (per Linux/macOS):

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Dopo l'installazione, avvia il server (se non è già attivo):
```bash
ollama serve
```

### 2. Configurare l'Ambiente Python
È consigliato usare un virtual environment per non sporcare il sistema.

```bash
# Crea il virtual environment
python3 -m venv venv

# Attiva il virtual environment
source venv/bin/activate

# Installa le dipendenze necessarie
# Lo script usa 'requests' per parlare con le API di Ollama
pip install requests
```

***

## 📥 Scaricare i Modelli (Download Models)

Prima di lanciare il benchmark, devi scaricare i modelli che vuoi testare. Ecco i comandi per scaricare i modelli "Vincitori" e quelli usati nel tuo log:

### 🏆 I "Magnifici 4" (Consigliati)
Questi sono i modelli che hanno performato meglio nei test:

```bash
# Llama 3.1 8B (Ottimo per hardware limitato)
ollama pull llama3.1:8b

# Qwen 2.5 Coder 32B (Il migliore per coding e matematica - Richiede ~20GB VRAM)
ollama pull qwen2.5-coder:32b-instruct-q4_K_M

# DeepSeek R1 32B (Modello "Reasoning")
ollama pull deepseek-r1:32b

# Llama 3.2 Vision 11B (Multimodale versatile)
ollama pull llama3.2-vision:11b
```

### 🧪 Altri Modelli dal tuo Benchmark
Se vuoi replicare esattamente il tuo test completo:

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
# ... aggiungi altri modelli se necessario
```

***

## 🚀 Utilizzo

Assicurati che Ollama sia in esecuzione (solitamente sulla porta `11434`).

### Comando Base
Esegue il benchmark su tutti i modelli installati (fino al limite predefinito):

```bash
python3 benchmark.py
```

### Specificare l'URL di Ollama
Se Ollama gira su un altro server (es. `192.168.1.252` come nel tuo caso):

```bash
python3 benchmark.py --ollama http://192.168.1.252:11434
```

### Selezionare Modelli Specifici
Per testare solo una lista specifica di modelli separati da virgola:

```bash
python3 benchmark.py --models "llama3.1:8b,qwen2.5-coder:32b-instruct-q4_K_M"
```

### Aumentare il Limite
Per testare più di 5 modelli (default), usa il flag `--limit`:

```bash
python3 benchmark.py --limit 100
```

***

## 📊 Output dei Risultati

Lo script creerà una cartella `runs_complex/` contenente:
*   `full_responses.txt`: Le risposte complete (testo grezzo) di ogni modello.
*   `benchmark_summary.csv`: Una tabella riassuntiva con i punteggi (Pass/Fail) e le latenze.

Puoi importare il file CSV direttamente in Excel o Google Sheets per l'analisi.
