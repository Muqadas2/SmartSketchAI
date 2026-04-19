# """
# SmartSketch.AI - ML Package (Updated)
# """

# __version__ = "1.1.0"  # Updated version
# __author__ = "Muqaddas Anees, Muqadas Zahra, Eman Chaudhary"
# __institution__ = "NUST SEECS"

# from .validator import ForensicPromptValidator, validate_prompt
# from .generator import FaceGenerator, generate_face
# from .scorer import FaceScorer, score_image
# from .sketch_converter import MemoryEfficientSketchConverter, convert_to_sketch  # NEW
# from .pipeline import SmartSketchPipeline

# __all__ = [
#     'ForensicPromptValidator',
#     'FaceGenerator',
#     'FaceScorer',
#     'MemoryEfficientSketchConverter',  # NEW
#     'SmartSketchPipeline',
#     'validate_prompt',
#     'generate_face',
#     'score_image',
#     'convert_to_sketch',  # NEW
#     # 'generate_forensic_sketch',
# ]



import sys
from unittest.mock import MagicMock

# Shim for mediapipe.solutions (missing on some Python 3.14 wheels)
try:
    import mediapipe.solutions
except (ImportError, AttributeError):
    print("[Shim] Mocking missing mediapipe.solutions for compatibility...")
    mock_mp = MagicMock()
    if 'mediapipe' not in sys.modules:
        sys.modules['mediapipe'] = mock_mp
    sys.modules['mediapipe.solutions'] = MagicMock()
    sys.modules['mediapipe.solutions.face_mesh'] = MagicMock()
    sys.modules['mediapipe.solutions.drawing_utils'] = MagicMock()
    sys.modules['mediapipe.solutions.drawing_styles'] = MagicMock()

__version__ = "1.2.0"  # Updated for face editing
__author__ = "Muqaddas Anees, Muqadas Zahra, Eman Chaudhary"
__institution__ = "NUST SEECS"

from .validator import ForensicPromptValidator, validate_prompt
from .generator import FaceGenerator, generate_face
from .scorer import FaceScorer, score_image
# FIX: Import MemoryEfficientSketchConverter instead of SketchConverter
from .sketch_converter import MemoryEfficientSketchConverter, convert_to_sketch
from .editor import FaceEditor, edit_face  # NEW
from .pipeline import SmartSketchPipeline, generate_forensic_sketch

__all__ = [
    'ForensicPromptValidator',
    'FaceGenerator',
    'FaceScorer',
    'MemoryEfficientSketchConverter',  # FIX: Update here as well
    'FaceEditor',  # NEW
    'SmartSketchPipeline',
    'validate_prompt',
    'generate_face',
    'score_image',
    'convert_to_sketch',
    'edit_face',  # NEW
    'generate_forensic_sketch',
]