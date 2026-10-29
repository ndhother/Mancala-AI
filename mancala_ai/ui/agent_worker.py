"""Background worker for Mancala agent searches."""

from PySide6.QtCore import QObject, QRunnable, Signal

from mancala_ai.agents.minimax_agent import SearchCancelled


class _WorkerSignal(QObject):
    """Provide signals emitted by an agent worker."""
    
    result = Signal(object, object)


class AgentWorker(QRunnable):
    """Run an agent search without blocking the UI."""

    def __init__(self, runner, cancel_event):
        super().__init__()

        self._runner = runner
        self._cancel_event = cancel_event

        self.signal = _WorkerSignal()

    def run(self):
        """Run the agent search and emit its result."""
        try:
            action, report = self._runner.choose_action(self._cancel_event)
        
        except SearchCancelled:
            return

        self.signal.result.emit(action, report)
