from __future__ import annotations

import json
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .models import GameProblem, GameSolveResult
from .numeric import format_number, parse_number
from .presets import PRESET_GAMES
from .solver_bridge import solve_game

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

MONO_FONT = ("Courier New", 12)
THEME = {
    "app_bg": ("#F2F6FC", "#0B1220"),
    "sidebar": ("#E8F0FF", "#0F172A"),
    "sidebar_border": ("#C9D9F2", "#22324A"),
    "surface": ("#FFFFFF", "#111827"),
    "surface_alt": ("#F7FAFF", "#162033"),
    "surface_soft": ("#EEF4FF", "#1B2940"),
    "border": ("#CBD8EE", "#30435F"),
    "text": ("#10233F", "#F3F7FF"),
    "text_muted": ("#526581", "#B8C7DE"),
    "accent": ("#2563EB", "#3B82F6"),
    "accent_hover": ("#1D4ED8", "#2563EB"),
    "accent_soft": ("#DCEAFE", "#1E3A5F"),
    "success": ("#1F7A43", "#67D08B"),
    "warning": ("#C96A12", "#FFB454"),
    "danger": ("#C0392B", "#FF8F8F"),
}
STATUS_COLORS = {
    "not_started": ("#5B6D86", "#BAC7DB"),
    "running": ("#2563EB", "#60A5FA"),
    "optim": ("#1F7A43", "#67D08B"),
    "punct_sa": ("#1F7A43", "#67D08B"),
    "error": ("#C0392B", "#FF8F8F"),
}


class ValidationError(ValueError):
    def __init__(self, message: str, widgets: list[ctk.CTkEntry] | None = None):
        super().__init__(message)
        self.widgets = widgets or []


# -----------------------------------------------------------------------------
# Formatare text
# -----------------------------------------------------------------------------

def format_matrix(matrix: list[list[float]]) -> str:
    if not matrix:
        return "-"
    return "\n".join("[" + ", ".join(format_number(v) for v in row) + "]" for row in matrix)


def build_strategy_string(values: list[float], prefix: str) -> str:
    if not values:
        return "-"
    return ", ".join(f"{prefix}{i + 1} = {format_number(value)}" for i, value in enumerate(values))


def format_percent(value: float | None) -> str:
    if value is None:
        return "-"
    return format_number((value or 0.0) * 100.0, prefer_fraction=False, decimal_places=2)


def build_interpretation_text(problem: GameProblem, result: GameSolveResult) -> str:
    lines = [
        "Interpretare a rezultatului",
        "==========================",
        "",
    ]

    if result.status == "error":
        lines.extend([
            "Rezolvarea nu a fost finalizata din cauza unei erori.",
            result.status_message or "Verifica fila Log pentru detalii.",
        ])
        return "\n".join(lines)

    if result.game_value is None or not result.strategy_a or not result.strategy_b:
        lines.extend([
            "Rezultatul curent nu contine suficiente date pentru o interpretare completa.",
            "Verifica fila Rezultat si fila Log.",
        ])
        return "\n".join(lines)

    game_value_text = format_number(result.game_value)
    value_unit = "u. (unitati)"

    lines.extend([
        f"A -> castiga valoarea v = {game_value_text} {value_unit} daca aplica strategia:",
        "",
    ])
    for i, value in enumerate(result.strategy_a, start=1):
        lines.append(
            f"    - a{i} -> cu probabilitatea x{i} = {format_number(value)} (x{i} = {format_percent(value)}%)"
        )

    lines.extend([
        "",
        f"B -> pierde valoarea v = {game_value_text} {value_unit} daca aplica strategia:",
        "",
    ])
    for j, value in enumerate(result.strategy_b, start=1):
        lines.append(
            f"    - b{j} -> cu probabilitatea y{j} = {format_number(value)} (y{j} = {format_percent(value)}%)"
        )

    return "\n".join(lines)


def format_problem(problem: GameProblem) -> str:
    lines = [
        f"Nume joc: {problem.name}",
        f"Numar strategii A (linii): {problem.n_rows}",
        f"Numar strategii B (coloane): {problem.n_cols}",
        "",
        "Matricea castigului lui A:",
        format_matrix(problem.matrix),
    ]
    return "\n".join(lines)


def build_result_text(problem: GameProblem, result: GameSolveResult) -> str:
    lines = [
        "Rezumat solver JM2PSN",
        "====================",
        "",
        f"Status: {result.status}",
        f"Mesaj: {result.status_message}",
    ]

    if result.game_value is not None:
        lines.append(f"Valoarea jocului V: {format_number(result.game_value)}")
    else:
        lines.append("Valoarea jocului V: -")

    lines.extend(
        [
            f"Strategia optima a lui A: {build_strategy_string(result.strategy_a, 'A')}",
            f"Strategia optima a lui B: {build_strategy_string(result.strategy_b, 'B')}",
            "",
            "Indicatori initiali:",
            f"alpha = [{', '.join(format_number(x) for x in result.alpha)}]" if result.alpha else "alpha = -",
            f"beta  = [{', '.join(format_number(x) for x in result.beta)}]" if result.beta else "beta = -",
            f"v1 = {format_number(result.v1)}",
            f"v2 = {format_number(result.v2)}",
        ]
    )

    if result.alpha_red or result.beta_red:
        lines.extend(
            [
                "",
                "Dupa eventualele reduceri:",
                f"alpha_red = [{', '.join(format_number(x) for x in result.alpha_red)}]" if result.alpha_red else "alpha_red = -",
                f"beta_red  = [{', '.join(format_number(x) for x in result.beta_red)}]" if result.beta_red else "beta_red = -",
                f"v1_red = {format_number(result.v1_red)}",
                f"v2_red = {format_number(result.v2_red)}",
            ]
        )

    if result.x_aux or result.y_aux:
        lines.extend(
            [
                "",
                f"Solutia auxiliara PLA (x_A): {build_strategy_string(result.x_aux, 'x')}",
                f"Solutia auxiliara PLB (y_B): {build_strategy_string(result.y_aux, 'y')}",
            ]
        )

    return "\n".join(lines)


def build_details_text(problem: GameProblem, result: GameSolveResult) -> str:
    lines = [
        "Detalii complete",
        "================",
        "",
        format_problem(problem),
        "",
        f"Valoarea jocului V = {format_number(result.game_value)}",
        f"Strategia optima A = {build_strategy_string(result.strategy_a, 'A')}",
        f"Strategia optima B = {build_strategy_string(result.strategy_b, 'B')}",
        "",
        "Matrice redusa:",
        format_matrix(result.reduced_matrix),
        "",
        f"Linii pastrate (indexare de la 1): {[index + 1 for index in result.kept_rows] if result.kept_rows else '-'}",
        f"Coloane pastrate (indexare de la 1): {[index + 1 for index in result.kept_cols] if result.kept_cols else '-'}",
        f"Reducerile efectuate: {result.reductions if result.reductions else '-'}",
        "",
        f"Verificare x_opt * Q * y_opt = {format_number(result.bilinear)}",
    ]
    return "\n".join(lines)


def build_full_report(problem: GameProblem, result: GameSolveResult) -> str:
    sections = [
        "Aplicatie JM2PSN - raport",
        "=" * 24,
        "",
        format_problem(problem),
        "",
        build_result_text(problem, result),
        "",
        build_details_text(problem, result),
        "",
        build_interpretation_text(problem, result),
        "",
        "Log solver",
        "==========",
        result.full_output or "Fara log.",
    ]
    return "\n".join(sections)


# -----------------------------------------------------------------------------
# Widget-uri reutilizabile
# -----------------------------------------------------------------------------

def remember_default_border(widget: ctk.CTkEntry) -> None:
    widget._default_border_color = widget.cget("border_color")  # type: ignore[attr-defined]



def reset_border(widget: ctk.CTkEntry) -> None:
    color = getattr(widget, "_default_border_color", None)
    if color is not None:
        widget.configure(border_color=color)



def mark_invalid(widget: ctk.CTkEntry) -> None:
    widget.configure(border_color=THEME["danger"])



def mark_warning(widget: ctk.CTkEntry) -> None:
    widget.configure(border_color=THEME["warning"])


class MatrixEditor(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=THEME["surface_alt"], corner_radius=16, border_width=1, border_color=THEME["border"], **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame_color = self._apply_appearance_mode(self.cget("fg_color"))
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=frame_color)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.v_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.h_scrollbar = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.table_frame = ctk.CTkFrame(self.canvas, fg_color=THEME["surface_alt"])
        self._table_window = self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        self.table_frame.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel, add="+")

        self.row_count = 0
        self.col_count = 0
        self.entries: list[list[ctk.CTkEntry]] = []
        self.page_step = 6

    def _update_scroll_region(self, _event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        bbox = self.canvas.bbox(self._table_window)
        if not bbox:
            return
        content_width = bbox[2] - bbox[0]
        target_width = max(content_width, event.width)
        self.canvas.itemconfigure(self._table_window, width=target_width)
        self._update_scroll_region()

    def _is_pointer_inside(self) -> bool:
        widget_under_pointer = self.winfo_containing(self.winfo_pointerx(), self.winfo_pointery())
        while widget_under_pointer is not None:
            if widget_under_pointer == self:
                return True
            widget_under_pointer = widget_under_pointer.master
        return False

    def _on_mousewheel(self, event) -> None:
        if not self._is_pointer_inside():
            return
        delta = event.delta
        if delta == 0:
            return
        self.canvas.yview_scroll(int(-delta / 120), "units")

    def _on_shift_mousewheel(self, event) -> None:
        if not self._is_pointer_inside():
            return
        delta = event.delta
        if delta == 0:
            return
        self.canvas.xview_scroll(int(-delta / 120), "units")

    def _bind_navigation(self, entry: ctk.CTkEntry, row: int, col: int) -> None:
        target_widgets = [entry]
        inner_entry = getattr(entry, "_entry", None)
        if inner_entry is not None:
            target_widgets.append(inner_entry)

        for widget in target_widgets:
            widget._matrix_position = (row, col)  # type: ignore[attr-defined]
            widget._matrix_entry_owner = entry  # type: ignore[attr-defined]
            for sequence in ("<Left>", "<Right>", "<Up>", "<Down>", "<Prior>", "<Next>"):
                widget.bind(sequence, self._handle_navigation, add="+")

    def _handle_navigation(self, event) -> str | None:
        widget = event.widget
        owner = getattr(widget, "_matrix_entry_owner", widget)
        position = getattr(widget, "_matrix_position", None)
        if position is None:
            position = getattr(owner, "_matrix_position", None)
        if position is None:
            return None

        row, col = position
        target_row = row
        target_col = col

        if event.keysym == "Left":
            target_col -= 1
        elif event.keysym == "Right":
            target_col += 1
        elif event.keysym == "Up":
            target_row -= 1
        elif event.keysym == "Down":
            target_row += 1
        elif event.keysym == "Prior":
            target_row -= self.page_step
        elif event.keysym == "Next":
            target_row += self.page_step
        else:
            return None

        if not (0 <= target_row < self.row_count and 0 <= target_col < self.col_count):
            return "break"

        self.focus_cell(target_row, target_col, select_text=True)
        return "break"

    def focus_cell(self, row: int, col: int, *, select_text: bool = False) -> None:
        if not (0 <= row < self.row_count and 0 <= col < self.col_count):
            return

        entry = self.entries[row][col]
        inner_entry = getattr(entry, "_entry", None)
        focus_target = inner_entry if inner_entry is not None else entry

        entry.focus_set()
        try:
            focus_target.focus_set()
        except Exception:
            pass

        if select_text:
            for widget in (entry, focus_target):
                try:
                    if hasattr(widget, "select_range"):
                        widget.select_range(0, tk.END)
                    elif hasattr(widget, "selection_range"):
                        widget.selection_range(0, tk.END)
                except Exception:
                    pass
                try:
                    widget.icursor(tk.END)
                except Exception:
                    pass

        self._ensure_cell_visible(row, col)

    def _ensure_cell_visible(self, row: int, col: int) -> None:
        self.update_idletasks()
        bbox = self.canvas.bbox(self._table_window)
        if not bbox:
            return

        entry = self.entries[row][col]
        entry_left = entry.winfo_x()
        entry_top = entry.winfo_y()
        entry_right = entry_left + entry.winfo_width()
        entry_bottom = entry_top + entry.winfo_height()

        total_width = max(1, bbox[2] - bbox[0])
        total_height = max(1, bbox[3] - bbox[1])
        viewport_left = self.canvas.canvasx(0)
        viewport_top = self.canvas.canvasy(0)
        viewport_right = viewport_left + self.canvas.winfo_width()
        viewport_bottom = viewport_top + self.canvas.winfo_height()

        new_x = None
        new_y = None

        if entry_left < viewport_left:
            new_x = entry_left / total_width
        elif entry_right > viewport_right:
            new_x = (entry_right - self.canvas.winfo_width()) / total_width

        if entry_top < viewport_top:
            new_y = entry_top / total_height
        elif entry_bottom > viewport_bottom:
            new_y = (entry_bottom - self.canvas.winfo_height()) / total_height

        if new_x is not None:
            self.canvas.xview_moveto(min(max(new_x, 0.0), 1.0))
        if new_y is not None:
            self.canvas.yview_moveto(min(max(new_y, 0.0), 1.0))

    def set_dimensions(self, row_count: int, col_count: int) -> None:
        self.row_count = row_count
        self.col_count = col_count

        for child in self.table_frame.winfo_children():
            child.destroy()
        self.entries.clear()

        if row_count <= 0 or col_count <= 0:
            self._update_scroll_region()
            return

        ctk.CTkLabel(self.table_frame, text="A\\B").grid(row=0, column=0, padx=8, pady=(10, 6), sticky="w")
        for j in range(col_count):
            ctk.CTkLabel(self.table_frame, text=f"B{j + 1}", text_color=THEME["text"]).grid(row=0, column=j + 1, padx=6, pady=(10, 6))

        for i in range(row_count):
            ctk.CTkLabel(self.table_frame, text=f"A{i + 1}", text_color=THEME["text"]).grid(row=i + 1, column=0, padx=8, pady=6, sticky="w")
            row_entries: list[ctk.CTkEntry] = []
            for j in range(col_count):
                entry = ctk.CTkEntry(self.table_frame, width=90, justify="center", fg_color=THEME["surface"], border_color=THEME["border"], text_color=THEME["text"], corner_radius=10)
                entry.grid(row=i + 1, column=j + 1, padx=6, pady=6)
                entry.insert(0, "0")
                remember_default_border(entry)
                self._bind_navigation(entry, i, j)
                row_entries.append(entry)
            self.entries.append(row_entries)

        self.update_idletasks()
        self._update_scroll_region()
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.focus_cell(0, 0, select_text=True)

    def get_entry_widgets(self) -> list[ctk.CTkEntry]:
        widgets: list[ctk.CTkEntry] = []
        for row in self.entries:
            widgets.extend(row)
        return widgets

    def set_values(self, matrix: list[list[float]]) -> None:
        self.set_dimensions(len(matrix), len(matrix[0]) if matrix else 0)
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                entry = self.entries[i][j]
                entry.delete(0, tk.END)
                entry.insert(0, format_number(value))

    def fill_with_zeros(self) -> None:
        for row in self.entries:
            for entry in row:
                entry.delete(0, tk.END)
                entry.insert(0, "0")


# -----------------------------------------------------------------------------
# Aplicatia principala
# -----------------------------------------------------------------------------
class JM2PSNApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("JM2PSN - CustomTkinter")
        self.geometry("1440x900")
        self.minsize(1180, 760)
        self.configure(fg_color=THEME["app_bg"])

        self.current_problem: GameProblem | None = None
        self.current_result: GameSolveResult | None = None
        self._validation_after_id: str | None = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()

        self.n_rows_entry.insert(0, "2")
        self.n_cols_entry.insert(0, "2")
        remember_default_border(self.n_rows_entry)
        remember_default_border(self.n_cols_entry)

        self.generate_matrix(silent=True)
        self._bind_static_validation()
        self.preset_menu.set(next(iter(PRESET_GAMES.keys())))
        self.load_selected_preset(show_message=False)
        self._refresh_live_warnings()

    def _primary_button_style(self) -> dict:
        return {
            "fg_color": THEME["accent"],
            "hover_color": THEME["accent_hover"],
            "text_color": "#FFFFFF",
            "corner_radius": 10,
            "height": 38,
        }

    def _secondary_button_style(self) -> dict:
        return {
            "fg_color": THEME["surface_soft"],
            "hover_color": THEME["accent_soft"],
            "text_color": THEME["text"],
            "border_width": 1,
            "border_color": THEME["border"],
            "corner_radius": 10,
            "height": 38,
        }

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, corner_radius=0, fg_color=THEME["sidebar"], border_width=1, border_color=THEME["sidebar_border"])
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(99, weight=1)

        ctk.CTkLabel(
            sidebar,
            text="JM2PSN UI",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=THEME["text"],
        ).grid(row=0, column=0, padx=20, pady=(24, 8), sticky="w")

        ctk.CTkLabel(
            sidebar,
            text="Aplicatie pentru jocuri matriciale de 2 persoane cu suma nula, construita in stilul simplex_app.",
            justify="left",
            wraplength=250,
            text_color=THEME["text_muted"],
        ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        ctk.CTkLabel(sidebar, text="Aspect", text_color=THEME["text"]).grid(row=2, column=0, padx=20, pady=(0, 6), sticky="w")
        self.appearance_menu = ctk.CTkOptionMenu(
            sidebar,
            values=["System", "Light", "Dark"],
            command=ctk.set_appearance_mode,
            fg_color=THEME["accent"],
            button_color=THEME["accent_hover"],
            button_hover_color=THEME["accent_hover"],
            text_color="#FFFFFF",
            dropdown_fg_color=THEME["surface"],
            dropdown_hover_color=THEME["accent_soft"],
            dropdown_text_color=THEME["text"],
        )
        self.appearance_menu.grid(row=3, column=0, padx=20, pady=(0, 16), sticky="ew")
        self.appearance_menu.set("System")

        ctk.CTkLabel(sidebar, text="Numar strategii A (linii)", text_color=THEME["text"]).grid(row=4, column=0, padx=20, pady=(0, 6), sticky="w")
        self.n_rows_entry = ctk.CTkEntry(sidebar, fg_color=THEME["surface"], border_color=THEME["border"], text_color=THEME["text"], corner_radius=10)
        self.n_rows_entry.grid(row=5, column=0, padx=20, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(sidebar, text="Numar strategii B (coloane)", text_color=THEME["text"]).grid(row=6, column=0, padx=20, pady=(0, 6), sticky="w")
        self.n_cols_entry = ctk.CTkEntry(sidebar, fg_color=THEME["surface"], border_color=THEME["border"], text_color=THEME["text"], corner_radius=10)
        self.n_cols_entry.grid(row=7, column=0, padx=20, pady=(0, 12), sticky="ew")

        ctk.CTkButton(sidebar, text="Genereaza matrice", command=self.generate_matrix, **self._primary_button_style()).grid(
            row=8, column=0, padx=20, pady=(0, 18), sticky="ew"
        )

        ctk.CTkLabel(sidebar, text="Exemple rapide", text_color=THEME["text"]).grid(row=9, column=0, padx=20, pady=(0, 6), sticky="w")
        self.preset_menu = ctk.CTkOptionMenu(
            sidebar,
            values=list(PRESET_GAMES.keys()),
            fg_color=THEME["surface_soft"],
            button_color=THEME["accent"],
            button_hover_color=THEME["accent_hover"],
            text_color=THEME["text"],
            dropdown_fg_color=THEME["surface"],
            dropdown_hover_color=THEME["accent_soft"],
            dropdown_text_color=THEME["text"],
        )
        self.preset_menu.grid(row=10, column=0, padx=20, pady=(0, 8), sticky="ew")

        ctk.CTkButton(sidebar, text="Incarca exemplu", command=self.load_selected_preset, **self._secondary_button_style()).grid(
            row=11, column=0, padx=20, pady=(0, 18), sticky="ew"
        )

        ctk.CTkButton(sidebar, text="Rezolva", command=self.solve_current_problem, **self._primary_button_style()).grid(
            row=12, column=0, padx=20, pady=(0, 8), sticky="ew"
        )
        ctk.CTkButton(sidebar, text="Reseteaza", command=self.reset_problem, **self._secondary_button_style()).grid(
            row=13, column=0, padx=20, pady=(0, 18), sticky="ew"
        )

        ctk.CTkButton(sidebar, text="Salveaza joc", command=self.save_problem, **self._secondary_button_style()).grid(
            row=14, column=0, padx=20, pady=(0, 8), sticky="ew"
        )
        ctk.CTkButton(sidebar, text="Incarca joc", command=self.load_problem, **self._secondary_button_style()).grid(
            row=15, column=0, padx=20, pady=(0, 8), sticky="ew"
        )
        ctk.CTkButton(sidebar, text="Exporta raport", command=self.export_report, **self._secondary_button_style()).grid(
            row=16, column=0, padx=20, pady=(0, 18), sticky="ew"
        )

        ctk.CTkLabel(
            sidebar,
            text="Nota: valorile introduse in matrice reprezinta castigurile jucatorului A.",
            wraplength=250,
            justify="left",
            text_color=THEME["text_muted"],
        ).grid(row=17, column=0, padx=20, pady=(0, 8), sticky="w")

        self.input_warning_label = ctk.CTkLabel(
            sidebar,
            text="",
            wraplength=250,
            justify="left",
            text_color=THEME["warning"],
        )
        self.input_warning_label.grid(row=18, column=0, padx=20, pady=(0, 20), sticky="w")

    def _build_main_area(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        summary = ctk.CTkFrame(container, fg_color=THEME["surface"], border_width=1, border_color=THEME["border"], corner_radius=18)
        summary.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        summary.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(summary, text="Status", font=ctk.CTkFont(weight="bold"), text_color=THEME["text"]).grid(
            row=0, column=0, padx=(20, 10), pady=(16, 4), sticky="w"
        )
        self.status_value_label = ctk.CTkLabel(summary, text="gata de lucru", text_color=THEME["text_muted"])
        self.status_value_label.grid(row=0, column=1, padx=(0, 20), pady=(16, 4), sticky="w")

        ctk.CTkLabel(summary, text="Valoare joc", font=ctk.CTkFont(weight="bold"), text_color=THEME["text"]).grid(
            row=1, column=0, padx=(20, 10), pady=4, sticky="w"
        )
        self.game_value_label = ctk.CTkLabel(summary, text="-", text_color=THEME["text"])
        self.game_value_label.grid(row=1, column=1, padx=(0, 20), pady=4, sticky="w")

        ctk.CTkLabel(summary, text="Strategia A", font=ctk.CTkFont(weight="bold"), text_color=THEME["text"]).grid(
            row=2, column=0, padx=(20, 10), pady=4, sticky="nw"
        )
        self.strategy_a_label = ctk.CTkLabel(summary, text="-", justify="left", wraplength=900, text_color=THEME["text"])
        self.strategy_a_label.grid(row=2, column=1, padx=(0, 20), pady=4, sticky="w")

        ctk.CTkLabel(summary, text="Strategia B", font=ctk.CTkFont(weight="bold"), text_color=THEME["text"]).grid(
            row=3, column=0, padx=(20, 10), pady=(4, 16), sticky="nw"
        )
        self.strategy_b_label = ctk.CTkLabel(summary, text="-", justify="left", wraplength=900, text_color=THEME["text"])
        self.strategy_b_label.grid(row=3, column=1, padx=(0, 20), pady=(4, 16), sticky="w")

        self.tabview = ctk.CTkTabview(container, fg_color=THEME["surface"], segmented_button_fg_color=THEME["surface_soft"], segmented_button_selected_color=THEME["accent"], segmented_button_selected_hover_color=THEME["accent_hover"], segmented_button_unselected_color=THEME["surface_soft"], segmented_button_unselected_hover_color=THEME["accent_soft"], text_color=THEME["text"])
        self.tabview.grid(row=1, column=0, sticky="nsew")
        self.problem_tab = self.tabview.add("Problema")
        self.result_tab = self.tabview.add("Rezultat")
        self.details_tab = self.tabview.add("Detalii")
        self.log_tab = self.tabview.add("Log")
        self.interpretation_tab = self.tabview.add("Interpretare")

        self._build_problem_tab()
        self._build_result_tab()
        self._build_details_tab()
        self._build_log_tab()
        self._build_interpretation_tab()

    def _build_problem_tab(self) -> None:
        self.problem_tab.grid_rowconfigure(0, weight=1)
        self.problem_tab.grid_columnconfigure(0, weight=1)

        matrix_card = ctk.CTkFrame(self.problem_tab, fg_color=THEME["surface"], border_width=1, border_color=THEME["border"], corner_radius=18)
        matrix_card.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        matrix_card.grid_rowconfigure(3, weight=1)
        matrix_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            matrix_card,
            text="Matricea jocului Q",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=THEME["text"],
        ).grid(row=0, column=0, padx=16, pady=(14, 8), sticky="w")
        ctk.CTkLabel(
            matrix_card,
            text="Introdu elementele q[i][j] ale matricei castigurilor lui A.",
            text_color=THEME["text_muted"],
        ).grid(row=1, column=0, padx=16, pady=(0, 4), sticky="w")
        ctk.CTkLabel(
            matrix_card,
            text="Navigare rapida: ← → ↑ ↓ intre celule, iar PgUp/PgDn sar cate 6 linii pe aceeasi coloana.",
            text_color=THEME["accent"],
        ).grid(row=2, column=0, padx=16, pady=(0, 8), sticky="w")

        self.matrix_editor = MatrixEditor(matrix_card)
        self.matrix_editor.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 12))

    def _build_result_tab(self) -> None:
        self.result_tab.grid_rowconfigure(0, weight=1)
        self.result_tab.grid_columnconfigure(0, weight=1)
        self.result_textbox = ctk.CTkTextbox(self.result_tab, wrap="none", font=MONO_FONT, fg_color=THEME["surface"], border_width=1, border_color=THEME["border"], text_color=THEME["text"], corner_radius=14)
        self.result_textbox.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self._set_textbox_content(self.result_textbox, "Rezultatul va aparea aici.")

    def _build_details_tab(self) -> None:
        self.details_tab.grid_rowconfigure(0, weight=1)
        self.details_tab.grid_columnconfigure(0, weight=1)
        self.details_textbox = ctk.CTkTextbox(self.details_tab, wrap="none", font=MONO_FONT, fg_color=THEME["surface"], border_width=1, border_color=THEME["border"], text_color=THEME["text"], corner_radius=14)
        self.details_textbox.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self._set_textbox_content(self.details_textbox, "Detaliile solverului vor aparea aici.")

    def _build_log_tab(self) -> None:
        self.log_tab.grid_rowconfigure(0, weight=1)
        self.log_tab.grid_columnconfigure(0, weight=1)
        self.log_textbox = ctk.CTkTextbox(self.log_tab, wrap="word", font=MONO_FONT, fg_color=THEME["surface"], border_width=1, border_color=THEME["border"], text_color=THEME["text"], corner_radius=14)
        self.log_textbox.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self._set_textbox_content(self.log_textbox, "Logul solverului va aparea aici.")

    def _build_interpretation_tab(self) -> None:
        self.interpretation_tab.grid_rowconfigure(0, weight=1)
        self.interpretation_tab.grid_columnconfigure(0, weight=1)
        self.interpretation_textbox = ctk.CTkTextbox(self.interpretation_tab, wrap="word", font=MONO_FONT, fg_color=THEME["surface"], border_width=1, border_color=THEME["border"], text_color=THEME["text"], corner_radius=14)
        self.interpretation_textbox.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self._set_textbox_content(self.interpretation_textbox, "Interpretarea rezultatelor va aparea aici.")

    def _set_textbox_content(self, textbox: ctk.CTkTextbox, text: str) -> None:
        textbox.configure(state="normal")
        textbox.delete("1.0", tk.END)
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")

    def _set_input_warning(self, text: str, *, error: bool = False) -> None:
        color = THEME["danger"] if error else THEME["warning"]
        self.input_warning_label.configure(text=text, text_color=color)

    def _bind_entry_validation(self, entry: ctk.CTkEntry, validator: str) -> None:
        entry.bind("<KeyRelease>", lambda _event, e=entry, v=validator: self._on_entry_key_release(e, v))
        entry.bind("<FocusOut>", lambda _event, e=entry, v=validator: self._validate_single_entry(e, v, refresh=True))

    def _on_entry_key_release(self, entry: ctk.CTkEntry, validator: str) -> None:
        self._validate_single_entry(entry, validator, refresh=False)
        self._schedule_live_warnings()

    def _schedule_live_warnings(self, delay_ms: int = 150) -> None:
        if self._validation_after_id is not None:
            try:
                self.after_cancel(self._validation_after_id)
            except Exception:
                pass
        self._validation_after_id = self.after(delay_ms, self._run_scheduled_live_warnings)

    def _run_scheduled_live_warnings(self) -> None:
        self._validation_after_id = None
        self._refresh_live_warnings()

    def _bind_static_validation(self) -> None:
        self._bind_entry_validation(self.n_rows_entry, "positive_int")
        self._bind_entry_validation(self.n_cols_entry, "positive_int")

    def _bind_dynamic_validation(self) -> None:
        for entry in self.matrix_editor.get_entry_widgets():
            self._bind_entry_validation(entry, "number")

    def _validate_single_entry(self, entry: ctk.CTkEntry, validator: str, *, refresh: bool = False) -> bool:
        raw = entry.get().strip()
        if not raw:
            mark_warning(entry)
            self._set_input_warning("Exista campuri goale sau incomplete.", error=False)
            if refresh:
                self._refresh_live_warnings()
            return False

        try:
            if validator == "positive_int":
                value = int(raw)
                if value <= 0:
                    raise ValueError
            else:
                parse_number(raw)
        except Exception:
            mark_invalid(entry)
            if validator == "positive_int":
                self._set_input_warning("Dimensiunile matricei trebuie sa fie numere intregi pozitive.", error=True)
            else:
                self._set_input_warning("Element invalid. Sunt permise valori ca 2, -1.5, 1/3.", error=True)
            if refresh:
                self._refresh_live_warnings()
            return False

        reset_border(entry)
        if refresh:
            self._refresh_live_warnings()
        return True

    def _refresh_live_warnings(self) -> None:
        invalid_exists = False
        incomplete_exists = False

        for entry in [self.n_rows_entry, self.n_cols_entry]:
            raw = entry.get().strip()
            if not raw:
                incomplete_exists = True
                continue
            try:
                if int(raw) <= 0:
                    invalid_exists = True
            except Exception:
                invalid_exists = True

        for entry in self.matrix_editor.get_entry_widgets():
            raw = entry.get().strip()
            if not raw:
                incomplete_exists = True
                continue
            try:
                parse_number(raw)
            except Exception:
                invalid_exists = True

        if invalid_exists:
            self._set_input_warning("Exista valori invalide in formular.", error=True)
            return
        if incomplete_exists:
            self._set_input_warning("Completeaza toate campurile numerice inainte de rezolvare.")
            return

        try:
            problem = self.collect_problem_from_ui()
        except ValidationError as exc:
            self._set_input_warning(str(exc), error=True)
            return
        except Exception:
            self._set_input_warning("")
            return

        warnings = self._build_structural_warnings(problem)
        if warnings:
            self._set_input_warning(warnings[0])
        else:
            self._set_input_warning("")

    def _build_structural_warnings(self, problem: GameProblem) -> list[str]:
        warnings: list[str] = []

        for i, row in enumerate(problem.matrix, start=1):
            if all(abs(value) <= 1e-9 for value in row):
                warnings.append(f"Linia A{i} este nula; verifica daca jocul a fost introdus corect.")

        for j in range(problem.n_cols):
            col = [problem.matrix[i][j] for i in range(problem.n_rows)]
            if all(abs(value) <= 1e-9 for value in col):
                warnings.append(f"Coloana B{j + 1} este nula; verifica datele introduse.")

        if any(value <= 0 for row in problem.matrix for value in row):
            warnings.append(
                "Exista elemente nenepozitive. Solverul va aplica translatarea la matrice strict pozitiva daca este necesar."
            )

        return warnings

    def _reset_all_borders(self) -> None:
        for widget in [self.n_rows_entry, self.n_cols_entry]:
            reset_border(widget)
        for widget in self.matrix_editor.get_entry_widgets():
            reset_border(widget)

    def _update_summary(self, result: GameSolveResult | None) -> None:
        if result is None:
            self.status_value_label.configure(text="gata de lucru", text_color=STATUS_COLORS["not_started"])
            self.game_value_label.configure(text="-")
            self.strategy_a_label.configure(text="-")
            self.strategy_b_label.configure(text="-")
            return

        status_color = STATUS_COLORS.get(result.status, STATUS_COLORS["not_started"])
        self.status_value_label.configure(text=result.status_message or result.status, text_color=status_color)
        self.game_value_label.configure(text=format_number(result.game_value))
        self.strategy_a_label.configure(text=build_strategy_string(result.strategy_a, "A"))
        self.strategy_b_label.configure(text=build_strategy_string(result.strategy_b, "B"))

    def _parse_positive_int(self, entry: ctk.CTkEntry, field_name: str) -> int:
        raw = entry.get().strip()
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValidationError(f"{field_name} trebuie sa fie un numar intreg pozitiv.", [entry]) from exc
        if value <= 0:
            raise ValidationError(f"{field_name} trebuie sa fie strict pozitiv.", [entry])
        return value

    def _parse_float_entry(self, entry: ctk.CTkEntry, field_name: str) -> float:
        raw = entry.get().strip()
        try:
            value = parse_number(raw)
        except ValueError as exc:
            raise ValidationError(
                f"{field_name} trebuie sa fie numeric (exemple valide: 2, -1.5, 1/3).",
                [entry],
            ) from exc
        return value

    def _validate_dimensions_are_synced(self, n_rows: int, n_cols: int) -> None:
        if self.matrix_editor.row_count != n_rows or self.matrix_editor.col_count != n_cols:
            raise ValidationError(
                "Ai schimbat dimensiunile matricei. Apasa 'Genereaza matrice' inainte de rezolvare.",
                [self.n_rows_entry, self.n_cols_entry],
            )

    def collect_problem_from_ui(self) -> GameProblem:
        self._reset_all_borders()

        n_rows = self._parse_positive_int(self.n_rows_entry, "Numarul de linii")
        n_cols = self._parse_positive_int(self.n_cols_entry, "Numarul de coloane")
        self._validate_dimensions_are_synced(n_rows, n_cols)

        matrix: list[list[float]] = []
        for i in range(n_rows):
            row: list[float] = []
            for j in range(n_cols):
                row.append(self._parse_float_entry(self.matrix_editor.entries[i][j], f"Elementul q[{i + 1}][{j + 1}]") )
            matrix.append(row)

        problem = GameProblem(name="Joc editat in UI", matrix=matrix)
        problem.validate()
        return problem

    def generate_matrix(self, silent: bool = False) -> None:
        self._reset_all_borders()
        try:
            n_rows = self._parse_positive_int(self.n_rows_entry, "Numarul de linii")
            n_cols = self._parse_positive_int(self.n_cols_entry, "Numarul de coloane")
        except ValidationError as exc:
            for widget in exc.widgets:
                mark_invalid(widget)
            if not silent:
                messagebox.showerror("Date invalide", str(exc))
            return

        self.matrix_editor.set_dimensions(n_rows, n_cols)
        self._bind_dynamic_validation()
        self._refresh_live_warnings()
        self.current_problem = None
        self.current_result = None
        self._update_summary(None)
        self._set_textbox_content(self.result_textbox, "Rezultatul va aparea aici.")
        self._set_textbox_content(self.details_textbox, "Detaliile solverului vor aparea aici.")
        self._set_textbox_content(self.log_textbox, "Logul solverului va aparea aici.")
        self._set_textbox_content(self.interpretation_textbox, "Interpretarea rezultatelor va aparea aici.")

        if not silent:
            messagebox.showinfo("Matrice regenerata", "Editorul a fost actualizat pentru noile dimensiuni.")

    def load_selected_preset(self, show_message: bool = True) -> None:
        problem = PRESET_GAMES[self.preset_menu.get()]
        self.apply_problem(problem)
        if show_message:
            messagebox.showinfo("Exemplu incarcat", f"A fost incarcat exemplul: {problem.name}")

    def apply_problem(self, problem: GameProblem) -> None:
        self.n_rows_entry.delete(0, tk.END)
        self.n_rows_entry.insert(0, str(problem.n_rows))
        self.n_cols_entry.delete(0, tk.END)
        self.n_cols_entry.insert(0, str(problem.n_cols))
        self.generate_matrix(silent=True)
        self.matrix_editor.set_values(problem.matrix)
        self._bind_dynamic_validation()
        self._refresh_live_warnings()
        self.current_problem = None
        self.current_result = None
        self._update_summary(None)

    def reset_problem(self) -> None:
        self.generate_matrix(silent=True)
        self.matrix_editor.fill_with_zeros()
        self.current_problem = None
        self.current_result = None
        self._update_summary(None)
        self._refresh_live_warnings()

    def solve_current_problem(self) -> None:
        try:
            problem = self.collect_problem_from_ui()
        except ValidationError as exc:
            for widget in exc.widgets:
                mark_invalid(widget)
            messagebox.showerror("Date invalide", str(exc))
            return
        except ValueError as exc:
            messagebox.showerror("Date invalide", str(exc))
            return

        warnings = self._build_structural_warnings(problem)
        if warnings:
            messagebox.showwarning("Avertismente model", "\n\n".join(warnings))

        self.current_problem = problem
        self.current_result = solve_game(problem)

        self._update_summary(self.current_result)
        self._set_textbox_content(self.result_textbox, build_result_text(problem, self.current_result))
        self._set_textbox_content(self.details_textbox, build_details_text(problem, self.current_result))
        self._set_textbox_content(self.log_textbox, self.current_result.full_output or "Fara log.")
        self._set_textbox_content(self.interpretation_textbox, build_interpretation_text(problem, self.current_result))
        self.tabview.set("Rezultat")

    def save_problem(self) -> None:
        try:
            problem = self.collect_problem_from_ui()
        except ValidationError as exc:
            for widget in exc.widgets:
                mark_invalid(widget)
            messagebox.showerror("Date invalide", str(exc))
            return
        except ValueError as exc:
            messagebox.showerror("Date invalide", str(exc))
            return

        path = filedialog.asksaveasfilename(
            title="Salveaza joc",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile="joc_jm2psn.json",
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as handle:
            json.dump(problem.to_dict(), handle, indent=2, ensure_ascii=False)

        messagebox.showinfo("Salvare reusita", f"Jocul a fost salvat in:\n{path}")

    def load_problem(self) -> None:
        path = filedialog.askopenfilename(
            title="Incarca joc",
            filetypes=[("JSON", "*.json")],
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            problem = GameProblem.from_dict(data)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Fisier invalid", f"Nu am putut citi jocul:\n{exc}")
            return

        self.apply_problem(problem)
        messagebox.showinfo("Joc incarcat", f"A fost incarcat jocul din:\n{path}")

    def export_report(self) -> None:
        if self.current_problem is None or self.current_result is None:
            messagebox.showinfo("Nimic de exportat", "Rezolva mai intai un joc.")
            return

        path = filedialog.asksaveasfilename(
            title="Exporta raport",
            defaultextension=".txt",
            filetypes=[("Text", "*.txt")],
            initialfile="raport_jm2psn.txt",
        )
        if not path:
            return

        report_text = build_full_report(self.current_problem, self.current_result)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(report_text)

        messagebox.showinfo("Raport exportat", f"Raportul a fost salvat in:\n{path}")



def main() -> None:
    app = JM2PSNApp()
    app.mainloop()
