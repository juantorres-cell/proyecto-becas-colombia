"""Configuración de pytest: poner la raíz del proyecto en sys.path.

Así los tests pueden hacer `from logica import ...` sin instalar el paquete.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))