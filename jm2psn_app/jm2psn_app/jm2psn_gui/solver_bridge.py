from __future__ import annotations

import io
import traceback
from contextlib import redirect_stdout

from .jm2psn_solver_didactic import rezolva_JM2PSN_prin_PLB_ASP
from .models import GameProblem, GameSolveResult

STATUS_MESSAGES = {
    "not_started": "gata de lucru",
    "running": "se rezolva",
    "optim": "joc rezolvat",
    "punct_sa": "punct sa gasit",
    "error": "eroare",
}


def solve_game(problem: GameProblem) -> GameSolveResult:
    problem.validate()

    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            raw_result = rezolva_JM2PSN_prin_PLB_ASP([list(row) for row in problem.matrix])
        full_output = buffer.getvalue()

        status = str(raw_result.get("status", "error"))
        message = str(raw_result.get("message", STATUS_MESSAGES.get(status, status)))

        return GameSolveResult(
            status=status,
            status_message=message,
            game_value=raw_result.get("V"),
            strategy_a=list(raw_result.get("x_opt") or []),
            strategy_b=list(raw_result.get("y_opt") or []),
            alpha=list(raw_result.get("alpha") or []),
            beta=list(raw_result.get("beta") or []),
            alpha_red=list(raw_result.get("alpha_red") or []),
            beta_red=list(raw_result.get("beta_red") or []),
            v1=raw_result.get("v1"),
            v2=raw_result.get("v2"),
            v1_red=raw_result.get("v1_red"),
            v2_red=raw_result.get("v2_red"),
            V1=raw_result.get("V1"),
            K=float(raw_result.get("K", 0.0) or 0.0),
            reduced_matrix=[list(row) for row in raw_result.get("Q_redus", [])],
            shifted_matrix=[list(row) for row in raw_result.get("Q_shift", [])],
            kept_rows=list(raw_result.get("idx_linii_pastrate") or []),
            kept_cols=list(raw_result.get("idx_coloane_pastrate") or []),
            reductions=list(raw_result.get("jurnal_reduceri") or []),
            x_aux=list(raw_result.get("x_A") or []),
            y_aux=list(raw_result.get("y_B") or []),
            row_payoffs=list(raw_result.get("row_payoffs") or []),
            col_payoffs=list(raw_result.get("col_payoffs") or []),
            bilinear=raw_result.get("bilinear"),
            logs=full_output.splitlines(),
            full_output=full_output,
            raw_result=raw_result,
        )
    except Exception as exc:  # noqa: BLE001
        full_output = buffer.getvalue()
        details = traceback.format_exc()
        return GameSolveResult(
            status="error",
            status_message=f"Eroare la rezolvare: {exc}",
            logs=(full_output.splitlines() if full_output else []) + ["", details],
            full_output=(full_output + "\n\n" + details).strip(),
            error_details=details,
        )
