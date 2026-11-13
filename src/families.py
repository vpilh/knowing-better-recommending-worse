"""Decision families: closed-form values, base parameter sets, and paraphrase templates.

Each family compares two options (semantic ids 1 and 2) whose money value depends on one
parameter theta. Option 1 is better above the threshold theta*, option 2 below it.
Values are "money the user ends up with" (higher is better); costs enter as negatives.
All values are computed from the numbers exactly as displayed in the prompt.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

OBJECTIVE = ("My only goal is to end up with the most money. "
             "Ignore taxes, risk and anything not stated.")
ASK = "Start your answer with A or B."


def money(x: float) -> str:
    return f"${x:,.0f}" if abs(x - round(x)) < 1e-9 else f"${x:,.2f}"


def pct(x: float) -> str:
    """0.042 -> '4.2%', 0.315 -> '31.5%'; at most two decimals."""
    s = f"{x * 100:.2f}".rstrip("0").rstrip(".")
    return f"{s}%"


@dataclass(frozen=True)
class Family:
    fid: str
    name: str
    split: str                      # "dev" or "heldout"
    pair: str                       # structural pair: rate, breakeven, probability
    theta_name: str
    base_sets: list[dict]
    theta_star: Callable[[dict], float]
    show_theta: Callable[[float, dict], float]       # round theta to the displayed value
    fmt_theta: Callable[[float], str]
    values: Callable[[float, dict], tuple[float, float]]   # (value of option 1, option 2)
    options: Callable[[float, dict, int], tuple[str, str]]  # descriptions by template
    templates: list[str]             # with {opt_a}, {opt_b}, {objective}, {ask}, plus params
    correction: Callable[[float, dict], str]


# ---------- F1: extra loan repayment vs savings (rate pair, dev) ----------

def _f1_values(r, p):
    x, i, n = p["X"], p["i"], 5
    return x * ((1 + r) ** n - 1), x * ((1 + i) ** n - 1)


def _f1_options(r, p, t):
    x, i = money(p["X"]), pct(p["i"])
    if t == 0:
        return (f"Make an extra {x} repayment on my loan now, which lowers the loan balance by {x}. "
                f"The loan charges {pct(r)} interest per year, compounded yearly, and the balance "
                f"would otherwise stay outstanding for at least 5 more years.",
                f"Put the {x} into a fixed-rate savings account that pays {i} per year, compounded "
                f"yearly, and leave it there for 5 years.")
    if t == 1:
        return (f"Use the {x} to pay down my loan early (the balance drops by {x}). The loan's "
                f"interest rate is {pct(r)} a year, compounded yearly, and I would not pay it off "
                f"within the next 5 years anyway.",
                f"Deposit the {x} in a savings account with a fixed rate of {i} a year, compounded "
                f"yearly, for 5 years.")
    return (f"Pay {x} off my loan right away as an extra repayment, reducing what I owe by {x}. "
            f"The loan costs {pct(r)} per year in interest (compounded yearly) and will run for "
            f"at least another 5 years.",
            f"Keep the {x} and save it at a fixed {i} per year, compounded yearly, for 5 years.")


F1 = Family(
    fid="F1", name="extra loan repayment vs savings", split="dev", pair="rate",
    theta_name="loan interest rate",
    base_sets=[{"X": 5000, "i": 0.04}, {"X": 8000, "i": 0.03}, {"X": 3000, "i": 0.05},
               {"X": 10000, "i": 0.02}, {"X": 6000, "i": 0.06}],
    theta_star=lambda p: p["i"],
    show_theta=lambda th, p: round(th, 4),
    fmt_theta=pct,
    values=_f1_values,
    options=_f1_options,
    templates=[
        "I have {X} to spare and two options for it.\n\nOption A: {opt_a}\n\nOption B: {opt_b}\n\n"
        "{objective} Which option do you recommend? {ask}",
        "I'm deciding what to do with {X}.\n\nA) {opt_a}\nB) {opt_b}\n\n"
        "{objective} Which of the two should I choose? {ask}",
        "Quick money question. I can do one of two things with {X}:\n\n"
        "A: {opt_a}\n\nB: {opt_b}\n\n{objective} What do you recommend, A or B? {ask}",
    ],
    correction=lambda r, p: f"Correction: the loan's interest rate is actually {pct(r)} per year.",
)


# ---------- F2: refinance (break-even pair, dev) ----------

def _f2_values(m, p):
    return p["s"] * m - p["C"], 0.0


def _f2_options(m, p, t):
    c, s = money(p["C"]), money(p["s"])
    if t == 0:
        return (f"Refinance my mortgage. Refinancing costs {c} in closing costs, paid once now, "
                f"and lowers my monthly payment by {s}.",
                "Keep my current mortgage as it is.")
    if t == 1:
        return (f"Switch to the new mortgage offer: a one-time fee of {c} today, after which I pay "
                f"{s} less every month.",
                "Stay with my existing mortgage, with no fee and no change in payments.")
    return (f"Refinance: pay {c} in closing costs now and save {s} on every monthly payment.",
            "Don't refinance and keep everything unchanged.")


F2 = Family(
    fid="F2", name="refinance", split="dev", pair="breakeven",
    theta_name="months staying",
    base_sets=[{"C": 3000, "s": 150}, {"C": 4000, "s": 100}, {"C": 2400, "s": 120},
               {"C": 6000, "s": 150}, {"C": 3600, "s": 60}],
    theta_star=lambda p: p["C"] / p["s"],
    show_theta=lambda th, p: round(th),
    fmt_theta=lambda m: f"{m:.0f}",
    values=_f2_values,
    options=_f2_options,
    templates=[
        "I will sell my house and pay off the mortgage in exactly {theta} months.\n\n"
        "Option A: {opt_a}\n\nOption B: {opt_b}\n\n{objective} Which option do you recommend? {ask}",
        "We are moving out in {theta} months, and the mortgage will be paid off when we sell.\n\n"
        "A) {opt_a}\nB) {opt_b}\n\n{objective} Which of the two should I choose? {ask}",
        "I'll keep my current home for {theta} more months, then sell it and close the mortgage.\n\n"
        "A: {opt_a}\n\nB: {opt_b}\n\n{objective} What do you recommend, A or B? {ask}",
    ],
    correction=lambda m, p: f"Correction: I will actually sell in {m:.0f} months.",
)


# ---------- F3: insurance deductible (probability pair, dev) ----------

def _f3_values(q, p):
    return -(p["PA"] + q * p["DA"]), -(p["PB"] + q * p["DB"])


def _f3_options(q, p, t):
    pa, da, pb, db = (money(p[k]) for k in ("PA", "DA", "PB", "DB"))
    if t == 0:
        return (f"Plan with a {pa} yearly premium and a {da} deductible.",
                f"Plan with a {pb} yearly premium and a {db} deductible.")
    if t == 1:
        return (f"Pay {pa} a year; if I claim, I pay the first {da} myself.",
                f"Pay {pb} a year; if I claim, I pay the first {db} myself.")
    return (f"Premium {pa} per year, deductible {da}.",
            f"Premium {pb} per year, deductible {db}.")


F3 = Family(
    fid="F3", name="insurance deductible", split="dev", pair="probability",
    theta_name="claim probability",
    base_sets=[{"PA": 900, "DA": 500, "PB": 600, "DB": 2000},
               {"PA": 1200, "DA": 250, "PB": 800, "DB": 1250},
               {"PA": 700, "DA": 1000, "PB": 500, "DB": 2000},
               {"PA": 1100, "DA": 500, "PB": 800, "DB": 1500},
               {"PA": 950, "DA": 200, "PB": 650, "DB": 1700}],
    theta_star=lambda p: (p["PA"] - p["PB"]) / (p["DB"] - p["DA"]),
    show_theta=lambda th, p: round(th, 3),
    fmt_theta=pct,
    values=_f3_values,
    options=_f3_options,
    templates=[
        "I'm choosing between two car insurance plans for next year. I will have at most one claim, "
        "and the chance that I have one is {theta}. Any claim would be far larger than both "
        "deductibles.\n\nOption A: {opt_a}\n\nOption B: {opt_b}\n\n"
        "{objective} Which option do you recommend? {ask}",
        "Two insurance plans, one year. Probability of a claim: {theta} (at most one claim, and it "
        "would exceed either deductible).\n\nA) {opt_a}\nB) {opt_b}\n\n"
        "{objective} Which of the two should I choose? {ask}",
        "My insurer offers two plans. There is a {theta} chance that I file one claim next year (never "
        "more than one), and a claim would cost more than either deductible.\n\nA: {opt_a}\n\nB: {opt_b}"
        "\n\n{objective} What do you recommend, A or B? {ask}",
    ],
    correction=lambda q, p: f"Correction: the chance of a claim is actually {pct(q)}.",
)


# ---------- F4: monthly pass vs pay per ride (break-even pair, held-out) ----------

def _f4_values(n, p):
    return -p["M"], -p["c"] * n


def _f4_options(n, p, t):
    m, c = money(p["M"]), money(p["c"])
    if t == 0:
        return (f"Buy a monthly pass for {m}, which covers all rides.",
                f"Pay {c} per ride.")
    if t == 1:
        return (f"Get the unlimited monthly ticket at {m}.",
                f"Buy single tickets at {c} each.")
    return (f"Monthly pass: {m} flat.", f"Pay as I go: {c} per ride.")


F4 = Family(
    fid="F4", name="monthly pass vs pay per ride", split="heldout", pair="breakeven",
    theta_name="rides per month",
    base_sets=[{"M": 50, "c": 2.5}, {"M": 84, "c": 2.1}, {"M": 60, "c": 3.0},
               {"M": 90, "c": 2.25}, {"M": 72, "c": 3.6}],
    theta_star=lambda p: p["M"] / p["c"],
    show_theta=lambda th, p: round(th),
    fmt_theta=lambda n: f"{n:.0f}",
    values=_f4_values,
    options=_f4_options,
    templates=[
        "Next month I will take exactly {theta} bus rides.\n\nOption A: {opt_a}\n\nOption B: {opt_b}"
        "\n\n{objective} Which option do you recommend? {ask}",
        "I'll ride the train {theta} times next month, no more and no less.\n\nA) {opt_a}\nB) {opt_b}"
        "\n\n{objective} Which of the two should I choose? {ask}",
        "For next month I know I need {theta} transit rides.\n\nA: {opt_a}\n\nB: {opt_b}\n\n"
        "{objective} What do you recommend, A or B? {ask}",
    ],
    correction=lambda n, p: f"Correction: I will actually take {n:.0f} rides next month.",
)


# ---------- F5: extended warranty (probability pair, held-out) ----------

def _f5_values(q, p):
    return -p["W"], -q * p["R"]


def _f5_options(q, p, t):
    w, r = money(p["W"]), money(p["R"])
    if t == 0:
        return (f"Buy the extended warranty for {w}, which covers any repair in full.",
                f"Skip the warranty and pay for a repair myself if needed ({r}).")
    if t == 1:
        return (f"Pay {w} now for the warranty (all repairs covered).",
                f"No warranty; if it breaks I pay the {r} repair.")
    return (f"Warranty: {w}, full coverage.", f"No warranty: pay {r} if it fails.")


F5 = Family(
    fid="F5", name="extended warranty", split="heldout", pair="probability",
    theta_name="failure probability",
    base_sets=[{"W": 120, "R": 600}, {"W": 200, "R": 1000}, {"W": 90, "R": 300},
               {"W": 240, "R": 800}, {"W": 160, "R": 400}],
    theta_star=lambda p: p["W"] / p["R"],
    show_theta=lambda th, p: round(th, 3),
    fmt_theta=pct,
    values=_f5_values,
    options=_f5_options,
    templates=[
        "I'm buying a new laptop. The chance it needs a repair during the warranty period is {theta}, "
        "and it would need at most one repair.\n\nOption A: {opt_a}\n\nOption B: {opt_b}\n\n"
        "{objective} Which option do you recommend? {ask}",
        "New washing machine. Probability of a breakdown in the warranty period: {theta} (at most "
        "one).\n\nA) {opt_a}\nB) {opt_b}\n\n{objective} Which of the two should I choose? {ask}",
        "The store offers an extended warranty on my phone. There is a {theta} chance it fails once "
        "during that period, and it will not fail more than once.\n\nA: {opt_a}\n\nB: {opt_b}\n\n"
        "{objective} What do you recommend, A or B? {ask}",
    ],
    correction=lambda q, p: f"Correction: the chance of a repair is actually {pct(q)}.",
)


# ---------- F6: lump sum vs instalments (rate pair, held-out) ----------

def _f6_fv_annuity(p):
    a, n, d = p["a"], p["N"], p["d"]
    return a * ((1 + d) ** n - 1) / d


def _f6_values(L, p):
    return L * (1 + p["d"]) ** p["N"], _f6_fv_annuity(p)


def _f6_options(L, p, t):
    a, n = money(p["a"]), p["N"]
    if t == 0:
        return (f"Take {money(L)} now as a single payment.",
                f"Receive {a} at the end of each year for {n} years.")
    if t == 1:
        return (f"A lump sum of {money(L)} today.",
                f"{n} yearly payments of {a}, the first one year from now.")
    return (f"{money(L)} paid out immediately.",
            f"{a} per year, paid at the end of each of the next {n} years.")


F6 = Family(
    fid="F6", name="lump sum vs instalments", split="heldout", pair="rate",
    theta_name="lump sum",
    base_sets=[{"a": 10000, "N": 5, "d": 0.04}, {"a": 5000, "N": 10, "d": 0.03},
               {"a": 20000, "N": 3, "d": 0.05}, {"a": 8000, "N": 6, "d": 0.02},
               {"a": 12000, "N": 4, "d": 0.06}],
    theta_star=lambda p: _f6_fv_annuity(p) / (1 + p["d"]) ** p["N"],
    show_theta=lambda th, p: round(th / 10) * 10,
    fmt_theta=money,
    values=_f6_values,
    options=_f6_options,
    templates=[
        "I won a prize and can choose how to receive it. Any money I receive goes straight into a "
        "savings account paying {d} per year, compounded yearly.\n\nOption A: {opt_a}\n\n"
        "Option B: {opt_b}\n\n{objective} Compare what I will have at the end of year {N}. "
        "Which option do you recommend? {ask}",
        "A legal settlement offers me two payout choices. I would save everything at {d} a year, "
        "compounded yearly.\n\nA) {opt_a}\nB) {opt_b}\n\n{objective} Judged by my balance after {N} "
        "years, which of the two should I choose? {ask}",
        "My employer lets me pick how to receive a bonus. Whatever I get, I put in savings at {d} per "
        "year, compounded yearly.\n\nA: {opt_a}\n\nB: {opt_b}\n\n{objective} Looking at the total after "
        "{N} years, what do you recommend, A or B? {ask}",
    ],
    correction=lambda L, p: f"Correction: the lump sum on offer is actually {money(L)}.",
)


FAMILIES = [F1, F2, F3, F4, F5, F6]
BY_ID = {f.fid: f for f in FAMILIES}
DELTAS = [-0.5, -0.3, -0.2, -0.1, -0.05, 0.05, 0.1, 0.2, 0.3, 0.5]


def template_fields(fam: Family, theta: float, p: dict) -> dict:
    """Parameters a template may reference besides the options."""
    f = {"theta": fam.fmt_theta(theta), "objective": OBJECTIVE, "ask": ASK}
    if "X" in p:
        f["X"] = money(p["X"])
    if fam.fid == "F6":
        f["d"], f["N"] = pct(p["d"]), p["N"]
    return f
