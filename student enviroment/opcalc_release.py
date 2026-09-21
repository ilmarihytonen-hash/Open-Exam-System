# ==============================================================================
#  OPcalc project
#  Copyright (C) 2026 OPcalc project Contributors
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# ==============================================================================



import tkinter as tk
import sympy as sp
import json
import os
import re
import time
import termcolor 
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sympy.parsing.latex import parse_latex
from termcolor import colored
from datetime import datetime
from tkinter import ttk, messagebox, filedialog

VERSION = "Alpha build: 0.8.19.26"
ABOUT = """# OPcalc project

Copyright (C) 2026 OPcalc project Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OPcalc is a mathematics and physics calculation software designed to
perform calculations using both standard mathematical expressions
and LaTeX code.

OPcalc also includes graphical mathematics functionality, allowing
mathematical functions written in LaTeX to be plotted visually.
"""
# ============================================================
# OP CALC - Advanced Physics / Mathematics Calculator
# ============================================================

def check_libraries():

    libraries = {
        "Tkinter": "tkinter",
        "SymPy": "sympy",
        "NumPy": "numpy",
        "Matplotlib": "matplotlib",
        "Termcolor": "termcolor",
        "ANTLR4": "antlr4",
    }

    all_ok = True

    for name, import_name in libraries.items():

        try:
            __import__(import_name)

            print(
                f"Loading {name}"
                + colored("  [", "white")
                + colored("OK", "green")
                + colored("]", "white")
            )

        except ImportError:

            print(
                f"Loading {name}"
                + colored("  [", "white")
                + colored("MISSING", "red")
                + colored("]", "white")
            )

            all_ok = False

    return all_ok

print("Detected main file" + colored("  [", "white") + colored("OK", "green") + colored("]", "white"))
print("starting main script" + colored("  [", "white") + colored("OK", "green") + colored("]", "white"))
print(f"Starting OPcalc {VERSION}")
time.sleep(0.5)
print("# ==============================================================================")
print("#  OPcalc project")
print("#  Copyright (C) 2026 OPcalc project Contributors")
print("#")
print("#  This program is free software: you can redistribute it and/or modify")
print("#  it under the terms of the GNU General Public License as published by")
print("#  the Free Software Foundation, either version 3 of the License, or")
print("#  (at your option) any later version.")
print("# ==============================================================================")
time.sleep(2)
print("Loading Formulas" + colored("  [", "white") + colored("OK", "green") + colored("]", "white"))
print("Loading LaTeX -code" + colored("  [", "white") + colored("OK", "green") + colored("]", "white"))
time.sleep(0.5)
print("Loading Python libraries" + colored("  [", "white") + colored("OK", "green") + colored("]", "white"))

if not check_libraries():
    print(
        "One or more required libraries are missing."
        + colored("  [", "white")
        + colored("ERROR", "red")
        + colored("]", "white")
    )

print("Loading Saving system" + colored("  [", "white") + colored("OK", "green") + colored("]", "white"))
print("Loading Graphicalcalculator" + colored("  [", "white") + colored("OK", "green") + colored("]", "white"))
print("Loading LaTeX partser" + colored("  [", "white") + colored("OK", "green") + colored("]", "white"))
print("Loading UI" + colored("  [", "white") + colored("OK", "green") + colored("]", "white"))
print("Starting UI" + colored("  [", "white") + colored("OK", "green") + colored("]", "white"))

APP_NAME = "OPcalc"


HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "opcalc_history.json"
)

# ============================================================
# COMMON VARIABLE INFORMATION
# ============================================================

VARIABLE_INFO = {
    "F":  ("N", "Force"),
    "m":  ("kg", "Mass"),
    "m1": ("kg", "Mass 1"),
    "m2": ("kg", "Mass 2"),
    "a":  ("m/s²", "Acceleration"),
    "v":  ("m/s", "Velocity"),
    "v0": ("m/s", "Initial velocity"),
    "vf": ("m/s", "Final velocity"),
    "u":  ("m/s", "Initial velocity"),
    "t":  ("s", "Time"),
    "r":  ("m", "Radius"),
    "d":  ("m", "Distance"),
    "s":  ("m", "Displacement"),
    "g":  ("m/s²", "Gravitational acceleration"),
    "h":  ("m", "Height"),
    "G":  ("N·m²/kg²", "Gravitational constant"),
    "E":  ("J", "Energy"),
    "K":  ("J", "Kinetic energy"),
    "U":  ("J", "Potential energy"),
    "P":  ("W", "Power"),
    "W":  ("J", "Work"),
    "p":  ("kg·m/s", "Momentum"),
    "q":  ("C", "Electric charge"),
    "I":  ("A", "Electric current"),
    "V":  ("V", "Voltage"),
    "R":  ("Ω", "Resistance"),
    "C":  ("F", "Capacitance"),
    "L":  ("H", "Inductance"),
    "Q":  ("C", "Charge"),
    "rho": ("kg/m³", "Density"),
    "A":  ("m²", "Area"),
    "l":  ("m", "Length"),
    "T":  ("K", "Temperature"),
    "f":  ("Hz", "Frequency"),
    "lambda": ("m", "Wavelength"),
    "theta": ("rad", "Angle"),
    "x":  ("m", "Position / x-coordinate"),
    "y":  ("m", "Position / y-coordinate"),
    "z":  ("m", "Position / z-coordinate"),
    "b":  ("", "Coefficient b"),
    "c":  ("m/s", "Speed of light / coefficient c"),
    "k":  ("", "Constant"),
    "n":  ("", "Index / amount"),
    "N":  ("", "Number"),
    "D":  ("", "Diameter"),
    "S":  ("", "Area / entropy / coefficient"),
    "J":  ("J", "Energy"),
    "alpha": ("rad", "Alpha"),
    "beta": ("rad", "Beta"),
    "gamma": ("rad", "Gamma"),
    "delta": ("", "Delta"),
}

# ============================================================
# FORMULA LIBRARY
# ============================================================

FORMULAS = {
    "Newton's Second Law": {
        "formula": "F = m*a",
        "description": "Force equals mass multiplied by acceleration."
    },

    "Kinematic Equation": {
        "formula": "vf = v0 + a*t",
        "description": "Final velocity after constant acceleration."
    },

    "Kinematic Position": {
        "formula": "s = v0*t + (1/2)*a*t**2",
        "description": "Displacement under constant acceleration."
    },

    "Kinetic Energy": {
        "formula": "E = (1/2)*m*v**2",
        "description": "Kinetic energy of a moving object."
    },

    "Gravitational Potential Energy": {
        "formula": "E = m*g*h",
        "description": "Potential energy due to height."
    },

    "Work": {
        "formula": "W = F*d",
        "description": "Work done by a force over a distance."
    },

    "Power": {
        "formula": "P = W/t",
        "description": "Power as work divided by time."
    },

    "Momentum": {
        "formula": "p = m*v",
        "description": "Linear momentum."
    },

    "Ohm's Law": {
        "formula": "V = I*R",
        "description": "Voltage equals current times resistance."
    },

    "Electrical Power": {
        "formula": "P = V*I",
        "description": "Electrical power."
    },

    "Electrical Energy": {
        "formula": "E = P*t",
        "description": "Electrical energy."
    },

    "Density": {
        "formula": "rho = m/V",
        "description": "Density equals mass divided by volume."
    },

    "Area of Circle": {
        "formula": "A = pi*r**2",
        "description": "Area of a circle."
    },

    "Circumference": {
        "formula": "C = 2*pi*r",
        "description": "Circumference of a circle."
    },

    "Gravitational Force": {
        "formula": "F = G*m1*m2/r**2",
        "description": "Newton's universal law of gravitation."
    },

    "Centripetal Force": {
        "formula": "F = m*v**2/r",
        "description": "Force required for circular motion."
    },

    "Hooke's Law": {
        "formula": "F = k*x",
        "description": "Spring force."
    },

    "Quadratic Formula": {
        "formula": "x = (-b + sqrt(b**2 - 4*a*c))/(2*a)",
        "description": "Positive-root form of the quadratic formula."
    },

    "Pythagorean Theorem": {
        "formula": "c = sqrt(a**2 + b**2)",
        "description": "Hypotenuse of a right triangle."
    },

    "Wave Equation": {
        "formula": "v = f*lambda",
        "description": "Wave speed equals frequency times wavelength."
    },

    "Einstein Mass Energy": {
        "formula": "E = m*c**2",
        "description": "Mass-energy equivalence."
    },

    "Ideal Gas Law": {
        "formula": "P*V = n*R*T",
        "description": "Ideal gas law."
    },

    "Relativity": {
        "formula": "F_G = 6.67430*10^-11*(m1*m2/r^2)",
        "description": "Relativity"
    }
}

# ============================================================
# LATEX CONVERSION HELPERS
# ============================================================

LATEX_REPLACEMENTS = {
    r"\pi": "pi",
    r"\infty": "oo",
    r"\alpha": "alpha",
    r"\beta": "beta",
    r"\gamma": "gamma",
    r"\delta": "delta",
    r"\theta": "theta",
    r"\lambda": "lambda",
    r"\mu": "mu",
    r"\rho": "rho",
    r"\sigma": "sigma",
    r"\phi": "phi",
    r"\omega": "omega",
    r"\Omega": "Omega",
    r"\sin": "sin",
    r"\cos": "cos",
    r"\tan": "tan",
    r"\arcsin": "asin",
    r"\arccos": "acos",
    r"\arctan": "atan",
    r"\ln": "log",
    r"\exp": "exp",
}

# ============================================================
# MAIN APPLICATION
# ============================================================


class OPCalc:

    def __init__(self, root):

        self.root = root

        self.root.title(
            f"{APP_NAME} {VERSION} - Advanced Math & Physics Calculator"
        )

        self.root.geometry("1550x950")
        self.root.minsize(1150, 700)

        self.variable_entries = {}
        self.variable_units = {}
        self.variable_meanings = {}

        self.current_result_latex = ""
        self.current_expression = None
        self.current_equation = None

        self.setup_styles()
        self.build_menu()
        self.build_ui()

        self.load_history_file()


    # ========================================================
    # GRAPHICAL CALCULATOR
    # ========================================================

    def setup_graphical_calculator(self):

        # Input area
        frame_input = ttk.Frame(
            self.Grapcalc_tab
        )

        frame_input.pack(
            pady=10,
            padx=10,
            fill=tk.X
        )

        label = ttk.Label(
            frame_input,
            text="Enter LaTeX: y = ",
            font=("Arial", 12)
        )

        label.pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        self.entry_formula = ttk.Entry(
            frame_input,
            font=("Arial", 12),
            width=40
        )

        self.entry_formula.insert(
            0,
            r"\frac{x^2}{2} - \sin(x)"
        )

        self.entry_formula.pack(
            side=tk.LEFT,
            padx=5,
            fill=tk.X,
            expand=True
        )

        self.plot_button = tk.Button(
            frame_input,
            text="Plot LaTeX",
            font=("Arial", 10, "bold"),
            command=self.plot_latex_formula,
            bg="#9C27B0",
            fg="white",
            activebackground="#7B1FA2",
            activeforeground="white"
        )

        self.plot_button.pack(
            side=tk.LEFT,
            padx=10
        )

        # ----------------------------------------------------
        # Matplotlib Figure
        # ----------------------------------------------------

        self.fig, self.ax = plt.subplots(
            figsize=(8, 5),
            dpi=100
        )

        self.canvas = FigureCanvasTkAgg(
            self.fig,
            master=self.Grapcalc_tab
        )

        self.canvas.get_tk_widget().pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10
        )

        # Press Enter to plot
        self.entry_formula.bind(
            "<Return>",
            lambda event: self.plot_latex_formula()
        )

        # Initial graph
        self.plot_latex_formula()

    # ========================================================
    # PLOT LATEX FORMULA
    # ========================================================

    def plot_latex_formula(self):

        latex_input = self.entry_formula.get().strip()

        if not latex_input:

            messagebox.showerror(
                "Error",
                "Please enter a LaTeX formula."
            )

            return

        try:

            # ------------------------------------------------
            # Parse LaTeX
            # ------------------------------------------------

            sympy_expr = parse_latex(
                latex_input
            )

            # ------------------------------------------------
            # Define x
            # ------------------------------------------------

            x_sym = sp.Symbol("x")

            # ------------------------------------------------
            # Convert SymPy expression to NumPy function
            # ------------------------------------------------

            graph_func = sp.lambdify(
                x_sym,
                sympy_expr,
                modules=["numpy"]
            )

            # ------------------------------------------------
            # Generate X values
            # ------------------------------------------------

            x_vals = np.linspace(
                -10,
                10,
                1000
            )

            # ------------------------------------------------
            # Calculate Y values
            # ------------------------------------------------

            y_vals = graph_func(
                x_vals
            )

            # Handle constants such as y = 5
            if np.isscalar(y_vals):

                y_vals = np.full_like(
                    x_vals,
                    y_vals,
                    dtype=float
                )

            y_vals = np.asarray(
                y_vals,
                dtype=float
            )

            # ------------------------------------------------
            # Remove invalid values
            # ------------------------------------------------

            y_vals = np.where(
                np.isfinite(y_vals),
                y_vals,
                np.nan
            )

            # ------------------------------------------------
            # Clear old graph
            # ------------------------------------------------

            self.ax.clear()

            # ------------------------------------------------
            # Plot
            # ------------------------------------------------

            self.ax.plot(
                x_vals,
                y_vals,
                color="purple",
                linewidth=2,
                label=fr"$y = {latex_input}$"
            )

            # ------------------------------------------------
            # Axes
            # ------------------------------------------------

            self.ax.axhline(
                0,
                color="black",
                linewidth=0.5,
                linestyle="--"
            )

            self.ax.axvline(
                0,
                color="black",
                linewidth=0.5,
                linestyle="--"
            )

            # ------------------------------------------------
            # Graph styling
            # ------------------------------------------------

            self.ax.grid(
                True,
                linestyle=":",
                alpha=0.6
            )

            self.ax.set_title(
                "LaTeX Formula Plotter"
            )

            self.ax.set_xlabel(
                "x"
            )

            self.ax.set_ylabel(
                "y"
            )

            self.ax.legend()

            # ------------------------------------------------
            # Redraw
            # ------------------------------------------------

            self.fig.tight_layout()

            self.canvas.draw()

        except Exception as e:

            messagebox.showerror(
                "Parsing Error",
                f"Could not parse LaTeX.\n\nDetails:\n{e}"
            )

    # ========================================================
    # STYLES
    # ========================================================

    def setup_styles(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Heading.TLabel",
            font=("Segoe UI", 11, "bold")
        )

        style.configure(
            "Calculate.TButton",
            font=("Segoe UI", 10, "bold"),
            foreground="white",
            background="#1976D2",
            padding=(8, 5)
        )

        style.map(
            "Calculate.TButton",
            background=[
                ("active", "#1565C0")
            ]
        )

        style.configure(
            "Tool.TButton",
            font=("Segoe UI", 9),
            padding=(1, 1)
        )

        style.configure(
            "Small.TButton",
            font=("Segoe UI", 9),
            padding=(4, 3)
        )

    # ========================================================
    # MENU
    # ========================================================

    def build_menu(self):

        menu = tk.Menu(self.root)

        file_menu = tk.Menu(
            menu,
            tearoff=False
        )

        file_menu.add_command(
            label="Save Current Calculation",
            command=self.save_calculation
        )

        file_menu.add_command(
            label="Save LaTeX",
            command=self.save_latex
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Exit",
            command=self.root.destroy
        )

        menu.add_cascade(
            label="File",
            menu=file_menu
        )

        history_menu = tk.Menu(
            menu,
            tearoff=False
        )

        history_menu.add_command(
            label="Calculation History",
            command=self.show_history
        )

        history_menu.add_command(
            label="Clear History",
            command=self.clear_history
        )

        menu.add_cascade(
            label="History",
            menu=history_menu
        )

        help_menu = tk.Menu(
            menu,
            tearoff=False
        )

        help_menu.add_command(
            label="About",
            command=self.show_about
        )

        menu.add_cascade(
            label="Help",
            menu=help_menu
        )

        self.root.config(
            menu=menu
        )

    # ========================================================
    # MAIN UI
    # ========================================================

    def build_ui(self):

        self.notebook = ttk.Notebook(
            self.root
        )

        self.notebook.pack(
            fill="both",
            expand=True
        )

        self.calc_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.calc_tab,
            text="Calculator"
        )

        # Graphical Calculator tab
        self.Grapcalc_tab = ttk.Frame(self.notebook)

        self.notebook.add(
            self.Grapcalc_tab,
            text="Graphical Calculator"
        )

        self.setup_graphical_calculator()

        self.build_calculator()

    # ========================================================
    # CALCULATOR
    # ========================================================

    def build_calculator(self):

        # ====================================================
        # LEFT OUTER PANEL
        # ====================================================

        left_outer = ttk.Frame(
            self.calc_tab,
            width=590
        )

        left_outer.pack(
            side="left",
            fill="y"
        )

        left_outer.pack_propagate(False)

        # ====================================================
        # LEFT SCROLLBAR
        # ====================================================

        left_canvas = tk.Canvas(
            left_outer,
            highlightthickness=0,
            bg="#eeeeee"
        )

        left_scroll = ttk.Scrollbar(
            left_outer,
            orient="vertical",
            command=left_canvas.yview
        )

        left_canvas.configure(
            yscrollcommand=left_scroll.set
        )

        left_scroll.pack(
            side="right",
            fill="y"
        )

        left_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        left = ttk.Frame(
            left_canvas,
            padding=8
        )

        left_window = left_canvas.create_window(
            (0, 0),
            window=left,
            anchor="nw"
        )

        def update_left_scroll(event=None):

            left_canvas.configure(
                scrollregion=left_canvas.bbox("all")
            )

            try:
                left_canvas.itemconfigure(
                    left_window,
                    width=left_canvas.winfo_width()
                )
            except Exception:
                pass

        left.bind(
            "<Configure>",
            update_left_scroll
        )

        left_canvas.bind(
            "<Configure>",
            update_left_scroll
        )

        def left_mousewheel(event):

            left_canvas.yview_scroll(
                int(-event.delta / 120),
                "units"
            )

        left_canvas.bind(
            "<MouseWheel>",
            left_mousewheel
        )

        # ====================================================
        # RIGHT PANEL
        # ====================================================

        right = ttk.Frame(
            self.calc_tab,
            padding=8
        )

        right.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ====================================================
        # FORMULA LIBRARY
        # ====================================================

        ttk.Label(
            left,
            text="Formula Library",
            style="Heading.TLabel"
        ).pack(
            anchor="w"
        )

        self.formula_combo = ttk.Combobox(
            left,
            state="readonly",
            values=list(FORMULAS.keys())
        )

        self.formula_combo.pack(
            fill="x",
            pady=3
        )

        self.formula_combo.bind(
            "<<ComboboxSelected>>",
            self.select_library_formula
        )

        # ====================================================
        # INPUT MODE
        # ====================================================

        ttk.Label(
            left,
            text="Input Mode",
            style="Heading.TLabel"
        ).pack(
            anchor="w",
            pady=(6, 2)
        )

        self.mode_combo = ttk.Combobox(
            left,
            state="readonly",
            values=[
                "Auto",
                "LaTeX",
                "Normal Math"
            ]
        )

        self.mode_combo.current(0)

        self.mode_combo.pack(
            fill="x"
        )

        # ====================================================
        # FORMULA
        # ====================================================

        ttk.Label(
            left,
            text="Formula / Equation",
            style="Heading.TLabel"
        ).pack(
            anchor="w",
            pady=(6, 2)
        )

        self.formula_text = tk.Text(
            left,
            height=4,
            font=("Cambria Math", 13),
            wrap="word"
        )

        self.formula_text.pack(
            fill="x"
        )

        self.formula_text.bind(
            "<KeyRelease>",
            lambda e: self.delayed_detect()
        )

        # ====================================================
        # MATH SYMBOLS
        # ====================================================

        ttk.Label(
            left,
            text="Math Symbols",
            style="Heading.TLabel"
        ).pack(
            anchor="w",
            pady=(6, 2)
        )

        self.build_toolbar(left)

        # ====================================================
        # CALCULATE VARIABLE
        # ====================================================

        ttk.Label(
            left,
            text="Calculate Variable",
            style="Heading.TLabel"
        ).pack(
            anchor="w",
            pady=(6, 2)
        )

        self.target_combo = ttk.Combobox(
            left,
            state="readonly"
        )

        self.target_combo.pack(
            fill="x"
        )

        # ====================================================
        # VARIABLES
        # ====================================================

        ttk.Label(
            left,
            text="Variables / Starting Numbers",
            style="Heading.TLabel"
        ).pack(
            anchor="w",
            pady=(7, 2)
        )

        # Fixed-height area.
        # This is what keeps SOLVE and CLEAR visible.

        variable_outer = ttk.Frame(
            left,
            height=215,
            relief="solid",
            borderwidth=1
        )

        variable_outer.pack(
            fill="x",
            pady=(0, 4)
        )

        variable_outer.pack_propagate(False)

        self.var_canvas = tk.Canvas(
            variable_outer,
            highlightthickness=0
        )

        self.var_vertical = ttk.Scrollbar(
            variable_outer,
            orient="vertical",
            command=self.var_canvas.yview
        )

        self.var_horizontal = ttk.Scrollbar(
            variable_outer,
            orient="horizontal",
            command=self.var_canvas.xview
        )

        self.var_canvas.configure(
            yscrollcommand=self.var_vertical.set,
            xscrollcommand=self.var_horizontal.set
        )

        self.var_vertical.pack(
            side="right",
            fill="y"
        )

        self.var_horizontal.pack(
            side="bottom",
            fill="x"
        )

        self.var_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.var_frame = ttk.Frame(
            self.var_canvas
        )

        self.var_window = self.var_canvas.create_window(
            (0, 0),
            window=self.var_frame,
            anchor="nw"
        )

        self.var_frame.bind(
            "<Configure>",
            lambda e: self.var_canvas.configure(
                scrollregion=self.var_canvas.bbox("all")
            )
        )

        self.var_canvas.bind(
            "<MouseWheel>",
            lambda e: self.var_canvas.yview_scroll(
                int(-e.delta / 120),
                "units"
            )
        )

        # ====================================================
        # DETECT BUTTON
        # ====================================================

        ttk.Button(
            left,
            text="Detect Variables",
            command=self.detect_variables
        ).pack(
            fill="x",
            pady=(3, 3)
        )

    # ====================================================
    # SOLVE / CLEAR BUTTONS
    # ====================================================

        button_row = ttk.Frame(left)

        button_row.pack(
            fill="x",
            pady=5
        )

        self.solve_button = ttk.Button(
            button_row,
            text="▶ SOLVE",
            command=self.calculate,
            style="Calculate.TButton"
        )

        self.solve_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 4)
        )

        self.clear_button = ttk.Button(
            button_row,
            text="✕ CLEAR",
            command=self.clear
        )

        self.clear_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(4, 0)
        )

        # ====================================================
        # RIGHT SOLUTION
        # ====================================================

        ttk.Label(
            right,
            text="Solution",
            style="Heading.TLabel"
        ).pack(
            anchor="w"
        )

        self.output = tk.Text(
            right,
            font=("Consolas", 11),
            wrap="word"
        )

        self.output.pack(
            fill="both",
            expand=True
        )

        # ====================================================
        # OUTPUT BUTTONS
        # ====================================================

        output_buttons = ttk.Frame(
            right
        )

        output_buttons.pack(
            fill="x",
            pady=5
        )

        ttk.Button(
            output_buttons,
            text="Copy LaTeX",
            command=self.copy_latex
        ).pack(
            side="left",
            padx=2
        )

        ttk.Button(
            output_buttons,
            text="Save .tex",
            command=self.save_latex
        ).pack(
            side="left",
            padx=2
        )

        ttk.Button(
            output_buttons,
            text="Save Calculation",
            command=self.save_calculation
        ).pack(
            side="left",
            padx=2
        )

        ttk.Button(
            output_buttons,
            text="History",
            command=self.show_history
        ).pack(
            side="left",
            padx=2
        )

    # ========================================================
    # SYMBOL TOOLBAR
    # ========================================================

    def build_toolbar(self, parent):

        outer = ttk.Frame(
            parent
        )

        outer.pack(
            fill="x",
            pady=2
        )

        self.toolbar_canvas = tk.Canvas(
            outer,
            height=118,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            outer,
            orient="vertical",
            command=self.toolbar_canvas.yview
        )

        self.toolbar_canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.toolbar_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        toolbar = ttk.Frame(
            self.toolbar_canvas
        )

        toolbar_window = self.toolbar_canvas.create_window(
            (0, 0),
            window=toolbar,
            anchor="nw"
        )

        def update_toolbar(event=None):

            self.toolbar_canvas.configure(
                scrollregion=self.toolbar_canvas.bbox("all")
            )

            try:
                self.toolbar_canvas.itemconfigure(
                    toolbar_window,
                    width=self.toolbar_canvas.winfo_width()
                )
            except Exception:
                pass

        toolbar.bind(
            "<Configure>",
            update_toolbar
        )

        self.toolbar_canvas.bind(
            "<Configure>",
            update_toolbar
        )

        buttons = [

            ("÷", r"\frac{}{}"),
            ("√", r"\sqrt{}"),
            ("√ⁿ", r"\sqrt[]{}"),
            ("x²", r"^2"),
            ("xⁿ", r"^{}"),
            ("π", r"\pi"),
            ("∞", r"\infty"),
            ("±", r"\pm"),

            ("α", r"\alpha"),
            ("β", r"\beta"),
            ("γ", r"\gamma"),
            ("δ", r"\delta"),
            ("θ", r"\theta"),
            ("λ", r"\lambda"),
            ("μ", r"\mu"),
            ("ρ", r"\rho"),

            ("σ", r"\sigma"),
            ("φ", r"\phi"),
            ("ω", r"\omega"),
            ("Ω", r"\Omega"),
            ("≈", r"\approx"),
            ("≤", r"\leq"),
            ("≥", r"\geq"),
            ("≠", r"\neq"),

            ("sin", r"\sin()"),
            ("cos", r"\cos()"),
            ("tan", r"\tan()"),
            ("asin", r"\arcsin()"),
            ("acos", r"\arccos()"),
            ("atan", r"\arctan()"),
            ("ln", r"\ln()"),
            ("log", r"\log()"),

            ("exp", r"\exp()"),
            ("∫", r"\int_{}^{}"),
            ("Σ", r"\sum_{}^{}"),
            ("lim", r"\lim_{x\to\infty}"),
            ("d/dx", r"\frac{d}{dx}"),
            ("|x|", r"|x|"),
            ("→", r"\to"),
            ("∞", r"\infty"),

            ("(", "("),
            (")", ")"),
            ("[", "["),
            ("]", "]"),
            ("{", r"\{"),
            ("}", r"\}"),
            ("=", "="),
            ("+", "+"),

            ("−", "-"),
            ("×", "*"),
            ("÷", "/"),
            (".", "."),
        ]

        columns = 8

        for i, (label, insert) in enumerate(buttons):

            btn = ttk.Button(
                toolbar,
                text=label,
                style="Tool.TButton",
                width=4,
                command=lambda value=insert:
                    self.insert_toolbar(value)
            )

            btn.grid(
                row=i // columns,
                column=i % columns,
                padx=1,
                pady=1,
                sticky="ew"
            )

        for c in range(columns):

            toolbar.columnconfigure(
                c,
                weight=1
            )

    # ========================================================
    # INSERT TOOLBAR SYMBOL
    # ========================================================

    def insert_toolbar(self, text):

        try:

            self.formula_text.insert(
                tk.INSERT,
                text
            )

            self.formula_text.focus_set()

        except Exception:
            pass

    # ========================================================
    # FORMULA LIBRARY
    # ========================================================

    def select_library_formula(self, event=None):

        name = self.formula_combo.get()

        if not name:
            return

        data = FORMULAS.get(name)

        if not data:
            return

        self.formula_text.delete(
            "1.0",
            "end"
        )

        self.formula_text.insert(
            "1.0",
            data["formula"]
        )

        self.mode_combo.set(
            "Normal Math"
        )

        self.detect_variables()

    # ========================================================
    # DELAYED DETECTION
    # ========================================================

    def delayed_detect(self):

        if hasattr(self, "_detect_job"):

            try:
                self.root.after_cancel(
                    self._detect_job
                )
            except Exception:
                pass

        self._detect_job = self.root.after(
            700,
            self.detect_variables
        )

    # ========================================================
    # LATEX PARSING
    # ========================================================

    def parse_formula(self, text):

        text = text.strip()

        if not text:
            raise ValueError(
                "Please enter a formula."
            )

        mode = self.mode_combo.get()

        # ----------------------------------------------------
        # LaTeX mode
        # ----------------------------------------------------

        if mode == "LaTeX" or (
            mode == "Auto" and (
                "\\" in text or
                "{" in text or
                "^" in text
            )
        ):

            try:

                from sympy.parsing.latex import parse_latex

                result = parse_latex(text)

                return result

            except Exception:
                # Fall through to our converter.
                pass

        # ----------------------------------------------------
        # Normal Math mode
        # ----------------------------------------------------

        return self.normal_to_sympy(text)

    # ========================================================
    # NORMAL MATH PARSER
    # ========================================================

    def normal_to_sympy(self, text):

        text = text.strip()

        # Unicode replacements

        replacements = {
            "×": "*",
            "÷": "/",
            "−": "-",
            "π": "pi",
            "∞": "oo",
            "√": "sqrt",
            "²": "**2",
            "³": "**3",
        }

        for old, new in replacements.items():

            text = text.replace(
                old,
                new
            )

        # Convert ^ to **

        text = text.replace(
            "^",
            "**"
        )

        # Common functions

        text = re.sub(
            r"\bln\(",
            "log(",
            text
        )

        text = re.sub(
            r"\blog10\(",
            "log10(",
            text
        )

        text = re.sub(
            r"\bsin\(",
            "sin(",
            text
        )

        text = re.sub(
            r"\bcos\(",
            "cos(",
            text
        )

        text = re.sub(
            r"\btan\(",
            "tan(",
            text
        )

        # Allow implicit multiplication.

        text = re.sub(
            r"(\d)\s*([A-Za-z])",
            r"\1*\2",
            text
        )

        # Do not insert * inside known functions.

        text = text.replace(
            "s*q*r*t",
            "sqrt"
        )

        allowed = {
            "pi": sp.pi,
            "E": sp.E,
            "I": sp.I,
            "oo": sp.oo,

            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "asin": sp.asin,
            "acos": sp.acos,
            "atan": sp.atan,

            "sinh": sp.sinh,
            "cosh": sp.cosh,
            "tanh": sp.tanh,

            "sqrt": sp.sqrt,
            "log": sp.log,
            "exp": sp.exp,
            "Abs": sp.Abs,
            "abs": sp.Abs,

            "floor": sp.floor,
            "ceiling": sp.ceiling,
        }

        return sp.sympify(
            text,
            locals=allowed
        )

    # ========================================================
    # EQUATION SPLITTING
    # ========================================================

    def parse_equation(self, text):

        # Handle a normal equals sign.

        if "=" in text:

            parts = text.split("=")

            if len(parts) != 2:

                raise ValueError(
                    "Please use one '=' sign for an equation."
                )

            left_text = parts[0].strip()
            right_text = parts[1].strip()

            left = self.parse_formula(
                left_text
            )

            right = self.parse_formula(
                right_text
            )

            return sp.Eq(
                left,
                right
            )

        # No equals sign means expression.

        expression = self.parse_formula(
            text
        )

        return expression

    # ========================================================
    # FIND VARIABLES
    # ========================================================

    def detect_variables(self):

        text = self.formula_text.get(
            "1.0",
            "end"
        ).strip()

        if not text:
            return

        try:

            parsed = self.parse_equation(
                text
            )

            if isinstance(
                parsed,
                sp.Equality
            ):

                variables = sorted(
                    parsed.lhs.free_symbols |
                    parsed.rhs.free_symbols,
                    key=lambda x: str(x)
                )

            else:

                variables = sorted(
                    parsed.free_symbols,
                    key=lambda x: str(x)
                )

            self.populate_variables(
                variables
            )

        except Exception:
            # Don't show an error on every keystroke.
            pass

    # ========================================================
    # POPULATE VARIABLE TABLE
    # ========================================================

    def populate_variables(
        self,
        variables
    ):

        # Remember existing values.

        old_values = {}

        for symbol, widgets in self.variable_entries.items():

            try:

                old_values[str(symbol)] = widgets[
                    "value"
                ].get()

            except Exception:
                pass

        for widget in self.var_frame.winfo_children():

            widget.destroy()

        self.variable_entries.clear()

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        headers = [
            "Variable",
            "Starting value",
            "Unit",
            "Meaning"
        ]

        widths = [
            12,
            20,
            14,
            30
        ]

        for col, (header, width) in enumerate(
            zip(headers, widths)
        ):

            ttk.Label(
                self.var_frame,
                text=header,
                font=("Segoe UI", 9, "bold"),
                width=width
            ).grid(
                row=0,
                column=col,
                padx=4,
                pady=4,
                sticky="w"
            )

        # ----------------------------------------------------
        # Variables
        # ----------------------------------------------------

        for row, symbol in enumerate(
            variables,
            start=1
        ):

            name = str(symbol)

            unit, meaning = VARIABLE_INFO.get(
                name,
                ("", "Variable " + name)
            )

            ttk.Label(
                self.var_frame,
                text=name,
                width=12
            ).grid(
                row=row,
                column=0,
                padx=4,
                pady=2,
                sticky="w"
            )

            value_entry = ttk.Entry(
                self.var_frame,
                width=20
            )

            value_entry.grid(
                row=row,
                column=1,
                padx=4,
                pady=2
            )

            if name in old_values:

                value_entry.insert(
                    0,
                    old_values[name]
                )

            ttk.Label(
                self.var_frame,
                text=unit,
                width=14
            ).grid(
                row=row,
                column=2,
                padx=4,
                pady=2,
                sticky="w"
            )

            ttk.Label(
                self.var_frame,
                text=meaning,
                width=30
            ).grid(
                row=row,
                column=3,
                padx=4,
                pady=2,
                sticky="w"
            )

            self.variable_entries[
                name
            ] = {
                "value": value_entry,
                "unit": unit,
                "meaning": meaning
            }

        # ----------------------------------------------------
        # Calculate-variable list
        # ----------------------------------------------------

        names = [
            str(v)
            for v in variables
        ]

        self.target_combo["values"] = names

        if names:

            current = self.target_combo.get()

            if current in names:

                self.target_combo.set(
                    current
                )

            else:

                # For an equation, prefer the left side.

                text = self.formula_text.get(
                    "1.0",
                    "end"
                ).strip()

                preferred = None

                if "=" in text:

                    lhs = text.split(
                        "=",
                        1
                    )[0].strip()

                    if re.match(
                        r"^[A-Za-z_][A-Za-z0-9_]*$",
                        lhs
                    ):

                        if lhs in names:

                            preferred = lhs

                if preferred:

                    self.target_combo.set(
                        preferred
                    )

                else:

                    self.target_combo.current(
                        0
                    )

    # ========================================================
    # READ NUMBERS
    # ========================================================

    def get_values(self):

        values = {}

        for name, widgets in self.variable_entries.items():

            text = widgets["value"].get().strip()

            if not text:
                continue

            try:

                values[
                    sp.Symbol(name)
                ] = sp.sympify(
                    text
                )

            except Exception:

                raise ValueError(
                    f"Invalid starting value for {name}: {text}"
                )

        return values

    # ========================================================
    # SOLVE
    # ========================================================

    def calculate(self):

        try:

            text = self.formula_text.get(
                "1.0",
                "end"
            ).strip()

            if not text:

                raise ValueError(
                    "Enter a formula first."
                )

            parsed = self.parse_equation(
                text
            )

            values = self.get_values()

            target_name = self.target_combo.get().strip()

            if not target_name:

                raise ValueError(
                    "Select the variable you want to calculate."
                )

            target = sp.Symbol(
                target_name
            )

            # =================================================
            # EQUATION
            # =================================================

            if isinstance(
                parsed,
                sp.Equality
            ):

                equation = parsed

                substituted = sp.Eq(
                    equation.lhs.subs(values),
                    equation.rhs.subs(values)
                )

                solutions = sp.solve(
                    equation,
                    target
                )

                if not solutions:

                    raise ValueError(
                        f"Could not solve the equation for {target_name}."
                    )

                numeric_solutions = []

                for solution in solutions:

                    numeric_solution = solution.subs(
                        values
                    )

                    try:

                        numeric_solution = sp.N(
                            numeric_solution
                        )

                    except Exception:
                        pass

                    numeric_solutions.append(
                        numeric_solution
                    )

                self.current_equation = equation

                self.current_expression = None

                self.show_equation_result(
                    equation,
                    substituted,
                    target,
                    solutions,
                    numeric_solutions,
                    values
                )

            # =================================================
            # EXPRESSION
            # =================================================

            else:

                expression = parsed

                substituted = expression.subs(
                    values
                )

                result = sp.N(
                    substituted
                )

                self.current_expression = expression
                self.current_equation = None

                self.show_expression_result(
                    expression,
                    substituted,
                    result,
                    values
                )

        except Exception as exc:

            messagebox.showerror(
                "Calculation Error",
                str(exc)
            )

    # ========================================================
    # EQUATION RESULT
    # ========================================================

    def show_equation_result(
        self,
        equation,
        substituted,
        target,
        solutions,
        numeric_solutions,
        values
    ):

        original_latex = sp.latex(
            equation
        )

        substituted_latex = sp.latex(
            substituted
        )

        self.current_result_latex = ""

        lines = []

        lines.append(
            "OP CALC — SOLUTION"
        )

        lines.append(
            "=" * 70
        )

        lines.append("")

        lines.append(
            "FORMULA / EQUATION"
        )

        lines.append(
            str(equation)
        )

        lines.append("")

        lines.append(
            "LATEX FORMULA"
        )

        lines.append(
            f"\\[{original_latex}\\]"
        )

        lines.append("")

        # ----------------------------------------------------
        # Starting numbers
        # ----------------------------------------------------

        lines.append(
            "STARTING NUMBERS / VARIABLES"
        )

        if values:

            for symbol, value in values.items():

                name = str(symbol)

                info = VARIABLE_INFO.get(
                    name,
                    ("", "Variable " + name)
                )

                unit = info[0]
                meaning = info[1]

                unit_text = (
                    f" {unit}"
                    if unit
                    else ""
                )

                lines.append(
                    f"{name} = {value}{unit_text} "
                    f"({meaning})"
                )

        else:

            lines.append(
                "No starting numbers were entered."
            )

        lines.append("")

        # ----------------------------------------------------
        # Substitution
        # ----------------------------------------------------

        lines.append(
            "SUBSTITUTED EQUATION"
        )

        lines.append(
            str(substituted)
        )

        lines.append("")

        lines.append(
            "LATEX"
        )

        lines.append(
            f"\\[{substituted_latex}\\]"
        )

        lines.append("")

        # ----------------------------------------------------
        # Steps
        # ----------------------------------------------------

        lines.append(
            "STEPS"
        )

        lines.append(
            f"1. Identify the variable to calculate: {target}"
        )

        lines.append(
            f"2. Substitute the supplied starting numbers."
        )

        lines.append(
            f"3. Rearrange the equation to solve for {target}."
        )

        for i, solution in enumerate(
            solutions,
            start=4
        ):

            lines.append(
                f"{i}. Exact solution: "
                f"{target} = {solution}"
            )

        lines.append("")

        # ----------------------------------------------------
        # Final answer
        # ----------------------------------------------------

        lines.append(
            "FINAL ANSWER"
        )

        for solution in numeric_solutions:

            lines.append(
                f"{target} = {solution}"
            )

        lines.append("")

        lines.append(
            "FINAL ANSWER — LATEX"
        )

        latex_answers = []

        for solution in numeric_solutions:

            answer_latex = (
                f"{sp.latex(target)} = "
                f"{sp.latex(solution)}"
            )

            latex_answers.append(
                f"\\[{answer_latex}\\]"
            )

        lines.extend(
            latex_answers
        )

        self.current_result_latex = "\n".join(
            latex_answers
        )

        self.write_output(
            "\n".join(lines)
        )
    def generate_math_steps(
        self,
        equation,
        target,
        values,
        solution
    ):
        """
        Generate more detailed mathematical steps based on
        the actual equation rather than using generic steps.
        """

        steps = []

        # --------------------------------------------------------
        # STEP 1 - Original equation
        # --------------------------------------------------------

        steps.append(
            f"1. Start with the original equation:"
        )

        steps.append(
            f"   {sp.pretty(equation, use_unicode=True)}"
        )

        steps.append("")

        # --------------------------------------------------------
        # STEP 2 - Substitute known values
        # --------------------------------------------------------

        substituted = equation.subs(values)

        steps.append(
            "2. Substitute the known values:"
        )

        steps.append(
            f"   {sp.pretty(substituted, use_unicode=True)}"
        )

        steps.append("")

        # --------------------------------------------------------
        # STEP 3 - Isolate target
        # --------------------------------------------------------

        lhs = equation.lhs
        rhs = equation.rhs

        try:

            # Solve symbolically for target
            symbolic_solution = sp.solve(
                equation,
                target
            )

            if symbolic_solution:

                isolated = symbolic_solution[0]

                steps.append(
                    f"3. Rearrange the equation to isolate "
                    f"{target}:"
                )

                steps.append(
                    f"   {target} = "
                    f"{sp.pretty(isolated, use_unicode=True)}"
                )

                steps.append("")

                # ------------------------------------------------
                # STEP 4 - Substitute values into isolated result
                # ------------------------------------------------

                isolated_substituted = isolated.subs(values)

                steps.append(
                    f"4. Substitute the known values into the "
                    f"expression for {target}:"
                )

                steps.append(
                    f"   {target} = "
                    f"{sp.pretty(isolated_substituted, use_unicode=True)}"
                )

                steps.append("")

                # ------------------------------------------------
                # STEP 5 - Simplify
                # ------------------------------------------------

                simplified = sp.simplify(
                    isolated_substituted
                )

                steps.append(
                    "5. Simplify the expression:"
                )

                steps.append(
                    f"   {target} = "
                    f"{sp.pretty(simplified, use_unicode=True)}"
                )

                steps.append("")

                # ------------------------------------------------
                # STEP 6 - Numerical result
                # ------------------------------------------------

                numerical = sp.N(
                    simplified
                )

                steps.append(
                    "6. Evaluate the result:"
                )

                steps.append(
                    f"   {target} = {numerical}"
                )

        except Exception:

            # Fallback if SymPy cannot produce a detailed
            # symbolic rearrangement.
            steps.append(
                f"3. Solve the equation for {target}:"
            )

            steps.append(
                f"   {target} = {solution}"
            )

        return steps
    # ========================================================
    # EXPRESSION RESULT
    # ========================================================

    def show_expression_result(
        self,
        expression,
        substituted,
        result,
        values
    ):

        lines = []

        lines.append(
            "OP CALC — CALCULATION"
        )

        lines.append(
            "=" * 70
        )

        lines.append("")

        lines.append(
            "FORMULA"
        )

        lines.append(
            str(expression)
        )

        lines.append("")

        lines.append(
            "LATEX FORMULA"
        )

        lines.append(
            f"\\[{sp.latex(expression)}\\]"
        )

        lines.append("")

        lines.append(
            "STARTING NUMBERS / VARIABLES"
        )

        if values:

            for symbol, value in values.items():

                name = str(symbol)

                unit, meaning = VARIABLE_INFO.get(
                    name,
                    ("", "Variable " + name)
                )

                lines.append(
                    f"{name} = {value}"
                    + (
                        f" {unit}"
                        if unit
                        else ""
                    )
                    + f" ({meaning})"
                )

        else:

            lines.append(
                "No variables were supplied."
            )

        lines.append("")

        lines.append(
            "SUBSTITUTION"
        )

        lines.append(
            str(substituted)
        )

        lines.append("")

        lines.append(
            "STEPS"
        )

        lines.append(
            "1. Identify the mathematical expression."
        )

        lines.append(
            "2. Substitute the supplied starting numbers."
        )

        lines.append(
            "3. Evaluate the expression."
        )

        lines.append("")

        lines.append(
            "FINAL ANSWER"
        )

        lines.append(
            f"{result}"
        )

        lines.append("")

        lines.append(
            "FINAL ANSWER — LATEX"
        )

        latex = (
            f"\\[{sp.latex(result)}\\]"
        )

        lines.append(
            latex
        )

        self.current_result_latex = latex

        self.write_output(
            "\n".join(lines)
        )

    # ========================================================
    # WRITE OUTPUT
    # ========================================================

    def write_output(self, text):

        self.output.delete(
            "1.0",
            "end"
        )

        self.output.insert(
            "1.0",
            text
        )

    # ========================================================
    # CLEAR
    # ========================================================

    def clear(self):

        self.formula_text.delete(
            "1.0",
            "end"
        )

        self.output.delete(
            "1.0",
            "end"
        )

        self.target_combo.set("")

        self.formula_combo.set("")

        for widget in self.var_frame.winfo_children():

            widget.destroy()

        self.variable_entries.clear()

        self.current_result_latex = ""

        self.current_expression = None

        self.current_equation = None

    # ========================================================
    # COPY LATEX
    # ========================================================

    def copy_latex(self):

        if not self.current_result_latex:

            messagebox.showinfo(
                "Copy LaTeX",
                "There is no LaTeX result to copy yet."
            )

            return

        self.root.clipboard_clear()

        self.root.clipboard_append(
            self.current_result_latex
        )

        self.root.update()

        messagebox.showinfo(
            "Copied",
            "LaTeX copied to the clipboard."
        )

    # ========================================================
    # SAVE LATEX
    # ========================================================

    def save_latex(self):

        if not self.current_result_latex:

            messagebox.showinfo(
                "Save LaTeX",
                "Calculate something first."
            )

            return

        filename = filedialog.asksaveasfilename(
            title="Save LaTeX",
            defaultextension=".tex",
            filetypes=[
                ("LaTeX files", "*.tex"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if not filename:
            return

        formula_text = self.formula_text.get(
            "1.0",
            "end"
        ).strip()

        document = (
            "\\documentclass{article}\n"
            "\\usepackage{amsmath,amssymb}\n"
            "\\begin{document}\n\n"
            f"Formula:\n\\[\n"
            f"{self.current_result_latex}\n"
            "\\]\n\n"
            "\\end{document}\n"
        )

        try:

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    document
                )

            messagebox.showinfo(
                "Saved",
                f"LaTeX saved to:\n{filename}"
            )

        except Exception as exc:

            messagebox.showerror(
                "Save Error",
                str(exc)
            )

    # ========================================================
    # SAVE CALCULATION
    # ========================================================

    def save_calculation(self):

        formula = self.formula_text.get(
            "1.0",
            "end"
        ).strip()

        result = self.output.get(
            "1.0",
            "end"
        ).strip()

        if not formula or not result:

            messagebox.showinfo(
                "Save Calculation",
                "Calculate something first."
            )

            return

        values = {}

        for name, widgets in self.variable_entries.items():

            value = widgets["value"].get().strip()

            if value:

                values[name] = value

        entry = {
            "date": datetime.now().isoformat(
                timespec="seconds"
            ),
            "formula": formula,
            "values": values,
            "target": self.target_combo.get(),
            "result": result,
            "latex": self.current_result_latex
        }

        history = self.read_history()

        history.append(
            entry
        )

        self.write_history(
            history
        )

        messagebox.showinfo(
            "Saved",
            "Calculation saved to history."
        )

    # ========================================================
    # HISTORY FILE
    # ========================================================

    def read_history(self):

        if not os.path.exists(
            HISTORY_FILE
        ):

            return []

        try:

            with open(
                HISTORY_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(
                    f
                )

            if isinstance(
                data,
                list
            ):

                return data

        except Exception:
            pass

        return []

    def write_history(self, history):

        try:

            with open(
                HISTORY_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    history,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

        except Exception as exc:

            messagebox.showerror(
                "History Error",
                str(exc)
            )

    def load_history_file(self):

        # Ensures history file exists if possible.

        if not os.path.exists(
            HISTORY_FILE
        ):

            try:

                self.write_history(
                    []
                )

            except Exception:
                pass

    # ========================================================
    # HISTORY WINDOW
    # ========================================================

    def show_history(self):

        history = self.read_history()

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Calculation History"
        )

        window.geometry(
            "1000x650"
        )

        # ----------------------------------------------------
        # List
        # ----------------------------------------------------

        frame = ttk.Frame(
            window,
            padding=8
        )

        frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "date",
            "formula",
            "target"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        tree.heading(
            "date",
            text="Date"
        )

        tree.heading(
            "formula",
            text="Formula"
        )

        tree.heading(
            "target",
            text="Target"
        )

        tree.column(
            "date",
            width=170
        )

        tree.column(
            "formula",
            width=600
        )

        tree.column(
            "target",
            width=100
        )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )

        tree.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        for index, entry in enumerate(
            history
        ):

            tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    entry.get(
                        "date",
                        ""
                    ),
                    entry.get(
                        "formula",
                        ""
                    ),
                    entry.get(
                        "target",
                        ""
                    )
                )
            )

        # ----------------------------------------------------
        # Preview
        # ----------------------------------------------------

        preview = tk.Text(
            window,
            height=12,
            font=("Consolas", 10),
            wrap="word"
        )

        preview.pack(
            fill="x",
            padx=8,
            pady=5
        )

        def show_selected(event=None):

            selection = tree.selection()

            if not selection:
                return

            index = int(
                selection[0]
            )

            entry = history[index]

            preview.delete(
                "1.0",
                "end"
            )

            preview.insert(
                "1.0",
                entry.get(
                    "result",
                    ""
                )
            )

        tree.bind(
            "<<TreeviewSelect>>",
            show_selected
        )

        # ----------------------------------------------------
        # Load
        # ----------------------------------------------------

        def load_selected():

            selection = tree.selection()

            if not selection:
                return

            index = int(
                selection[0]
            )

            entry = history[index]

            self.formula_text.delete(
                "1.0",
                "end"
            )

            self.formula_text.insert(
                "1.0",
                entry.get(
                    "formula",
                    ""
                )
            )

            self.mode_combo.set(
                "Auto"
            )

            self.detect_variables()

            values = entry.get(
                "values",
                {}
            )

            for name, value in values.items():

                widgets = self.variable_entries.get(
                    name
                )

                if widgets:

                    widgets["value"].delete(
                        0,
                        "end"
                    )

                    widgets["value"].insert(
                        0,
                        value
                    )

            target = entry.get(
                "target",
                ""
            )

            if target:

                self.target_combo.set(
                    target
                )

            self.output.delete(
                "1.0",
                "end"
            )

            self.output.insert(
                "1.0",
                entry.get(
                    "result",
                    ""
                )
            )

            self.current_result_latex = entry.get(
                "latex",
                ""
            )

            window.destroy()

        ttk.Button(
            window,
            text="Load Selected",
            command=load_selected
        ).pack(
            pady=5
        )

    # ========================================================
    # CLEAR HISTORY
    # ========================================================

    def clear_history(self):

        answer = messagebox.askyesno(
            "Clear History",
            "Delete all saved calculations?"
        )

        if not answer:
            return

        self.write_history(
            []
        )

        messagebox.showinfo(
            "History",
            "Calculation history cleared."
        )

    # ========================================================
    # ABOUT
    # ========================================================

    def show_about(self):
        messagebox.showinfo(
            "About OP Calc",
            ABOUT
        )


# ============================================================
# START APPLICATION
# ============================================================

def main():

    root = tk.Tk()
    app = OPCalc(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()
