# Mancala AI

A desktop application for playing and simulating Mancala board games with configurable AI agents.

**Mancala AI** currently supports three Mancala variants: **Kalah**, **Oware**, and **Congkak**. Matches can be configured with different game rules, board layouts, and combinations of human and AI players.

Built with **Python** and **PySide6**.

## Features

* Play **Kalah**, **Oware**, and **Congkak**
* Configure board layout and game-specific rules
* Play using the **Pie Rule**
* Play human vs human, human vs AI, or AI vs AI matches
* Choose between **Random**, **Greedy**, and **Minimax** AI agents
* Configure Minimax search using:
  * Depth and time limits
  * Alpha-beta pruning
  * Multiple evaluation strategies
  * Customisable move ordering
* Save match configurations and user settings between sessions
* Step through AI vs AI matches one move at a time using **Step Mode**
* Detect repeated game states using a configurable repetition limit

## AI Agents

### Random

Selects randomly from the available legal actions. An optional seed can be provided for reproducible play.

### Greedy

Selects moves based on their immediate score gain.

### Minimax

Supports depth-limited and time-limited Minimax search. Time-limited searches use iterative deepening to retain the result of the deepest completed search.

Search can be configured with alpha-beta pruning, a choice of six evaluation heuristics, and priority-based move ordering using ten available ordering criteria. 

Minimax searches run separately from the UI and active searches are cancelled when leaving a match.

## Requirements

Python 3.12 or later is required.

Install the required dependencies with:

```bash
python -m pip install -r requirements.txt
```

## Running the Application

From the project root, run:

```bash
python -m mancala_ai
```

### Building the Desktop Application

A PyInstaller specification is included for building the desktop application.

Install PyInstaller with:

```bash
python -m pip install pyinstaller
```

Then build from the project root with:

```bash
pyinstaller "Mancala AI.spec"
```

The packaged application will be created in the `dist` directory.

## Project Structure

```text
mancala_ai/
├── agents/       # Random, Greedy, and Minimax agents
├── config/       # Configuration definitions, validation, and persistence
├── engine/       # Match execution
├── games/        # Game implementations and state representation
├── ui/           # PySide6 interface and application pages
├── __main__.py   # Application entry point
└── prepare.py    # Configuration data and match preparation
```

## Background

Mancala AI began as part of my final-year university project exploring AI approaches to Mancala games. The application has since been refactored to include a redesigned PySide6 interface, reorganised configuration system, and improved support for interactive matches.

## Future Improvements

Potential future improvements include:

* Automated test coverage
* In-app game rules and instructions
* Visual and animation improvements
* Additional AI strategies
* Expanded match analysis and results
