"""Independent re-computation of selected months, written from the assumptions in the user
manual (section 10) WITHOUT importing the model. Uses Python's decimal module and explicit
arithmetic a person could follow with a calculator. Compares with the engine at the end.

Usage: python benchmark/hand_check.py
"""
from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from decimal import Decimal as D, getcontext
getcontext().prec = 28

# ---- Base case, typed in by hand -------------------------------------------
land, land_month = D("20"), 1
approval, ap_start, ap_end = D("3"), 1, 3
area, ccost = D("100000"), D("3000")
c_start, c_end = 4, 30
price = D("7500")
s_start, s_end = 7, 30
booking, inst = D("0.20"), 6
mkt = D("0.02")
debt_pct, rate, sweep = D("0.50"), D("0.12"), D("0.50")
tax_rate, disc = D("0.25"), D("0.15")
N = 36

constr_total = area * ccost / D(10**7)     # 30 cr
revenue = area * price / D(10**7)          # 75 cr
rm = (D(1) + disc) ** (D(1) / D(12)) - D(1)


def smooth(k, dur):
    x = D(k) / D(dur)
    return 3 * x**2 - 2 * x**3


def land_t(t): return land if t == land_month else D(0)
def approval_t(t): return approval / D(ap_end - ap_start + 1) if ap_start <= t <= ap_end else D(0)
def constr_t(t):
    if t < c_start or t > c_end: return D(0)
    dur = c_end - c_start + 1; k = t - c_start + 1
    return (smooth(k, dur) - (smooth(k - 1, dur) if k > 1 else D(0))) * constr_total
def sales_t(t): return revenue / D(s_end - s_start + 1) if s_start <= t <= s_end else D(0)
def coll_t(t):
    c = booking * sales_t(t)
    for j in range(1, inst + 1):
        c += (D(1) - booking) / D(inst) * sales_t(t - j)
    return c


# Debt schedule month by month (needed sequentially)
bal = D(0); rows = {}
tot_interest = D(0)
for t in range(1, N + 1):
    opening = bal
    draw = (land_t(t) + approval_t(t) + constr_t(t)) * debt_pct
    interest = opening * rate / D(12)
    avail = opening + draw
    rep = avail if t == N else min(avail, coll_t(t) * sweep)
    bal = avail - rep
    tot_interest += interest
    rows[t] = dict(opening=opening, draw=draw, interest=interest, rep=rep, closing=bal)

total_cost = land + approval + constr_total + sum(coll_t(t) for t in range(1, N + 1)) * mkt + tot_interest
profit = revenue - total_cost
tax = max(D(0), profit * tax_rate)

def project_cf(t):
    return coll_t(t) - land_t(t) - approval_t(t) - constr_t(t) - coll_t(t) * mkt - (tax if t == N else D(0))
def equity_cf(t):
    r = rows[t]; return project_cf(t) + r["draw"] - r["interest"] - r["rep"]

npv = sum(equity_cf(t) / (D(1) + rm) ** t for t in range(1, N + 1))

print("Monthly discount rate m = (1.15)^(1/12) - 1 =", f"{rm:.8f}")
print(f"Construction total = {constr_total} cr, revenue = {revenue} cr")
print(f"Total interest = {tot_interest:.6f} cr, pre-tax profit = {profit:.6f} cr, tax = {tax:.6f} cr\n")
hdr = f"{'month':>5} {'land':>8} {'apprv':>8} {'constr':>9} {'sales':>8} {'collect':>9} {'draw':>8} {'interest':>9} {'repay':>8} {'closing':>9} {'projCF':>9} {'equityCF':>9} {'DF':>9} {'PV':>9}"
print(hdr)
for t in (1, 2, 8, 12, 20, 30, 31, 36):
    r = rows[t]; df_ = D(1) / (D(1) + rm) ** t
    print(f"{t:>5} {land_t(t):>8.3f} {approval_t(t):>8.3f} {constr_t(t):>9.4f} {sales_t(t):>8.3f} {coll_t(t):>9.4f} {r['draw']:>8.4f} {r['interest']:>9.5f} {r['rep']:>8.4f} {r['closing']:>9.4f} {project_cf(t):>9.4f} {equity_cf(t):>9.4f} {df_:>9.6f} {equity_cf(t)*df_:>9.4f}")
print(f"\nHand-check NPV (sum of PV column over 36 months) = {npv:.6f} cr")

# ---- Compare with the engine -------------------------------------------------
from feasibility import BASE_CASE, build_cashflow, appraise
df = build_cashflow(BASE_CASE); a = appraise(BASE_CASE, df)
worst = D(0)
for t in range(1, N + 1):
    worst = max(worst, abs(equity_cf(t) - D(str(df['equity_cf'].iloc[t-1]))))
print(f"Engine NPV = {a.npv_equity_cr:.6f} cr; difference = {float(npv) - a.npv_equity_cr:.2e}")
print(f"Largest monthly equity CF difference, hand vs engine = {float(worst):.2e} cr")
print("RESULT:", "MATCH" if abs(float(npv) - a.npv_equity_cr) < 1e-9 and float(worst) < 1e-9 else "MISMATCH")
