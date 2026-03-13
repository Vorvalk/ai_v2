from __future__ import annotations

from dataclasses import dataclass, asdict


ALLOWED_METHODS = {
    "locator",
    "get_by_text",
    "get_by_placeholder",
    "get_by_label",
    "get_by_role",
    "get_by_test_id",
    "get_by_alt_text",
    "get_by_title",
}


@dataclass
class LocatorRequest:
    element: str
    url: str
    dom: str


@dataclass
class LocatorResult:
    method: str
    args: list
    kwargs: dict

    def validate(self) -> None:
        if self.method not in ALLOWED_METHODS:
            raise ValueError(f"Unsupported Playwright method: {self.method}")
        if not isinstance(self.args, list):
            raise ValueError("'args' must be a list.")
        if not isinstance(self.kwargs, dict):
            raise ValueError("'kwargs' must be a dict.")

    def to_dict(self) -> dict:
        self.validate()
        return asdict(self)

    def to_json(self) -> str:
        return __import__("json").dumps(self.to_dict())


@dataclass
class LocatorCandidatesResult:
    candidates: list[LocatorResult]

    def validate(self) -> None:
        if not isinstance(self.candidates, list) or not self.candidates:
            raise ValueError("'candidates' must be a non-empty list.")
        for candidate in self.candidates:
            if not isinstance(candidate, LocatorResult):
                raise ValueError("Each candidate must be a LocatorResult.")
            candidate.validate()

    def to_json(self) -> str:
        self.validate()
        return __import__("json").dumps(
            {"candidates": [candidate.to_dict() for candidate in self.candidates]}
        )