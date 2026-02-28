# Ollama Setup Guide

This guide explains how to install and configure Ollama with the Mistral 7B model for the Nyaya Mitra platform.

## What is Ollama?

Ollama is a tool that allows you to run large language models locally on your machine. It provides a simple API for interacting with models like Mistral, Llama, and others.

## Installation

### Windows

1. Download Ollama for Windows from the official website:
   - Visit: https://ollama.ai/download
   - Download the Windows installer
   - Run the installer and follow the prompts

2. Verify installation:
   ```cmd
   ollama --version
   ```

### macOS

1. Download Ollama for macOS:
   - Visit: https://ollama.ai/download
   - Download the macOS installer
   - Open the downloaded file and drag Ollama to Applications

2. Verify installation:
   ```bash
   ollama --version
   ```

### Linux

1. Install using the install script:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. Verify installation:
   ```bash
   ollama --version
   ```

## Download Mistral 7B Model

After installing Ollama, download the Mistral 7B model:

```bash
ollama pull mistral:7b
```

This will download the Mistral 7B model (approximately 4.1 GB). The download may take several minutes depending on your internet connection.

## Verify Model Installation

Check that the model is available:

```bash
ollama list
```

You should see `mistral:7b` in the list of available models.

## Start Ollama Service

Ollama runs as a background service. To ensure it's running:

### Windows
Ollama should start automatically after installation. If not, search for "Ollama" in the Start menu and launch it.

### macOS
Ollama should start automatically. You can also start it from Applications.

### Linux
Start the Ollama service:
```bash
ollama serve
```

## Test the Installation

Test that Ollama is working correctly:

```bash
ollama run mistral:7b "Hello, how are you?"
```

You should see a response from the model.

## Configuration for Nyaya Mitra

The Nyaya Mitra backend is configured to connect to Ollama at `http://localhost:11434` by default.

If you need to use a different URL, set the `OLLAMA_BASE_URL` environment variable in your `.env` file:

```env
OLLAMA_BASE_URL=http://localhost:11434
```

## Testing the Integration

To test the Ollama integration with the backend:

```bash
cd backend
python -m pytest test_ollama_client.py -v
```

All tests should pass (they use mocks, so Ollama doesn't need to be running for tests).

## Troubleshooting

### Ollama service not running
- **Windows**: Check if Ollama is running in the system tray. If not, launch it from the Start menu.
- **macOS**: Check if Ollama is running in the menu bar. If not, launch it from Applications.
- **Linux**: Run `ollama serve` to start the service.

### Model not found
If you get a "model not found" error, ensure you've pulled the model:
```bash
ollama pull mistral:7b
```

### Connection refused
If you get a connection error, ensure Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

This should return a JSON response with available models.

### Port already in use
If port 11434 is already in use, you can configure Ollama to use a different port by setting the `OLLAMA_HOST` environment variable before starting Ollama:
```bash
export OLLAMA_HOST=0.0.0.0:11435
ollama serve
```

Then update your `.env` file:
```env
OLLAMA_BASE_URL=http://localhost:11435
```

## Performance Considerations

- **RAM**: Mistral 7B requires at least 8GB of RAM. 16GB is recommended for better performance.
- **GPU**: Ollama will automatically use GPU acceleration if available (NVIDIA CUDA or Apple Metal).
- **Response Time**: First request may be slower as the model loads into memory. Subsequent requests will be faster.

## Alternative Models

If Mistral 7B is too large for your system, you can use smaller models:

```bash
# Mistral 7B Instruct (optimized for instructions)
ollama pull mistral:7b-instruct

# Llama 2 7B (alternative model)
ollama pull llama2:7b

# Phi-2 (smaller, faster model)
ollama pull phi:2.7b
```

Update the model name in the backend code if using a different model.

## Resources

- Ollama Documentation: https://github.com/ollama/ollama
- Mistral AI: https://mistral.ai/
- Model Library: https://ollama.ai/library
