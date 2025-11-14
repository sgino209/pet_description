"""
Pet Description Utility

This module provides a function to analyze pet images and generate descriptions
using various vision-language models via Ollama.
"""

import base64
import json
from pathlib import Path
from typing import Dict, Any, Union, Optional
import requests
from PIL import Image
import io


def load_params(params_file: Union[str, Path] = 'params.json') -> Dict[str, Any]:
    """
    Load parameters from a JSON file.
    
    Args:
        params_file: Path to the JSON parameters file. Default: 'params.json'
    
    Returns:
        Dictionary containing parameters from the JSON file, or empty dict if file not found
    """
    params_path = Path(params_file)
    if params_path.exists():
        try:
            with open(params_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load params from {params_file}: {e}")
            return {}
    return {}


def _get_prompt_for_language(language: str) -> str:
    """
    Get the default prompt for a given language.
    
    Args:
        language: Language code ('english' or 'hebrew')
    
    Returns:
        Prompt string in the specified language
    """
    prompts = {
        'english': 'Describe this pet in detail. Include information about the type of animal, breed (if identifiable), colors, size, pose, and any distinctive features.',
        'hebrew': 'תאר את חיית המחמד הזו בפירוט. כלול מידע על סוג החיה, גזע (אם ניתן לזיהוי), צבעים, גודל, תנוחה, וכל מאפיינים ייחודיים.'
    }
    return prompts.get(language.lower(), prompts['english'])


def describe_pet(image: Union[str, Path, bytes, Image.Image], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyzes a pet image and returns information about the pet.
    
    Args:
        image: Pet image. Can be:
            - Path to image file (str or Path)
            - Image bytes
            - PIL Image object
        params: Dictionary containing parameters (optional). If None, loads from params.json:
            - llm_engine (str): Model to use. Options: 'llava', 'qwen-vl'
            - language (str, optional): Language for the prompt. Options: 'english', 'hebrew'. Default: 'english'
            - ollama_base_url (str, optional): Base URL for Ollama API. Default: 'http://localhost:11434'
            - prompt (str, optional): Custom prompt for the model. If None, uses language-specific default
            - temperature (float, optional): Temperature for generation. Default: 0.7
            - max_tokens (int, optional): Maximum tokens to generate. Default: 512
    
    Returns:
        Dictionary containing:
            - description (str): Generated description of the pet
            - model_used (str): Model that was used
            - language_used (str): Language that was used
            - success (bool): Whether the operation was successful
            - error (str, optional): Error message if success is False
    """
    
    # Load parameters from JSON file
    json_params = load_params()
    
    # Default parameters
    default_params = {
        'ollama_base_url': 'http://localhost:11434',
        'language': 'english',
        'temperature': 0.7,
        'max_tokens': 512,
        'prompt': None
    }
    
    # Merge: defaults -> JSON params -> provided params (provided params take precedence)
    if params is None:
        params = {}
    config = {**default_params, **json_params, **params}
    
    # Validate and set language
    language = config.get('language', 'english').lower()
    valid_languages = ['english', 'hebrew']
    if language not in valid_languages:
        return {
            'success': False,
            'error': f'Invalid language: {language}. Must be one of: {", ".join(valid_languages)}'
        }
    
    # Set prompt based on language if not explicitly provided
    if config.get('prompt') is None:
        config['prompt'] = _get_prompt_for_language(language)
    
    # Validate required parameter
    if 'llm_engine' not in config:
        return {
            'success': False,
            'error': 'llm_engine parameter is required. Options: llava, qwen-vl'
        }
    
    llm_engine = config['llm_engine'].lower()
    valid_engines = ['llava', 'qwen-vl']
    
    if llm_engine not in valid_engines:
        return {
            'success': False,
            'error': f'Invalid llm_engine: {llm_engine}. Must be one of: {", ".join(valid_engines)}'
        }
    
    # Map engine names to Ollama model names
    model_map = {
        'llava': 'llava',
        'qwen-vl': 'qwen3-vl'
    }
    
    model_name = model_map[llm_engine]
    
    try:
        # Load and encode image
        image_data = _load_image(image)
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Prepare the request
        ollama_url = f"{config['ollama_base_url']}/api/generate"
        
        payload = {
            'model': model_name,
            'prompt': config['prompt'],
            'images': [image_base64],
            'stream': False,
            'options': {
                'temperature': config.get('temperature', 0.7),
                'num_predict': config.get('max_tokens', 512)
            }
        }
        
        # Note: Some Ollama versions may use 'image' (singular) instead of 'images' (array)
        # If you encounter issues, try uncommenting the line below and commenting out 'images'
        # payload['image'] = image_base64
        
        # Make request to Ollama
        response = requests.post(ollama_url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        
        return {
            'success': True,
            'description': result.get('response', ''),
            'model_used': model_name,
            'language_used': language,
            'full_response': result
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Ollama API error: {str(e)}',
            'model_used': model_name
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'model_used': model_name
        }


def _load_image(image: Union[str, Path, bytes, Image.Image]) -> bytes:
    """
    Helper function to load and convert image to bytes.
    
    Args:
        image: Image input in various formats
    
    Returns:
        Image as bytes
    """
    if isinstance(image, (str, Path)):
        # File path
        with open(image, 'rb') as f:
            return f.read()
    elif isinstance(image, bytes):
        # Already bytes
        return image
    elif isinstance(image, Image.Image):
        # PIL Image
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    else:
        raise ValueError(f'Unsupported image type: {type(image)}')


if __name__ == '__main__':
    import argparse
    
    # Load default params from JSON file
    default_params = load_params()
    
    # Create argument parser
    parser = argparse.ArgumentParser(
        description='Analyze pet images and generate descriptions using vision-language models via Ollama.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pet_description.py pet.jpg
  python pet_description.py pet.jpg --llm_engine llava --language english
  python pet_description.py pet.jpg --llm_engine qwen-vl --language hebrew
  python pet_description.py pet.jpg --llm_engine llava --temperature 0.8 --max_tokens 1024

Note: Parameters can also be set in params.json. Command-line arguments override params.json values.
        """
    )
    
    # Required positional argument
    parser.add_argument(
        'image_path',
        type=str,
        help='Path to the pet image file'
    )
    
    # Optional arguments
    parser.add_argument(
        '--llm_engine',
        type=str,
        choices=['llava', 'qwen-vl'],
        default=default_params.get('llm_engine'),
        help='LLM engine to use (default: from params.json, required if not in params.json)'
    )
    
    parser.add_argument(
        '--language',
        type=str,
        choices=['english', 'hebrew'],
        default=default_params.get('language', 'english'),
        help='Language for the prompt (default: from params.json or english)'
    )
    
    parser.add_argument(
        '--temperature',
        type=float,
        default=default_params.get('temperature', 0.7),
        help='Temperature for generation (default: from params.json or 0.7)'
    )
    
    parser.add_argument(
        '--max_tokens',
        type=int,
        default=default_params.get('max_tokens', 512),
        help='Maximum tokens to generate (default: from params.json or 512)'
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        default=default_params.get('prompt'),
        help='Custom prompt for the model (default: from params.json or language-specific default)'
    )
    
    parser.add_argument(
        '--ollama_base_url',
        type=str,
        default=default_params.get('ollama_base_url', 'http://localhost:11434'),
        help='Base URL for Ollama API (default: from params.json or http://localhost:11434)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Build params dictionary from arguments
    params = {
        'language': args.language,
        'temperature': args.temperature,
        'max_tokens': args.max_tokens,
        'ollama_base_url': args.ollama_base_url
    }
    
    # Add llm_engine if provided (either from args or params.json)
    if args.llm_engine is not None:
        params['llm_engine'] = args.llm_engine
    
    # Only add prompt if explicitly provided
    if args.prompt is not None:
        params['prompt'] = args.prompt
    
    # Call describe_pet
    result = describe_pet(args.image_path, params)
    
    # Display results
    if result['success']:
        print(f"Model used: {result['model_used']}")
        print(f"Language used: {result.get('language_used', 'N/A')}")
        print(f"\nDescription:\n{result['description']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        exit(1)

