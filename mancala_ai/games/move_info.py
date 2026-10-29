"""Move metadata for Mancala games."""

from dataclasses import dataclass, field


@dataclass
class MoveInfo:
    """Record rule effects produced by a Mancala move."""
    
    # Pie rule
    swap: bool = False

    # Kalah/Congkak
    extra_turn: bool = False
    capture: bool = False
    capture_seeds: int = 0

    # Congkak
    relay_count: int = 0
    relay_states: list = field(default_factory=list)

    # Oware
    harvest_count: int = 0
    harvest_seeds: int = 0
    grand_slam: bool = False
    no_harvest: bool = False
    starvation: bool = False
