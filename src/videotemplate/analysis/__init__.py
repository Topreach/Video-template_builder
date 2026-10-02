"""Analysis modules. Current shot-boundary adapter remains experimental."""

from .proposals import AnalysisProposal
from .shot_boundaries import AdaptiveShotBoundaryAnalyzer, ShotBoundaryAnalysisError

__all__ = ["AnalysisProposal", "AdaptiveShotBoundaryAnalyzer", "ShotBoundaryAnalysisError"]
