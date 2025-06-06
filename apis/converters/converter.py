import os
from typing import Union, Optional
from pathlib import Path


from .text_from_audio import text_from_audio
from .text_from_image import text_from_image
from .text_from_text import text_from_text


__all__ = [
    'text_from_audio',
    'text_from_image', 
    'text_from_text',
    'convert_to_text',
    'get_supported_formats',
    'is_supported_format'
]


AUDIO_FORMATS = {'.wav', '.mp3', '.flac', '.aiff', '.m4a', '.ogg'}
IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}
TEXT_FORMATS = {'.txt', '.md', '.rtf', '.csv', '.json', '.xml', '.html'}


def get_supported_formats() -> dict:

    return {
        'audio': list(AUDIO_FORMATS),
        'image': list(IMAGE_FORMATS),
        'text': list(TEXT_FORMATS)
    }


def is_supported_format(file_path: Union[str, Path]) -> bool:

    ext = Path(file_path).suffix.lower()
    return ext in (AUDIO_FORMATS | IMAGE_FORMATS | TEXT_FORMATS)


def _detect_media_type(file_path: Union[str, Path]) -> Optional[str]:

    ext = Path(file_path).suffix.lower()
    
    if ext in AUDIO_FORMATS:
        return 'audio'
    elif ext in IMAGE_FORMATS:
        return 'image'
    elif ext in TEXT_FORMATS:
        return 'text'
    else:
        return None


def convert_to_text(file_path: Union[str, Path], media_type: Optional[str] = None) -> str:

    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # detect media type if not provided
    if media_type is None:
        media_type = _detect_media_type(file_path)
    
    if media_type is None:
        supported = get_supported_formats()
        raise ValueError(
            f"Unsupported file format: {file_path.suffix}\n"
            f"Supported formats: {supported}"
        )
    
    try:
        if media_type == 'audio':
            return text_from_audio(str(file_path))
        elif media_type == 'image':
            return text_from_image(str(file_path))
        elif media_type == 'text':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return text_from_text(content)
        else:
            raise ValueError(f"Unknown media type: {media_type}")
            
    except Exception as e:
        return f"[ERROR] Failed to convert {media_type} file '{file_path}': {str(e)}"