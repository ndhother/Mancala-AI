"""Configuration and parsing utilities for Minimax move ordering."""

_MOVE_CODES = {
    "A": "Ascending (BASE)",
    "D": "Descending (BASE)", 
    "L": "Least to Most Seeds",
    "M": "Most to Least Seeds", 
    "I": "Iterative Ranking",
    "H": "Heuristic Value", 
    "X": "Extra Turn Priority",
    "C": "Capture Priority", 
    "R": "Relay Chain Priority",
    "V": "Harvest Chain Priority",
}

_BASE_CODES = ("A", "D")

MOVE_ORDER_INFO = (
    "Controls the order in which Minimax searches moves.\n\n"
    "Enter one or more codes in priority order:\n"
    "(One base code is required.)\n\n"
    + "\n".join(f"{code}:\t{name}" for code, name in _MOVE_CODES.items())
)


def parse_move_order(code):
    """Return a validated and normalised Minimax move-ordering code."""
    if not isinstance(code, str):
        raise ValueError("Move order must be a string.")

    # Remove duplicates but preserve order
    code = "".join(dict.fromkeys(code.upper()))

    if not code or any(c not in _MOVE_CODES for c in code):
        raise ValueError("Missing or invalid move ordering.")
    
    base = [c for c in code if c in _BASE_CODES]
    
    # Keep first base code only
    base = base[0] if base else None

    code = "".join(c for c in code if c not in _BASE_CODES)

    # Ensure at least one base ordering
    code += base or _BASE_CODES[0]

    return code
