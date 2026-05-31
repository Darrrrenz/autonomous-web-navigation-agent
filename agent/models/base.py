from abc import ABC, abstractmethod
from pathlib import Path


class ModelClient(ABC):
    @abstractmethod
    def decide_action(self, prompt: str, screenshot_path: Path) -> str:
        pass

    @abstractmethod
    def extract_json(self, prompt: str) -> str:
        pass