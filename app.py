import re
import tkinter as tk
from tkinter import filedialog, messagebox


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


class InpViewerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("NMC INP Viewer")
        self.root.geometry("800x500")

        self.inp_data: list[dict[str, float]] = []

        self._build_menu()
        self._build_main_view()

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open INP", command=self.open_inp_file)
        file_menu.add_command(label="Open Ideal", command=self.open_ideal_placeholder)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def _build_main_view(self) -> None:
        self.status_label = tk.Label(
            self.root,
            text="Use File > Open INP to load a file.",
            anchor="w",
            padx=8,
            pady=8,
        )
        self.status_label.pack(fill="x")

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

        self.inp_data = self.parse_inp_content(content)
        self.status_label.config(
            text=f"Loaded: {file_path} | Parsed rows: {len(self.inp_data)}"
        )
        self.show_inp_text_window(file_path, content)

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

    def show_inp_text_window(self, file_path: str, content: str) -> None:
        child = tk.Toplevel(self.root)
        child.title(f"INP File View - {file_path}")
        child.geometry("900x550")

        text_widget = tk.Text(child, wrap="none")
        y_scroll = tk.Scrollbar(child, orient="vertical", command=text_widget.yview)
        x_scroll = tk.Scrollbar(child, orient="horizontal", command=text_widget.xview)
        text_widget.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        text_widget.insert("1.0", content)
        text_widget.config(state="disabled")

        text_widget.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        child.grid_rowconfigure(0, weight=1)
        child.grid_columnconfigure(0, weight=1)


def main() -> None:
    root = tk.Tk()
    InpViewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
