# Pet Description Utility

A Python utility for analyzing pet images and generating detailed descriptions using vision-language models via Ollama. Supports LLaVA and Qwen-VL.

## Features

- Analyze pet images using state-of-the-art vision-language models
- Support for multiple LLM engines: LLaVA and Qwen-VL
- **Multi-language support**: English and Hebrew
- **Web-based UI** for easy image upload and parameter configuration
- Flexible image input formats (file path, bytes, PIL Image)
- Configurable parameters via JSON file or function arguments
- Configurable parameters for temperature, max tokens, and custom prompts
- Easy integration with Ollama API

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Ollama** installed and running locally
   - Download from: https://ollama.ai
   - Installation instructions: https://github.com/ollama/ollama

3. **Vision models** pulled in Ollama:
   ```bash
   ollama pull llava
   ollama pull qwen3-vl
   ```

## Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd pet_description
   ```

2. **Activate the virtual environment (if using one):**
   ```bash
   source env/bin/activate  # On macOS/Linux
   # or
   env\Scripts\activate  # On Windows
   ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure Ollama is running:**
   ```bash
   ollama serve
   ```
   Or start it as a service (varies by OS).

5. **Configure parameters (optional):**
   Edit `params.json` to set default parameters:
   ```json
   {
     "llm_engine": "llava",
     "language": "english",
     "ollama_base_url": "http://localhost:11434",
     "temperature": 0.7,
     "max_tokens": 512,
     "prompt": null
   }
   ```
   If `prompt` is `null`, a language-specific default prompt will be used.

## Usage

### Web Interface (Recommended)

The easiest way to use the utility is through the web interface:

1. **Start the web server:**
   ```bash
   python app.py
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

3. **Use the interface:**
   - Upload a pet image (drag & drop or click to select)
   - Configure parameters (LLM engine, language, temperature, etc.)
   - Click "Generate Description"
   - View the results in the browser

The web interface provides:
- Easy image upload with drag & drop support
- Real-time image preview
- All parameter controls in one place
- Beautiful, responsive design
- Clear error messages and loading indicators

### Python API Usage

### Basic Usage

**Option 1: Using params.json (recommended)**
```python
from pet_description import describe_pet

# Parameters are automatically loaded from params.json
result = describe_pet('path/to/pet_image.jpg')

if result['success']:
    print(f"Language: {result['language_used']}")
    print(result['description'])
else:
    print(f"Error: {result['error']}")
```

**Option 2: Passing parameters directly**
```python
from pet_description import describe_pet

params = {
    'llm_engine': 'llava',  # Options: 'llava', 'qwen-vl'
    'language': 'english'    # Options: 'english', 'hebrew'
}

result = describe_pet('path/to/pet_image.jpg', params)

if result['success']:
    print(result['description'])
else:
    print(f"Error: {result['error']}")
```

### Advanced Usage with Custom Parameters

```python
from pet_description import describe_pet
from PIL import Image

# Load image
img = Image.open('pet.jpg')

# Custom parameters (overrides params.json)
    params = {
        'llm_engine': 'llava',
        'language': 'english',  # or 'hebrew'
        'prompt': 'Describe this pet focusing on its breed, colors, and personality traits.',
        'temperature': 0.8,
        'max_tokens': 1024,
        'ollama_base_url': 'http://localhost:11434'  # Default, can be customized
    }

result = describe_pet(img, params)

if result['success']:
    print(f"Model: {result['model_used']}")
    print(f"Language: {result['language_used']}")
    print(f"Description: {result['description']}")
```

### Using Hebrew Language

```python
from pet_description import describe_pet

params = {
    'llm_engine': 'llava',
    'language': 'hebrew'
}

result = describe_pet('pet.jpg', params)

if result['success']:
    print(result['description'])  # Description will be in Hebrew
```

### Command Line Usage

```bash
python pet_description.py <image_path> [OPTIONS]
```

**Options:**
- `--llm_engine`: LLM engine to use (`llava`, `qwen-vl`)
- `--language`: Language for the prompt (`english`, `hebrew`)
- `--temperature`: Temperature for generation (default: 0.7)
- `--max_tokens`: Maximum tokens to generate (default: 512)
- `--prompt`: Custom prompt for the model
- `--ollama_base_url`: Base URL for Ollama API (default: http://localhost:11434)
- `-h, --help`: Show help message

**Examples:**
```bash
# Uses params.json for all parameters
python pet_description.py pet.jpg

# Override model and language
python pet_description.py pet.jpg --llm_engine llava --language english
python pet_description.py pet.jpg --llm_engine qwen-vl --language hebrew

# Override multiple parameters
python pet_description.py pet.jpg --llm_engine llava --temperature 0.8 --max_tokens 1024

# Use custom prompt
python pet_description.py pet.jpg --llm_engine llava --prompt "Describe this pet's personality"

# Show help
python pet_description.py --help
```

## API Reference

### `describe_pet(image, params)`

Analyzes a pet image and returns information about the pet.

**Parameters:**

- `image` (Union[str, Path, bytes, Image.Image]): Pet image input
  - Can be a file path (str or Path)
  - Image bytes
  - PIL Image object

- `params` (Dict[str, Any], optional): Configuration dictionary. If `None`, parameters are loaded from `params.json`. Parameters passed here override those in `params.json`:
  - `llm_engine` (str, **required**): Model to use
    - Options: `'llava'`, `'qwen-vl'`
  - `language` (str, optional): Language for the prompt
    - Options: `'english'`, `'hebrew'`
    - Default: `'english'`
  - `ollama_base_url` (str, optional): Base URL for Ollama API
    - Default: `'http://localhost:11434'`
  - `prompt` (str, optional): Custom prompt for the model
    - If `None`, uses language-specific default prompt
  - `temperature` (float, optional): Temperature for generation
    - Default: `0.7`
  - `max_tokens` (int, optional): Maximum tokens to generate
    - Default: `512`

**Returns:**

- `Dict[str, Any]`: Result dictionary containing:
  - `success` (bool): Whether the operation was successful
  - `description` (str): Generated description of the pet (if successful)
  - `model_used` (str): Model that was used
  - `language_used` (str): Language that was used
  - `error` (str, optional): Error message (if success is False)
  - `full_response` (dict, optional): Full Ollama API response (if successful)

## Configuration File (params.json)

The `params.json` file allows you to set default parameters that will be used when calling `describe_pet()` without explicitly passing parameters. The file structure is:

```json
{
  "llm_engine": "llava",
  "language": "english",
  "ollama_base_url": "http://localhost:11434",
  "temperature": 0.7,
  "max_tokens": 512,
  "prompt": null
}
```

**Parameter precedence:**
1. Parameters passed directly to `describe_pet()` (highest priority)
2. Parameters from `params.json`
3. Default values (lowest priority)

**Note:** If `prompt` is set to `null`, the system will use a language-specific default prompt based on the `language` parameter.

### Loading Parameters Programmatically

You can also load parameters from a JSON file programmatically:

```python
from pet_description import load_params, describe_pet

# Load parameters from a custom JSON file
params = load_params('my_custom_params.json')
result = describe_pet('pet.jpg', params)
```

## Supported Models

### LLaVA (Large Language and Vision Assistant)
- Model name in Ollama: `llava`
- Good general-purpose vision-language understanding
- Recommended for balanced performance

### Qwen-VL
- Model name in Ollama: `qwen3-vl` (use `qwen-vl` as the engine name)
- Advanced vision-language model from Alibaba Cloud
- Excellent multilingual support including Chinese and English
- Good for complex visual reasoning tasks

## Troubleshooting

### Ollama Connection Issues

If you get connection errors:
1. Ensure Ollama is running: `ollama serve`
2. Check if the model is pulled: `ollama list`
3. Verify the base URL in params matches your Ollama instance

### Model Not Found

If you get model not found errors:
```bash
# Pull the required model
ollama pull llava
ollama pull qwen3-vl
```

### Image Loading Errors

- Ensure the image file exists and is readable
- Supported formats: JPEG, PNG, and other formats supported by PIL
- Check file permissions

## Requirements

See `requirements.txt` for the complete list of dependencies:
- `requests>=2.31.0` - For HTTP requests to Ollama API
- `Pillow>=10.0.0` - For image processing

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
