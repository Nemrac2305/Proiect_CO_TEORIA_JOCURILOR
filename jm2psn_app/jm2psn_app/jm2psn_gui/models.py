from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .numeric import parse_number


@dataclass(slots=True)
class GameProblem:
    name: str
    matrix: list[list[float]]

    @property
    def n_rows(self) -> int:
        return len(self.matrix)

    @property
    def n_cols(self) -> int:
        return len(self.matrix[0]) if self.matrix else 0

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Numele jocului nu poate fi gol.")
        if not self.matrix:
            raise ValueError("Matricea jocului nu poate fi goala.")
        if not self.matrix[0]:
            raise ValueError("Matricea jocului trebuie sa aiba cel putin o coloana.")

        expected_cols = len(self.matrix[0])
        for i, row in enumerate(self.matrix, start=1):
            if len(row) != expected_cols:
                raise ValueError(f"Linia {i} nu are acelasi numar de coloane ca prima linie.")
            for j, value in enumerate(row, start=1):
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Elementul q[{i}][{j}] nu este numeric.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "matrix": [list(row) for row in self.matrix],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GameProblem":
        problem = cls(
            name=str(data.get("name", "Joc incarcat")),
            matrix=[[parse_number(x) for x in row] for row in data["matrix"]],
        )
        problem.validate()
        return problem


@dataclass(slots=True)
class GameSolveResult:
    status: str = "not_started"
    status_message: str = ""
    game_value: Optional[float] = None
    strategy_a: list[float] = field(default_factory=list)
    strategy_b: list[float] = field(default_factory=list)
    alpha: list[float] = field(default_factory=list)
    beta: list[float] = field(default_factory=list)
    alpha_red: list[float] = field(default_factory=list)
    beta_red: list[float] = field(default_factory=list)
    v1: Optional[float] = None
    v2: Optional[float] = None
    v1_red: Optional[float] = None
    v2_red: Optional[float] = None
    V1: Optional[float] = None
    K: float = 0.0
    reduced_matrix: list[list[float]] = field(default_factory=list)
    shifted_matrix: list[list[float]] = field(default_factory=list)
    kept_rows: list[int] = field(default_factory=list)
    kept_cols: list[int] = field(default_factory=list)
    reductions: list[tuple] = field(default_factory=list)
    x_aux: list[float] = field(default_factory=list)
    y_aux: list[float] = field(default_factory=list)
    row_payoffs: list[float] = field(default_factory=list)
    col_payoffs: list[float] = field(default_factory=list)
    bilinear: Optional[float] = None
    logs: list[str] = field(default_factory=list)
    full_output: str = ""
    raw_result: dict[str, Any] = field(default_factory=dict)
    error_details: Optional[str] = None
