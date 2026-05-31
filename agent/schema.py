from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator


ActionType = Literal[
    "click",
    "type",
    "press",
    "goto",
    "scroll",
    "wait",
    "back",
    "extract",
    "done",
    "fail",
]


class BrowserAction(BaseModel):
    type: ActionType
    reason: Optional[str] = None
    # click
    x: Optional[int] = None
    y: Optional[int] = None
    # type
    text: Optional[str] = None
    # press
    key: Optional[str] = None
    # goto
    url: Optional[str] = None
    # scroll
    direction: Optional[Literal["up", "down"]] = None
    amount: Optional[int] = None
    # wait
    ms: Optional[int] = None

    @model_validator(mode="after")
    def validate_required_fields(self):
        if self.type == "click":
            if self.x is None or self.y is None:
                raise ValueError("click action requires both x and y.")

        elif self.type == "type":
            if not self.text:
                raise ValueError("type action requires text.")

        elif self.type == "press":
            if not self.key:
                raise ValueError("press action requires key.")

        elif self.type == "goto":
            if not self.url:
                raise ValueError("goto action requires url.")

        elif self.type == "scroll":
            if self.direction not in ("up", "down"):
                raise ValueError("scroll action requires direction to be 'up' or 'down'.")
            if self.amount is None:
                raise ValueError("scroll action requires amount.")

        elif self.type == "wait":
            if self.ms is None:
                raise ValueError("wait action requires ms.")

        return self


class AgentDecision(BaseModel):
    previous_action_success: bool
    error_explanation: str = ""
    next_action: BrowserAction
    expected_result: str
    confidence: float = Field(ge=0.0, le=1.0)