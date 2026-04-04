from __future__ import annotations

from .models import GameProblem


PRESET_GAMES: dict[str, GameProblem] = {
    "2x2 cu punct sa": GameProblem(
        name="2x2 cu punct sa",
        matrix=[
            [3.0, 1.0],
            [5.0, 2.0],
        ],
    ),
    "2x2 fara punct sa": GameProblem(
        name="2x2 fara punct sa",
        matrix=[
            [1.0, -1.0],
            [-1.0, 1.0],
        ],
    ),
    "3x3 cu reduceri": GameProblem(
        name="3x3 cu reduceri",
        matrix=[
            [4.0, 1.0, 3.0],
            [2.0, 0.0, 1.0],
            [5.0, 2.0, 4.0],
        ],
    ),
    "3x3 mixt clasic": GameProblem(
        name="3x3 mixt clasic",
        matrix=[
            [0.0, 2.0, -1.0],
            [1.0, -1.0, 3.0],
            [2.0, 1.0, 0.0],
        ],
    ),
}
