""" zdsim: agent-based zero-dose vaccination model (Starsim).

The model uses tetanus as the sentinel outcome for DTP1/pentavalent zero-dose
children, following Rono et al. (2024): diphtheria is eliminated, neonatal
tetanus is near elimination, pertussis and measles are under marked control,
so tetanus is the only DTP-bracket disease still endemic enough to serve as a
sensitive indicator of first-dose coverage.
"""

from .interventions import ZeroDoseVaccination
from .diseases import Tetanus

__all__ = [
    "ZeroDoseVaccination",
    "Tetanus",
]
