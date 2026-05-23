import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path


FIELD_ORDER = [
    "Center frequency",
    "Bandwidth",
    "Q value",
    "ReVAR",
    "Minp",
    "Mout",
    "PHimp (inch)",
    "PHout (inch)",
]


REPO_ROOT = Path(__file__).resolve().parent
EXAMPLE_TEMPLATE_PATH = REPO_ROOT / "example.inp"


def build_default_inp_template() -> str:
    header = " FILTER DATA TEMPLATE (.inp)\n"
    meta = (
        " FORMAT: CENTER_FREQ  BANDWIDTH  Q_VALUE  ReVAR  Minp  Mout  PHimp(in)  PHout(in)\n"
        " -------------------------------------------------------------------------------\n"
    )
    sample_rows = [
        [1200.0, 85.0, 14.12, 1.60, 0.92, 0.88, 2.25, 2.10],
        [1750.0, 95.0, 18.42, 1.52, 0.90, 0.86, 2.40, 2.30],
        [2300.0, 120.0, 19.17, 1.45, 0.82, 0.79, 2.55, 2.48],
        [3100.0, 140.0, 22.14, 1.38, 0.76, 0.73, 2.70, 2.64],
    ]
    row_lines = [
        f" {r[0]:>11.3f} {r[1]:>10.3f} {r[2]:>9.3f} {r[3]:>7.3f} {r[4]:>6.3f} {r[5]:>6.3f} {r[6]:>11.3f} {r[7]:>11.3f}"
        for r in sample_rows
    ]
    footer = (
        "\n\n NOTES:\n"
        " - Replace sample values with real filter data.\n"
        " - Numeric rows with at least 8 values are parsed.\n"
    )
    return header + meta + "\n".join(row_lines) + footer


def load_inp_template() -> str:
    try:
        return EXAMPLE_TEMPLATE_PATH.read_text(encoding="utf-8")
    except OSError:
        return build_default_inp_template()


class InpViewerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("NMC Filter INP Viewer")
        self.root.geometry("1040x640")
        self.root.minsize(920, 560)
        self._set_styles()

        self.inp_data: list[dict[str, float]] = []
        self.template_text_value = load_inp_template()
        self.loaded_content = self.template_text_value

        self._build_menu()
        self._build_main_view()

    def _set_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 15, "bold"), foreground="#14325C")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#4D5C75")
        style.configure("Status.TLabel", font=("Segoe UI", 9), padding=(8, 5))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="open inp", command=self.open_inp_file)
        file_menu.add_command(label="open ideal", command=self.open_ideal_placeholder)
        menu_bar.add_cascade(label="file", menu=file_menu)
        self.root.config(menu=menu_bar)

    def _build_main_view(self) -> None:
        wrapper = ttk.Frame(self.root, padding=12)
        wrapper.pack(fill="both", expand=True)

        header = ttk.Frame(wrapper)
        header.pack(fill="x", pady=(0, 8))

        ttk.Label(header, text="NMC INP File Viewer", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Open INP data files, preview raw text, and inspect parsed filter values.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        actions = ttk.Frame(wrapper)
        actions.pack(fill="x", pady=(0, 8))
        ttk.Button(actions, text="Open INP", command=self.open_inp_file).pack(side="left")
        ttk.Button(actions, text="View Template", command=self.show_template_window).pack(
            side="left", padx=(8, 0)
        )

        panes = ttk.Panedwindow(wrapper, orient="horizontal")
        panes.pack(fill="both", expand=True)

        template_box = ttk.Labelframe(
            panes, text="INP Template (based on your example)", style="Section.TLabelframe"
        )
        data_box = ttk.Labelframe(panes, text="Parsed Data Preview", style="Section.TLabelframe")
        panes.add(template_box, weight=3)
        panes.add(data_box, weight=4)

        self.template_text = tk.Text(template_box, wrap="none", font=("Consolas", 10), height=18)
        t_y_scroll = ttk.Scrollbar(template_box, orient="vertical", command=self.template_text.yview)
        t_x_scroll = ttk.Scrollbar(
            template_box, orient="horizontal", command=self.template_text.xview
        )
        self.template_text.configure(
            yscrollcommand=t_y_scroll.set, xscrollcommand=t_x_scroll.set, background="#F9FBFE"
        )
        self.template_text.insert("1.0", self.template_text_value)
        self.template_text.config(state="disabled")
        self.template_text.grid(row=0, column=0, sticky="nsew")
        t_y_scroll.grid(row=0, column=1, sticky="ns")
        t_x_scroll.grid(row=1, column=0, sticky="ew")
        template_box.grid_rowconfigure(0, weight=1)
        template_box.grid_columnconfigure(0, weight=1)

        self.data_tree = ttk.Treeview(data_box, columns=FIELD_ORDER, show="headings", height=14)
        for col in FIELD_ORDER:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=120, anchor="center", minwidth=90)
        d_y_scroll = ttk.Scrollbar(data_box, orient="vertical", command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=d_y_scroll.set)
        self.data_tree.grid(row=0, column=0, sticky="nsew")
        d_y_scroll.grid(row=0, column=1, sticky="ns")
        data_box.grid_rowconfigure(0, weight=1)
        data_box.grid_columnconfigure(0, weight=1)

        self.status_label = ttk.Label(
            wrapper, text="Use file > open inp to load a file.", anchor="w", style="Status.TLabel"
        )
        self.status_label.pack(fill="x", pady=(8, 0))

        self._populate_tree_from_rows(self.parse_inp_content(self.template_text_value))

    def open_ideal_placeholder(self) -> None:
        messagebox.showinfo("Open Ideal", "Open Ideal is not implemented yet.")

    def open_inp_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Open INP file",
            filetypes=[("INP files", "*.inp"), ("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
                content = handle.read()
        except OSError as exc:
            messagebox.showerror("Error", f"Could not open file:\n{exc}")
            return

        self.loaded_content = content
        self.inp_data = self.parse_inp_content(content)
        self._populate_tree_from_rows(self.inp_data)
        self.status_label.config(
            text=f"Loaded: {file_path} | Parsed rows: {len(self.inp_data)}"
        )
        self.show_inp_text_window(file_path, content)

    def _populate_tree_from_rows(self, rows: list[dict[str, float]]) -> None:
        self.data_tree.delete(*self.data_tree.get_children())
        for row in rows:
            self.data_tree.insert("", "end", values=[f"{row[k]:.3f}" for k in FIELD_ORDER])

    @staticmethod
    def parse_inp_content(content: str) -> list[dict[str, float]]:
        rows: list[dict[str, float]] = []
        number_pattern = re.compile(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")

        for line in content.splitlines():
            if not line.strip():
                continue
            values = [float(match) for match in number_pattern.findall(line)]
            if len(values) < len(FIELD_ORDER):
                continue
            row = {FIELD_ORDER[i]: values[i] for i in range(len(FIELD_ORDER))}
            rows.append(row)

        return rows

    def show_template_window(self) -> None:
        self.show_inp_text_window("Template", self.template_text_value)

    def show_inp_text_window(self, file_path: str, content: str) -> None:
        child = tk.Toplevel(self.root)
        child.title(f"INP File View - {file_path}")
        child.geometry("900x550")
        child.configure(background="#EAF0F9")

        title_frame = ttk.Frame(child, padding=(10, 8))
        title_frame.pack(fill="x")
        ttk.Label(title_frame, text=f"Preview: {file_path}", style="Title.TLabel").pack(anchor="w")

        content_frame = ttk.Frame(child, padding=(10, 0, 10, 10))
        content_frame.pack(fill="both", expand=True)

        text_widget = tk.Text(content_frame, wrap="none", font=("Consolas", 10), background="#FFFFFF")
        y_scroll = ttk.Scrollbar(content_frame, orient="vertical", command=text_widget.yview)
        x_scroll = ttk.Scrollbar(content_frame, orient="horizontal", command=text_widget.xview)
        text_widget.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        text_widget.insert("1.0", content)
        text_widget.config(state="disabled")

        text_widget.grid(row=0, column=0, sticky="nsew", padx=(0, 2), pady=(0, 2))
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)


def main() -> None:
    root = tk.Tk()
    InpViewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
