import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
import uuid
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "filaments.json")

BASE_RATES_CZK = {
    "CZK": 1,
    "USD": 23.0,
    "EUR": 25.0,
    "GBP": 29.0,
    "PLN": 5.7,
    "HUF": 0.065,
    "RON": 5.0,
    "BGN": 12.8,
    "SEK": 2.2,
    "NOK": 2.1,
    "DKK": 3.4,
    "CHF": 26.0,
    "CAD": 17.0,
    "AUD": 15.0,
    "NZD": 14.0,
    "JPY": 0.15,
    "CNY": 3.2,
    "KRW": 0.017,
    "INR": 0.27,
    "BRL": 4.5,
    "MXN": 1.3,
    "TRY": 0.7,
    "RUB": 0.25,
    "UAH": 0.55,
    "THB": 0.65,
    "IDR": 0.0014,
    "MYR": 4.9,
    "PHP": 0.4,
    "SGD": 17.0,
    "HKD": 2.9,
    "TWD": 0.72,
    "ZAR": 1.25,
    "ILS": 6.3,
    "SAR": 6.1,
    "AED": 6.3,
    "QAR": 6.3,
    "KWD": 75.0,
    "BHD": 61.0,
    "OMR": 59.0,
    "JOD": 32.0,
    "EGP": 0.47,
    "NGN": 0.014,
    "KES": 0.18,
    "GHS": 1.9,
    "PKR": 0.082,
    "BDT": 0.21,
    "VND": 0.00092,
    "COP": 0.0057,
    "CLP": 0.024,
    "ARS": 0.023,
    "PEN": 6.1,
}

CURRENCIES = sorted(BASE_RATES_CZK.keys())

RATES = {}
for _f in CURRENCIES:
    for _t in CURRENCIES:
        if _f != _t:
            RATES[f"{_f}_{_t}"] = BASE_RATES_CZK[_t] / BASE_RATES_CZK[_f]

DEFAULT_MATERIALS = ["PLA", "ABS", "PETG", "TPU", "Nylon", "PC", "ASA", "PVA", "HIPS"]

C = {
    "bg": "#11111b",
    "card": "#181825",
    "input": "#242438",
    "input_bright": "#2e2e48",
    "accent": "#89b4fa",
    "accent_h": "#a6c8ff",
    "accent_p": "#74a8f7",
    "red": "#f38ba8",
    "red_h": "#f5b0c8",
    "orange": "#fab387",
    "orange_h": "#fbcba3",
    "green": "#a6e3a1",
    "yellow": "#f9e2af",
    "text": "#cdd6f4",
    "dim": "#6c7086",
    "sep": "#313244",
    "list_bg": "#11111b",
    "list_sel": "#45475a",
    "result": "#11111b",
    "white": "#ffffff",
}


def convert(amount, from_c, to_c):
    if from_c == to_c:
        return amount
    return amount * RATES.get(f"{from_c}_{to_c}", 1)


class In(tk.Entry):
    def __init__(self, parent, **kw):
        kw.setdefault("bg", C["input"])
        kw.setdefault("fg", C["text"])
        kw.setdefault("insertbackground", C["text"])
        kw.setdefault("font", ("Segoe UI", 10))
        kw.setdefault("relief", "flat")
        kw.setdefault("highlightthickness", 0)
        kw.setdefault("bd", 0)
        kw.setdefault("selectbackground", C["accent"])
        kw.setdefault("selectforeground", C["white"])
        super().__init__(parent, **kw)
        self.bind("<FocusIn>", lambda e: self.configure(bg=C["input_bright"]))
        self.bind("<FocusOut>", lambda e: self.configure(bg=C["input"]))


class Combo(tk.Frame):
    _active = None

    def __init__(self, parent, values=None, width=15, **kw):
        self._bg = kw.pop("bg", C["input"])
        super().__init__(parent, bg=self._bg, highlightthickness=0)
        self._values = values or []
        self._open = False
        self._callback = None

        self._entry = tk.Entry(self, bg=self._bg, fg=C["text"],
                               font=("Segoe UI", 10), relief="flat",
                               highlightthickness=0, bd=0,
                               insertbackground=C["text"], state="readonly",
                               readonlybackground=self._bg)
        self._entry.pack(fill="x", expand=True)
        self._entry.bind("<Button-1>", self._toggle)

        self._list = None

        if self._values:
            self.set(self._values[0])

    def _toggle(self, event=None):
        if self._open:
            self._close()
        else:
            self._open_list()

    def _open_list(self):
        if self._open:
            return
        if Combo._active and Combo._active is not self:
            Combo._active._close()

        self._list = tk.Toplevel(self)
        self._list.overrideredirect(True)
        self._list.configure(bg=C["sep"], highlightthickness=1,
                             highlightbackground=C["dim"])
        lb = tk.Listbox(self._list, bg=C["input"], fg=C["text"],
                        selectbackground=C["accent"], selectforeground=C["white"],
                        font=("Segoe UI", 10), highlightthickness=0,
                        bd=0, activestyle="none", relief="flat")
        lb.pack(fill="both", expand=True)
        for v in self._values:
            lb.insert(tk.END, v)
        lb.bind("<<ListboxSelect>>", lambda e: self._select(lb))
        lb.bind("<ButtonRelease-1>", lambda e: self.after(50, self._check_if_still_open))
        x = self._entry.winfo_rootx()
        y = self._entry.winfo_rooty() + self._entry.winfo_height()
        w = self._entry.winfo_width()
        h = min(len(self._values) * 28 + 4, 200)
        self._list.geometry(f"{w}x{h}+{x}+{y}")
        self._list.lift()
        self._open = True
        Combo._active = self
        self._list.bind("<FocusOut>", lambda e: self.after(100, self._check_if_still_open))
        self._list.focus_set()

    def _check_if_still_open(self):
        if not self._open:
            return
        try:
            focused = self._list.focus_get()
        except Exception:
            focused = None
        if focused is None:
            self._close()

    def _select(self, lb):
        sel = lb.curselection()
        if sel:
            val = self._values[sel[0]]
            self.set(val)
            if self._callback:
                self._callback(val)
        self._close()

    def _close(self):
        if self._list:
            self._list.destroy()
            self._list = None
        self._open = False
        if Combo._active is self:
            Combo._active = None

    def set(self, value):
        self._entry.configure(state="normal")
        self._entry.delete(0, tk.END)
        self._entry.insert(0, value)
        self._entry.configure(state="readonly")

    def get(self):
        return self._entry.get()

    def configure_values(self, values):
        self._values = values

    def on_select(self, callback):
        self._callback = callback


class RoundedCanvas(tk.Canvas):
    def __init__(self, parent, color, radius=10, **kw):
        super().__init__(parent, highlightthickness=0, bg=C["bg"], **kw)
        self._color = color
        self._radius = radius
        self.bind("<Configure>", self._paint)

    def _paint(self, e=None):
        self.delete("bg")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 2 or h < 2:
            return
        r = min(self._radius, w // 2, h // 2)
        self.create_polygon(
            r, 0, w - r, 0, w, 0, w, r, w, h - r, w, h,
            w - r, h, r, h, 0, h, 0, h - r, 0, r, 0, 0,
            fill=self._color, smooth=True, tags="bg"
        )
        self.tag_lower("bg")


class Btn(tk.Canvas):
    def __init__(self, parent, text, bg, fg="#ffffff", hover=None, pressed=None,
                 command=None, w=100, h=32, radius=8):
        super().__init__(parent, width=w, height=h, highlightthickness=0,
                         bg=C["bg"], cursor="hand2")
        self._bg = bg
        self._fg = fg
        self._hover = hover or bg
        self._pressed = pressed or bg
        self._cmd = command
        self._bw = w
        self._bh = h
        self._br = radius
        self._text = text
        self._draw(bg)
        self.bind("<Enter>", lambda e: self._draw(self._hover))
        self.bind("<Leave>", lambda e: self._draw(self._bg))
        self.bind("<ButtonPress-1>", lambda e: self._draw(self._pressed))
        self.bind("<ButtonRelease-1>", self._release)

    def _draw(self, color):
        self.delete("all")
        w, h, r = self._bw, self._bh, self._br
        self.create_polygon(
            r, 0, w - r, 0, w, 0, w, r, w, h - r, w, h,
            w - r, h, r, h, 0, h, 0, h - r, 0, r, 0, 0,
            fill=color, smooth=True
        )
        self.create_text(w / 2, h / 2, text=self._text, fill=self._fg,
                         font=("Segoe UI", 10, "bold"))

    def _release(self, e):
        self._draw(self._hover)
        if self._cmd:
            self._cmd()

    def set_text(self, t):
        self._text = t
        self._draw(self._bg)


class Spin(tk.Frame):
    def __init__(self, parent, from_=0, to=999, width=5, **kw):
        self._bg = kw.pop("bg", C["input"])
        super().__init__(parent, bg=self._bg, highlightthickness=0)
        self._val = tk.StringVar(value=str(from_))
        self._minus = tk.Label(self, text="-", bg=self._bg, fg=C["text"],
                               font=("Segoe UI", 11, "bold"), cursor="hand2", padx=4)
        self._minus.pack(side="left")
        self._minus.bind("<Button-1>", lambda e: self._step(-1))
        self._entry = tk.Entry(self, textvariable=self._val, bg=self._bg,
                               fg=C["text"], font=("Segoe UI", 10),
                               relief="flat", highlightthickness=0, bd=0,
                               insertbackground=C["text"], width=width, justify="center")
        self._entry.pack(side="left")
        self._plus = tk.Label(self, text="+", bg=self._bg, fg=C["text"],
                              font=("Segoe UI", 11, "bold"), cursor="hand2", padx=4)
        self._plus.pack(side="left")
        self._plus.bind("<Button-1>", lambda e: self._step(1))
        self._from = from_
        self._to = to

    def _step(self, delta):
        try:
            v = int(self._val.get()) + delta
        except ValueError:
            v = self._from
        v = max(self._from, min(self._to, v))
        self._val.set(str(v))

    def get(self):
        return self._val.get()


class FilamentList(tk.Frame):
    """Custom list showing filaments with color swatches, material tags, and stock."""
    def __init__(self, parent, on_select=None, on_edit=None, on_delete=None, **kw):
        super().__init__(parent, bg=C["list_bg"], highlightthickness=0, **kw)
        self._on_select = on_select
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._items = []
        self._selected_id = None

        self._menu = tk.Menu(self, tearoff=0, bg=C["input"], fg=C["text"],
                             activebackground=C["accent"], activeforeground=C["white"],
                             relief="flat", bd=0, font=("Segoe UI", 10))
        self._menu.add_command(label="Edit", command=self._menu_edit)
        self._menu.add_command(label="Delete", command=self._menu_delete)

        self._canvas = tk.Canvas(self, bg=C["list_bg"], highlightthickness=0,
                                 bd=0, cursor="hand2")
        self._canvas.pack(fill="both", expand=True)
        self._inner = tk.Frame(self._canvas, bg=C["list_bg"], highlightthickness=0)
        self._window = self._canvas.create_window(0, 0, window=self._inner, anchor="nw")

        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._inner.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._window, width=event.width)

    def set_items(self, items):
        self._items = items
        self._selected_id = None
        self._render()

    def get_selected_id(self):
        return self._selected_id

    def _render(self):
        for w in self._inner.winfo_children():
            w.destroy()

        for item in self._items:
            row = tk.Frame(self._inner, bg=C["list_bg"], highlightthickness=0, cursor="hand2")
            row.pack(fill="x", padx=4, pady=1)

            fid = item.get("id", "")
            color = item.get("color", "#888888")
            swatch = tk.Canvas(row, width=18, height=18, bg=C["list_bg"],
                               highlightthickness=0, bd=0)
            swatch.pack(side="left", padx=(8, 8), pady=6)
            swatch.create_oval(2, 2, 16, 16, fill=color, outline=color)

            text_frame = tk.Frame(row, bg=C["list_bg"], highlightthickness=0)
            text_frame.pack(side="left", fill="x", expand=True)

            name = item.get("name", "")
            material = item.get("material", "")
            grams = item.get("max_grams", 0)
            cost = item.get("cost_per_kg", 0)
            currency = item.get("currency", "CZK")
            stock = item.get("stock")

            tk.Label(text_frame, text=name, bg=C["list_bg"], fg=C["text"],
                     font=("Segoe UI", 10, "bold"), anchor="w").pack(anchor="w")
            detail = f"{grams}g  |  {cost:.2f} {currency}/kg"
            if material:
                detail = f"{material}  |  {detail}"
            if stock is not None and stock >= 0:
                detail = f"{detail}  |  Stock: {stock:.0f}g"
            tk.Label(text_frame, text=detail, bg=C["list_bg"], fg=C["dim"],
                     font=("Consolas", 9), anchor="w").pack(anchor="w")

            for widget in [row, swatch, text_frame]:
                widget.bind("<Button-1>", lambda e, i=fid: self._select(i))
                widget.bind("<Button-3>", lambda e, i=fid: self._show_menu(e, i))

            for child in text_frame.winfo_children():
                child.bind("<Button-1>", lambda e, i=fid: self._select(i))
                child.bind("<Button-3>", lambda e, i=fid: self._show_menu(e, i))

            tk.Frame(self._inner, bg=C["sep"], height=1).pack(fill="x", padx=12)

    def _select(self, fid):
        self._selected_id = fid
        self._highlight()
        if self._on_select:
            self._on_select(fid)

    def _show_menu(self, event, fid):
        self._selected_id = fid
        self._highlight()
        try:
            self._menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._menu.grab_release()

    def _menu_edit(self):
        if self._on_edit and self._selected_id:
            self._on_edit(self._selected_id)

    def _menu_delete(self):
        if self._on_delete and self._selected_id:
            self._on_delete(self._selected_id)

    def _highlight(self):
        for row in self._inner.winfo_children():
            if isinstance(row, tk.Frame):
                is_sel = False
                for child in row.winfo_children():
                    if isinstance(child, tk.Canvas):
                        try:
                            oval_id = child.find_all()[0] if child.find_all() else None
                        except Exception:
                            oval_id = None
                row.bind("<Button-1>", lambda e: None)
                for sub in row.winfo_children():
                    if hasattr(sub, '_fid'):
                        pass

        for row in self._inner.winfo_children():
            if not isinstance(row, tk.Frame):
                continue
            row_bg = C["list_bg"]
            for child in row.winfo_children():
                if isinstance(child, tk.Frame):
                    for sub in child.winfo_children():
                        try:
                            if sub.cget("font").split()[0] == "Segoe":
                                pass
                        except Exception:
                            pass

    def _set_row_bg(self, row, bg):
        row.configure(bg=bg)
        for child in row.winfo_children():
            try:
                child.configure(bg=bg)
            except tk.TclError:
                pass
            if isinstance(child, tk.Frame):
                for sub in child.winfo_children():
                    try:
                        sub.configure(bg=bg)
                    except tk.TclError:
                        pass


class ColorBtn(tk.Canvas):
    def __init__(self, parent, color="#888888", size=28, command=None, **kw):
        super().__init__(parent, width=size, height=size, highlightthickness=0,
                         bg=C["card"], cursor="hand2", bd=0)
        self._color = color
        self._size = size
        self._cmd = command
        self._draw()
        self.bind("<Button-1>", self._click)

    def _draw(self):
        self.delete("all")
        s = self._size
        m = 3
        self.create_oval(m, m, s - m, s - m, fill=self._color, outline=C["dim"], width=1)

    def _click(self, e=None):
        if self._cmd:
            self._cmd()

    def set_color(self, color):
        self._color = color
        self._draw()

    def get_color(self):
        return self._color


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Filament Cost Calculator")
        self.root.geometry("900x640")
        self.root.minsize(850, 600)
        self.root.configure(bg=C["bg"])

        self.filaments = []
        self.materials = list(DEFAULT_MATERIALS)
        self.disp_cur = tk.StringVar(value="CZK")
        self.edit_id = None
        self._filter_material = None

        self._load()
        self._ui()
        self._refresh()

    def _ui(self):
        outer = tk.Frame(self.root, bg=C["bg"], highlightthickness=0)
        outer.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(outer, text="Filament Cost Calculator", bg=C["bg"],
                 fg=C["accent"], font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 12))

        body = tk.Frame(outer, bg=C["bg"], highlightthickness=0)
        body.pack(fill="both", expand=True)

        lp = RoundedCanvas(body, C["card"], radius=10)
        lp.pack(side="left", fill="both", expand=True, padx=(0, 6))
        li = tk.Frame(lp, bg=C["card"], highlightthickness=0)
        li.place(relx=0, rely=0, relwidth=1, relheight=1, x=16, y=14, width=-32, height=-28)

        rp = RoundedCanvas(body, C["card"], radius=10)
        rp.pack(side="right", fill="both", expand=True, padx=(6, 0))
        ri = tk.Frame(rp, bg=C["card"], highlightthickness=0)
        ri.place(relx=0, rely=0, relwidth=1, relheight=1, x=16, y=14, width=-32, height=-28)

        self._left(li)
        self._right(ri)

    def _left(self, p):
        c = C
        tk.Label(p, text="FILAMENTS", bg=c["card"], fg=c["text"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Frame(p, bg=c["sep"], height=1).pack(fill="x", pady=6)

        f = tk.Frame(p, bg=c["card"], highlightthickness=0)
        f.pack(fill="x", pady=(4, 3))

        for i, (lbl, attr) in enumerate([("Name:", "e_name"), ("Max grams:", "e_grams"), ("Cost/kg:", "e_cost")]):
            tk.Label(f, text=lbl, bg=c["card"], fg=c["dim"],
                     font=("Segoe UI", 10)).grid(row=i, column=0, sticky="w", pady=2, padx=(0, 10))
            e = In(f, width=18)
            e.grid(row=i, column=1, sticky="ew", pady=2)
            setattr(self, attr, e)

        tk.Label(f, text="Material:", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", pady=2, padx=(0, 10))
        self.cb_mat = Combo(f, values=self.materials, width=16)
        self.cb_mat.grid(row=3, column=1, sticky="ew", pady=2)

        tk.Label(f, text="Currency:", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 10)).grid(row=4, column=0, sticky="w", pady=2, padx=(0, 10))
        self.cb_cur = Combo(f, values=CURRENCIES, width=16)
        self.cb_cur.grid(row=4, column=1, sticky="ew", pady=2)

        tk.Label(f, text="Stock (g):", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 10)).grid(row=5, column=0, sticky="w", pady=2, padx=(0, 10))
        self.e_stock = In(f, width=18)
        self.e_stock.grid(row=5, column=1, sticky="ew", pady=2)
        self.e_stock.insert(0, "")
        tk.Label(f, text="(optional)", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 8)).grid(row=6, column=1, sticky="w", pady=0)
        f.columnconfigure(1, weight=1)

        color_row = tk.Frame(p, bg=c["card"], highlightthickness=0)
        color_row.pack(fill="x", pady=(2, 3))
        tk.Label(color_row, text="Color:", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 10)).pack(side="left")
        self.color_btn = ColorBtn(color_row, color="#89b4fa", size=24, command=self._pick_color)
        self.color_btn.pack(side="left", padx=(10, 0))

        br = tk.Frame(p, bg=c["card"], highlightthickness=0)
        br.pack(fill="x", pady=(3, 5))
        self.b_add = Btn(br, "+ Add", c["accent"], hover=c["accent_h"],
                         pressed=c["accent_p"], command=self._add, w=90)
        self.b_add.pack(side="left")
        self.b_cancel = Btn(br, "Cancel", c["input"], hover=c["input_bright"],
                            command=self._cancel_edit, w=70)
        self.b_cancel.pack(side="left", padx=(8, 0))
        self.b_cancel.pack_forget()

        tk.Frame(p, bg=c["sep"], height=1).pack(fill="x", pady=3)

        top_row = tk.Frame(p, bg=c["card"], highlightthickness=0)
        top_row.pack(fill="x", pady=(3, 3))
        tk.Label(top_row, text="Show in:", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 9)).pack(side="left")
        self.cb_disp = Combo(top_row, values=CURRENCIES, width=5)
        self.cb_disp.pack(side="left", padx=(4, 0))
        tk.Label(top_row, text="Material:", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 9)).pack(side="left", padx=(12, 0))
        self.cb_mat_filter = Combo(top_row, values=["All"] + self.materials, width=10)
        self.cb_mat_filter.pack(side="left", padx=(4, 0))
        self.cb_mat_filter.set("All")
        self.cb_mat_filter.on_select(self._on_filter_change)

        tk.Frame(p, bg=c["sep"], height=1).pack(fill="x", pady=3)

        self.fl = FilamentList(p, on_select=self._on_list_select,
                               on_edit=self._edit, on_delete=self._delete)
        self.fl.pack(fill="both", expand=True)

        lb = tk.Frame(p, bg=c["card"], highlightthickness=0)
        lb.pack(fill="x", pady=(5, 0))
        Btn(lb, "Edit", c["orange"], fg="#1e1e2e", hover=c["orange_h"],
            command=self._edit, w=70, h=28).pack(side="left")
        Btn(lb, "Delete", c["red"], hover=c["red_h"],
            command=self._delete, w=70, h=28).pack(side="left", padx=(8, 0))

    def _right(self, p):
        c = C
        tk.Label(p, text="CALCULATOR", bg=c["card"], fg=c["text"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Frame(p, bg=c["sep"], height=1).pack(fill="x", pady=6)

        f = tk.Frame(p, bg=c["card"], highlightthickness=0)
        f.pack(fill="x", pady=4)

        tk.Label(f, text="Filament:", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
        self.cb_sel = Combo(f, width=22)
        self.cb_sel.grid(row=0, column=1, sticky="ew", pady=5)

        tk.Label(f, text="Grams used:", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5, padx=(0, 10))
        self.e_used = In(f, width=22)
        self.e_used.grid(row=1, column=1, sticky="ew", pady=5)

        tk.Label(f, text="Print time:", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=5, padx=(0, 10))
        tf = tk.Frame(f, bg=c["card"], highlightthickness=0)
        tf.grid(row=2, column=1, sticky="ew", pady=5)
        self.sp_h = Spin(tf, from_=0, to=999, width=4)
        self.sp_h.pack(side="left")
        tk.Label(tf, text="h", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 10)).pack(side="left", padx=(4, 10))
        self.sp_m = Spin(tf, from_=0, to=59, width=4)
        self.sp_m.pack(side="left")
        tk.Label(tf, text="min", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 10)).pack(side="left", padx=(4, 0))
        f.columnconfigure(1, weight=1)

        tk.Frame(p, bg=c["sep"], height=1).pack(fill="x", pady=8)

        rf = tk.Frame(p, bg=c["card"], highlightthickness=0)
        rf.pack(fill="x", pady=4)
        tk.Label(rf, text="Elec. rate ($/hr):", bg=c["card"], fg=c["dim"],
                 font=("Segoe UI", 10)).pack(side="left")
        self.e_rate = In(rf, width=10)
        self.e_rate.insert(0, "0.025")
        self.e_rate.pack(side="left", padx=(6, 0))

        Btn(p, "Calculate", c["accent"], hover=c["accent_h"],
            pressed=c["accent_p"], command=self._calc, w=140, h=36).pack(pady=12)

        tk.Frame(p, bg=c["sep"], height=1).pack(fill="x", pady=4)

        rc = tk.Frame(p, bg=c["result"], highlightthickness=0, bd=0)
        rc.pack(fill="x", pady=(10, 0))
        ri = tk.Frame(rc, bg=c["result"], highlightthickness=0)
        ri.pack(fill="x", padx=16, pady=12)

        self.r_fil = tk.Label(ri, text="Filament cost:       —", bg=c["result"],
                              fg=c["green"], font=("Consolas", 11, "bold"), anchor="w")
        self.r_fil.pack(fill="x", pady=2)
        self.r_ele = tk.Label(ri, text="Electricity cost:    —", bg=c["result"],
                              fg=c["green"], font=("Consolas", 11, "bold"), anchor="w")
        self.r_ele.pack(fill="x", pady=2)
        tk.Frame(ri, bg=c["sep"], height=1).pack(fill="x", pady=6)
        self.r_tot = tk.Label(ri, text="TOTAL:               —", bg=c["result"],
                              fg=c["yellow"], font=("Consolas", 14, "bold"), anchor="w")
        self.r_tot.pack(fill="x", pady=2)
        self.r_warn = tk.Label(ri, text="", bg=c["result"],
                               fg=c["red"], font=("Segoe UI", 9, "bold"), anchor="w")
        self.r_warn.pack(fill="x", pady=(4, 0))

    def _pick_color(self):
        color = colorchooser.askcolor(initialcolor=self.color_btn.get_color(),
                                       title="Pick filament color")
        if color and color[1]:
            self.color_btn.set_color(color[1])

    def _on_filter_change(self, value):
        self._filter_material = None if value == "All" else value
        self._refresh()

    def _on_list_select(self, fid):
        pass

    def _load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE) as f:
                    d = json.load(f)
                self.filaments = d.get("filaments", [])
                self.materials = d.get("settings", {}).get("materials", list(DEFAULT_MATERIALS))
                self.disp_cur.set(d.get("settings", {}).get("display_currency", "CZK"))
            except (json.JSONDecodeError, KeyError):
                pass

    def _save(self):
        with open(DATA_FILE, "w") as f:
            json.dump({
                "filaments": self.filaments,
                "settings": {
                    "display_currency": self.disp_cur.get(),
                    "materials": self.materials,
                }
            }, f, indent=2)

    def _get_filament_by_id(self, fid):
        return next((f for f in self.filaments if f["id"] == fid), None)

    def _refresh(self):
        filtered = self.filaments
        if self._filter_material:
            filtered = [fi for fi in self.filaments if fi.get("material") == self._filter_material]
        self.fl.set_items(filtered)

        names = [fi["name"] for fi in self.filaments]
        self.cb_sel.configure_values(names)
        if names and not self.cb_sel.get():
            self.cb_sel.set(names[0])

        self.cb_mat.configure_values(self.materials)
        self.cb_mat_filter.configure_values(["All"] + self.materials)

    def _add(self):
        n = self.e_name.get().strip()
        g = self.e_grams.get().strip()
        co = self.e_cost.get().strip()
        cu = self.cb_cur.get()
        mat = self.cb_mat.get()
        clr = self.color_btn.get_color()
        stock_str = self.e_stock.get().strip()

        if not n:
            messagebox.showwarning("Validation", "Enter a filament name.")
            return
        try:
            gv, cv = float(g), float(co)
        except ValueError:
            messagebox.showwarning("Validation", "Max grams and cost must be numbers.")
            return
        if gv <= 0 or cv < 0:
            messagebox.showwarning("Validation", "Max grams > 0, cost >= 0.")
            return

        stock = None
        if stock_str:
            try:
                stock = float(stock_str)
                if stock < 0:
                    messagebox.showwarning("Validation", "Stock must be >= 0.")
                    return
            except ValueError:
                messagebox.showwarning("Validation", "Stock must be a number.")
                return

        if self.edit_id:
            for fi in self.filaments:
                if fi["id"] == self.edit_id:
                    fi.update(name=n, max_grams=gv, cost_per_kg=cv,
                              currency=cu, material=mat, color=clr, stock=stock)
                    break
            self.edit_id = None
            self.b_add.set_text("+ Add")
            self.b_cancel.pack_forget()
        else:
            self.filaments.append({
                "id": str(uuid.uuid4())[:8], "name": n,
                "max_grams": gv, "cost_per_kg": cv,
                "currency": cu, "material": mat, "color": clr,
                "stock": stock,
            })
        for e in (self.e_name, self.e_grams, self.e_cost, self.e_stock):
            e.delete(0, tk.END)
        self.cb_cur.set("CZK")
        self.cb_mat.set(self.materials[0] if self.materials else "")
        self.color_btn.set_color("#89b4fa")
        self._save()
        self._refresh()

    def _cancel_edit(self):
        self.edit_id = None
        self.b_add.set_text("+ Add")
        self.b_cancel.pack_forget()
        for e in (self.e_name, self.e_grams, self.e_cost, self.e_stock):
            e.delete(0, tk.END)
        self.cb_cur.set("CZK")
        self.cb_mat.set(self.materials[0] if self.materials else "")
        self.color_btn.set_color("#89b4fa")

    def _edit(self, fid=None):
        if not fid:
            fid = self.fl.get_selected_id()
        if not fid:
            messagebox.showinfo("Info", "Select a filament to edit.")
            return
        fi = self._get_filament_by_id(fid)
        if not fi:
            return
        self.edit_id = fi["id"]
        for e, v in [(self.e_name, fi["name"]), (self.e_grams, fi["max_grams"]),
                      (self.e_cost, fi["cost_per_kg"])]:
            e.delete(0, tk.END)
            e.insert(0, str(v))
        stock = fi.get("stock")
        self.e_stock.delete(0, tk.END)
        if stock is not None:
            self.e_stock.insert(0, str(stock))
        self.cb_cur.set(fi.get("currency", "CZK"))
        self.cb_mat.set(fi.get("material", self.materials[0] if self.materials else ""))
        self.color_btn.set_color(fi.get("color", "#888888"))
        self.b_add.set_text("Save")
        self.b_cancel.pack(side="left", padx=(8, 0))

    def _delete(self, fid=None):
        if not fid:
            fid = self.fl.get_selected_id()
        if not fid:
            messagebox.showinfo("Info", "Select a filament to delete.")
            return
        fi = self._get_filament_by_id(fid)
        if not fi:
            return
        if messagebox.askyesno("Confirm", f"Delete '{fi['name']}'?"):
            self.filaments = [f for f in self.filaments if f["id"] != fid]
            self._save()
            self._refresh()

    def _calc(self):
        sn = self.cb_sel.get()
        if not sn:
            messagebox.showinfo("Info", "Select a filament first.")
            return
        fi = next((f for f in self.filaments if f["name"] == sn), None)
        if not fi:
            messagebox.showerror("Error", "Filament not found.")
            return
        try:
            gu = float(self.e_used.get().strip())
        except ValueError:
            messagebox.showwarning("Validation", "Grams used must be a number.")
            return
        if gu <= 0:
            messagebox.showwarning("Validation", "Grams used must be > 0.")
            return

        stock = fi.get("stock")
        if stock is not None and gu > stock:
            self.r_warn.configure(text=f"WARNING: Not enough stock! Have {stock:.0f}g, need {gu:.0f}g")
        else:
            self.r_warn.configure(text="")

        try:
            h = int(self.sp_h.get() or 0)
            m = int(self.sp_m.get() or 0)
        except ValueError:
            messagebox.showwarning("Validation", "Print time must be whole numbers.")
            return
        try:
            er = float(self.e_rate.get().strip())
        except ValueError:
            messagebox.showwarning("Validation", "Electricity rate must be a number.")
            return

        to = self.disp_cur.get()
        fc = convert((gu / fi["max_grams"]) * fi["cost_per_kg"], fi["currency"], to)
        ec = convert((h + m / 60) * er, "USD", to)
        tot = fc + ec
        sym = {
            "CZK": "CZK", "USD": "$", "EUR": "\u20ac", "GBP": "\u00a3",
            "PLN": "z\u0142", "HUF": "Ft", "RON": "lei", "BGN": "\u043b\u0432",
            "SEK": "kr", "NOK": "kr", "DKK": "kr", "CHF": "CHF",
            "CAD": "C$", "AUD": "A$", "NZD": "NZ$", "JPY": "\u00a5",
            "CNY": "\u00a5", "KRW": "\u20a9", "INR": "\u20b9", "BRL": "R$",
            "MXN": "MX$", "TRY": "\u20ba", "RUB": "\u20bd", "UAH": "\u20b4",
            "THB": "\u0e3f", "IDR": "Rp", "MYR": "RM", "PHP": "\u20b1",
            "SGD": "S$", "HKD": "HK$", "TWD": "NT$", "ZAR": "R",
            "ILS": "\u20aa", "SAR": "SAR", "AED": "AED", "QAR": "QAR",
            "KWD": "KD", "BHD": "BD", "OMR": "OMR", "JOD": "JD",
            "EGP": "E\u00a3", "NGN": "\u20a6", "KES": "KSh", "GHS": "GH\u20b5",
            "PKR": "Rs", "BDT": "\u09f3", "VND": "\u20ab", "COP": "COL$",
            "CLP": "CL$", "ARS": "AR$", "PEN": "S/.",
        }.get(to, to)
        self.r_fil.configure(text=f"Filament cost:       {fc:>10.2f} {sym}")
        self.r_ele.configure(text=f"Electricity cost:    {ec:>10.2f} {sym}")
        self.r_tot.configure(text=f"TOTAL:               {tot:>10.2f} {sym}")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
