from collections import deque


class AccuracyTracker:
    def __init__(self):
        self.history = deque(maxlen=500)

    def record(self, predicted: str, outcome_return: float):
        win = (predicted == "BUY" and outcome_return > 0) or (predicted == "SELL" and outcome_return < 0)
        self.history.append(1 if win else 0)

    @property
    def accuracy(self) -> float:
        if not self.history:
            return 0.0
        return sum(self.history) / len(self.history)


accuracy_tracker = AccuracyTracker()
