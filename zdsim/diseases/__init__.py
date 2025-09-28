"""
Disease modules for zero-dose vaccination simulation.
"""

from .diphtheria import Diphtheria
from .tetanus import Tetanus
from .pertussis import Pertussis
from .hepatitis_b import HepatitisB
from .hib import Hib

__all__ = ['Diphtheria', 'Tetanus', 'Pertussis', 'HepatitisB', 'Hib']
