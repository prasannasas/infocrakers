
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import datetime
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def bot_reply(message: str):
    msg = message.lower()
    if "save" in msg or "savings" in msg or "goal" in msg:
        return "Try the 'Savings Goal' tool or type: 'I want to save 20000 in 6 months'."
    if "tax" in msg or "taxes" in msg or "income" in msg:
        return "Use 'Tax Estimator' or type: 'estimate tax on 500000'."
    if "invest" in msg or "returns" in msg:
        return "Use 'Investment Projection' tool to simulate returns."
    tips = [
        "Automate savings: little and often works best.",
        "Emergency fund = 3–6 months of expenses.",
        "Diversify — mix safer instruments and growth assets."
    ]
    return "I can help with savings, taxes and investments. " + np.random.choice(tips)

def simple_tax_estimator(annual_income):
    tax = 0.0
    slabs = [
        (250000, 0.0),
        (500000, 0.05),
        (1000000, 0.20),
        (float('inf'), 0.30)
    ]
    prev = 0
    for cap, rate in slabs:
        taxable = max(0, min(cap - prev, annual_income - prev))
        if taxable <= 0:
            prev = cap
            continue
        tax += taxable * rate
        prev = cap
    tax *= 1.04
    return tax

def savings_plan(target_amount, months):
    return target_amount / months

def investment_projection(principal, annual_rate_pct, years, contribution=0):
    r = annual_rate_pct / 100.0
    values = []
    balance = principal
    for year in range(1, years + 1):
        balance = balance * (1 + r) + contribution
        values.append(balance)
    return values


class FullscreenFinanceApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Personal Finance Chatbot")
        
        try:
            self.root.attributes("-fullscreen", True)
        except Exception:
            try:
                self.root.state("zoomed")
            except Exception:
                self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")

       
        self.root.bind("<Escape>", lambda e: self._exit_fullscreen())
        self.root.bind("<F11>", lambda e: self._toggle_fullscreen())

        
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.bg_canvas.bind("<Configure>", self._on_resize)

       
        self.landing_frame = None
        self.landing_win = None
        self.main_frame = None
        self.main_win = None

        # Create landing UI (centered)
        self._create_landing()

    # ---------------------------
    # Landing UI
    # ---------------------------
    def _create_landing(self):
        # Landing frame (small white card centered)
        self.landing_frame = tk.Frame(self.bg_canvas, bg="#ffffff", bd=0, relief="flat")
        lbl_title = tk.Label(self.landing_frame, text="Personal Finance Chatbot", font=("Segoe UI", 36, "bold"), bg="#ffffff")
        lbl_sub = tk.Label(self.landing_frame, text="Intelligent guidance for savings, taxes, and investments.", font=("Segoe UI", 14), bg="#ffffff")
        enter_btn = tk.Button(self.landing_frame, text="Enter", font=("Segoe UI", 14, "bold"), padx=20, pady=8, command=self._enter_main_ui)
        quit_btn = tk.Button(self.landing_frame, text="Quit", font=("Segoe UI", 10), padx=12, pady=6, command=self.root.destroy)

        lbl_title.pack(pady=(20,6))
        lbl_sub.pack(pady=(0,18))
        enter_btn.pack(pady=(0,10))
        quit_btn.pack(pady=(0,18))

        # create_window (we'll center it in _on_resize)
        self.landing_win = self.bg_canvas.create_window(0, 0, window=self.landing_frame, anchor="center")

    # ---------------------------
    # Resize / gradient handling
    # ---------------------------
    def _on_resize(self, event):
        w = max(event.width, 2)
        h = max(event.height, 2)
        # draw gradient (3-stop vertical gradient)
        self.bg_canvas.delete("gradient")
        colors = ["#063f56", "#0b132b", "#8b5cf6"]  # landing gradient colors
        stops = len(colors) - 1
        step = 3  # vertical step (px); increase for faster drawing, decrease for smoother
        for y in range(0, h, step):
            t = y / max(h - 1, 1)
            segment = min(int(t * stops), max(stops - 1, 0))
            local_t = (t * stops) - segment
            c1 = colors[segment]
            c2 = colors[segment + 1] if segment + 1 < len(colors) else colors[-1]
            r1, g1, b1 = tuple(int(c1.lstrip('#')[j:j+2], 16) for j in (0, 2, 4))
            r2, g2, b2 = tuple(int(c2.lstrip('#')[j:j+2], 16) for j in (0, 2, 4))
            r = int(r1 + (r2 - r1) * local_t)
            g = int(g1 + (g2 - g1) * local_t)
            b = int(b1 + (b2 - b1) * local_t)
            hexc = f"#{r:02x}{g:02x}{b:02x}"
            # draw a horizontal rectangle stripe
            self.bg_canvas.create_rectangle(0, y, w, min(y + step, h), outline="", fill=hexc, tags="gradient")

        # Position landing centered if present
        if self.landing_win is not None:
            self.bg_canvas.coords(self.landing_win, w // 2, h // 2)

        # If main UI exists, resize & anchor it to top-left and make it cover full canvas
        if self.main_win is not None:
            # reposition top-left
            try:
                self.bg_canvas.coords(self.main_win, 0, 0)
                # update width/height so the embedded frame expands to fill
                self.bg_canvas.itemconfigure(self.main_win, width=w, height=h)
            except Exception:
                pass

    # ---------------------------
    # Enter main UI (replaces landing)
    # ---------------------------
    def _enter_main_ui(self):
        # remove landing
        if self.landing_win is not None:
            try:
                self.bg_canvas.delete(self.landing_win)
            except Exception:
                pass
            self.landing_win = None
        if self.landing_frame is not None:
            try:
                self.landing_frame.destroy()
            except Exception:
                pass
            self.landing_frame = None

        # Create main_frame and embed it into canvas as a full-size window
        self.main_frame = tk.Frame(self.bg_canvas, bg="#f8fafc")
        w = self.bg_canvas.winfo_width() or self.root.winfo_screenwidth()
        h = self.bg_canvas.winfo_height() or self.root.winfo_screenheight()
        self.main_win = self.bg_canvas.create_window(0, 0, window=self.main_frame, anchor="nw", width=w, height=h)
        # Build main UI inside main_frame
        self._build_main_ui()

    # ---------------------------
    # Main chat UI (fills the screen)
    # ---------------------------
    def _build_main_ui(self):
        # Layout: two columns (left chat, right tools)
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        left = tk.Frame(self.main_frame, bg="#ffffff")
        right = tk.Frame(self.main_frame, bg="#0f172a")

        left.grid(row=0, column=0, sticky="nsew", padx=(30,12), pady=20)
        right.grid(row=0, column=1, sticky="nsew", padx=(12,30), pady=20)

        # Left: title, chat canvas, entry
        tk.Label(left, text="Personal Finance Chatbot", font=("Segoe UI", 24, "bold"), bg="#ffffff").pack(anchor="nw", pady=(6,2))
        tk.Label(left, text="Ask about savings, taxes, investments.", font=("Segoe UI", 10), bg="#ffffff", fg="#475569").pack(anchor="nw")

        chat_outer = tk.Frame(left, bg="#f1f5f9")
        chat_outer.pack(fill="both", expand=True, pady=(12,8))

        self.chat_canvas = tk.Canvas(chat_outer, bg="#f1f5f9", highlightthickness=0)
        vsb = ttk.Scrollbar(chat_outer, orient="vertical", command=self.chat_canvas.yview)
        self.chat_frame_inner = tk.Frame(self.chat_canvas, bg="#f1f5f9")
        self.chat_frame_inner.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        self.chat_canvas.create_window((0, 0), window=self.chat_frame_inner, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=vsb.set)
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Input row
        input_row = tk.Frame(left, bg="#ffffff")
        input_row.pack(fill="x", pady=(8,0))
        self.user_entry = ttk.Entry(input_row, font=("Segoe UI", 11))
        self.user_entry.pack(side="left", fill="x", expand=True, padx=(6,6), ipady=6)
        self.user_entry.bind("<Return>", lambda e: self._send_message())
        ttk.Button(input_row, text="Send", command=self._send_message).pack(side="right", padx=(0,6))

        # small suggestion chips
        chips = tk.Frame(left, bg="#ffffff")
        chips.pack(fill="x", pady=(8,0))
        for s in ["Savings", "Tax Estimator", "Investment Projection", "Budget Tips"]:
            b = tk.Button(chips, text=s, bd=0, padx=10, pady=6, bg="#e2e8f0", activebackground="#c7d2fe",
                          command=lambda t=s: self._suggestion_clicked(t))
            b.pack(side="left", padx=6)

        # Start with a bot greeting
        self._display_bot("Hi — I'm your finance assistant. Click suggestions or type a question.")

        # Right: tools & quick actions
        header = tk.Label(right, text="Tools & Calculators", font=("Segoe UI", 14, "bold"), bg="#0f172a", fg="#fff")
        header.pack(fill="x", padx=12, pady=(6,12))

        btn_save = tk.Button(right, text="Savings Goal", font=("Segoe UI", 11), bg="#10b981", fg="#fff",
                             command=self._open_savings_dialog)
        btn_save.pack(fill="x", padx=12, pady=(6,8))

        btn_tax = tk.Button(right, text="Tax Estimator", font=("Segoe UI", 11), bg="#ef4444", fg="#fff",
                             command=self._open_tax_estimator)
        btn_tax.pack(fill="x", padx=12, pady=8)

        btn_inv = tk.Button(right, text="Investment Projection", font=("Segoe UI", 11), bg="#7c3aed", fg="#fff",
                             command=self._open_investment_projection)
        btn_inv.pack(fill="x", padx=12, pady=8)

        tk.Label(right, text="Quick Facts", bg="#0f172a", fg="#fff", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(14,4))
        for f in ["Start small: consistency beats timing the market.",
                  "Emergency fund: 3–6 months expenses.",
                  "Tax planning can increase net returns."]:
            tk.Label(right, text=f, bg="#0f172a", fg="#c7d2fe", wraplength=260, justify="left").pack(anchor="w", padx=12, pady=4)

        footer = tk.Label(right, text=f"Updated: {datetime.date.today().isoformat()}", bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 8))
        footer.pack(side="bottom", pady=12, padx=6)
        exit_btn = tk.Button(right, text="Exit App", font=("Segoe UI", 11, "bold"),
                             bg="#dc2626", fg="#fff", command=self.root.destroy)
        exit_btn.pack(side="bottom", pady=(8,12), padx=12, fill="x")
     
    # ---------------------------
    # UI helpers: chat display & actions
    # ---------------------------
    def _display_bot(self, text):
        lbl = tk.Label(self.chat_frame_inner, text=text, wraplength=700, justify="left", bg="#f8fafc", fg="#0f172a",
                       padx=12, pady=8, relief="groove", bd=1)
        lbl.pack(anchor="w", pady=6, padx=8)
        self.root.after(50, lambda: self.chat_canvas.yview_moveto(1.0))

    def _display_user(self, text):
        lbl = tk.Label(self.chat_frame_inner, text=text, wraplength=700, justify="left", bg="#0f172a", fg="#fff",
                       padx=12, pady=8, relief="ridge")
        lbl.pack(anchor="e", pady=6, padx=8)
        self.root.after(50, lambda: self.chat_canvas.yview_moveto(1.0))

    def _send_message(self):
        txt = self.user_entry.get().strip()
        if not txt:
            return
        self.user_entry.delete(0, tk.END)
        self._display_user(txt)
        reply = bot_reply(txt)
        self.root.after(200, lambda: self._display_bot(reply))

    def _suggestion_clicked(self, label):
        if label == "Savings":
            self._open_savings_dialog()
        elif label == "Tax Estimator":
            self._open_tax_estimator()
        elif label == "Investment Projection":
            self._open_investment_projection()
        else:
            self._display_bot("Budget tip: 50/30/20 rule — 50% needs, 30% wants, 20% savings.")

    # ---------------------------
    # Tools dialogs
    # ---------------------------
    def _open_savings_dialog(self):
        target = simpledialog.askfloat("Savings Goal", "Target amount (₹):", minvalue=0)
        if target is None: return
        months = simpledialog.askinteger("Months", "Months to save:", minvalue=1, maxvalue=600)
        if months is None: return
        monthly = savings_plan(target, months)
        self._display_bot(f"Save ₹{monthly:,.0f}/month to reach ₹{target:,.0f} in {months} months.")

    def _open_tax_estimator(self):
        income = simpledialog.askfloat("Tax Estimator", "Annual taxable income (₹):", minvalue=0)
        if income is None: return
        tax = simple_tax_estimator(income)
        self._display_bot(f"Estimated tax on ₹{income:,.0f} : ₹{tax:,.0f} (example slabs).")

    def _open_investment_projection(self):
        p = simpledialog.askfloat("Investment Projection", "Initial principal (₹):", minvalue=0)
        if p is None: return
        r = simpledialog.askfloat("Expected annual return (%)", "Annual rate (%):", minvalue=0)
        if r is None: return
        years = simpledialog.askinteger("Years", "Number of years:", minvalue=1, maxvalue=100)
        if years is None: return
        contrib = simpledialog.askfloat("Annual contribution (optional)", "Yearly contribution (₹):", minvalue=0)
        if contrib is None:
            contrib = 0.0
        values = investment_projection(p, r, years, contribution=contrib)
        self._display_bot(f"Projection: ₹{values[-1]:,.0f} after {years} years.")
        self._show_investment_chart(values, r, p, contrib)

    def _show_investment_chart(self, values, rate, principal, contrib):
        win = tk.Toplevel(self.root)
        win.title("Investment Projection Chart")
        win.geometry("800x520")
        fig = Figure(figsize=(8,4.5), dpi=100)
        ax = fig.add_subplot(111)
        years = list(range(1, len(values) + 1))
        ax.plot(years, values, linewidth=2)
        ax.set_xlabel("Year")
        ax.set_ylabel("Value (₹)")
        ax.set_title(f"Projection @ {rate}% p.a.")
        ax.grid(True, linestyle="--", linewidth=0.5)
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------------------------
    # Fullscreen controls
    # ---------------------------
    def _exit_fullscreen(self):
        try:
            self.root.attributes("-fullscreen", False)
        except Exception:
            self.root.destroy()

    def _toggle_fullscreen(self):
        try:
            state = self.root.attributes("-fullscreen")
            self.root.attributes("-fullscreen", not state)
        except Exception:
            pass

    def run(self):
        self.root.mainloop()

# ---------------------------
# Run app
# ---------------------------
if __name__ == "__main__":
    app = FullscreenFinanceApp()
    app.run()
