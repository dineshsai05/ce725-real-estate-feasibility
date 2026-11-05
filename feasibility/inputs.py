"""Input definitions for the feasibility model.

All money is in INR crore (1 crore = 1e7 rupees). Areas are in square feet.
Time is in months, numbered from 1. All cash flows are assumed to occur at the
END of the month in which they arise (end-of-period convention).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from typing import Any

CRORE = 1e7


@dataclass(frozen=True)
class ProjectInputs:
    # --- Timeline -----------------------------------------------------------
    horizon_months: int = 36          # minimum horizon; auto-extended if sales/collections run later

    # --- Land ---------------------------------------------------------------
    land_cost_cr: float = 20.0
    land_month: int = 1               # month in which land is paid for (single payment)

    # --- Approvals / statutory ---------------------------------------------
    approval_cost_cr: float = 3.0
    approval_start: int = 1
    approval_end: int = 3             # spread evenly between start and end (inclusive)

    # --- Construction -------------------------------------------------------
    saleable_area_sqft: float = 100_000.0
    construction_cost_per_sqft: float = 3_000.0
    construction_start: int = 4
    construction_end: int = 30        # spent on a smoothstep S-curve between start and end

    # --- Sales --------------------------------------------------------------
    selling_price_per_sqft: float = 7_500.0
    sales_start: int = 7              # launch month
    sales_end: int = 30               # area sold evenly between launch and sales_end
    booking_pct: float = 0.20         # share of a sale collected in the month of booking
    instalment_months: int = 6        # balance collected evenly over the following N months
    marketing_pct: float = 0.02       # marketing & brokerage, as a share of collections

    # --- Financing ----------------------------------------------------------
    debt_pct_of_costs: float = 0.50          # share of each month's land, approval and construction spend funded by loan
    interest_rate: float = 0.12              # nominal annual rate, interest = balance * rate/12, paid monthly
    repayment_sweep_pct: float = 0.50        # share of each month's collections used to repay the loan

    # --- Tax ----------------------------------------------------------------
    tax_rate: float = 0.25            # income tax on project profit, paid in the final month

    # --- Appraisal ----------------------------------------------------------
    discount_rate: float = 0.15       # effective annual discount rate for NPV (equity cash flows)

    # ----------------------------------------------------------------------
    @property
    def construction_cost_cr(self) -> float:
        return self.saleable_area_sqft * self.construction_cost_per_sqft / CRORE

    @property
    def gross_revenue_cr(self) -> float:
        return self.saleable_area_sqft * self.selling_price_per_sqft / CRORE

    @property
    def effective_horizon(self) -> int:
        """Horizon long enough to collect every sale and finish construction."""
        return max(
            self.horizon_months,
            self.sales_end + self.instalment_months,
            self.construction_end,
            self.approval_end,
            self.land_month,
        )

    def with_changes(self, **changes: Any) -> "ProjectInputs":
        return replace(self, **changes)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> list[str]:
        """Return a list of human-readable problems (empty list means OK)."""
        p = []
        if self.approval_end < self.approval_start:
            p.append("Approval end month must be >= start month.")
        if self.construction_end < self.construction_start:
            p.append("Construction end month must be >= start month.")
        if self.sales_end < self.sales_start:
            p.append("Sales end month must be >= launch month.")
        if not 0 <= self.booking_pct <= 1:
            p.append("Booking % must be between 0 and 1.")
        if self.instalment_months < 0:
            p.append("Instalment months cannot be negative.")
        if not 0 <= self.debt_pct_of_costs <= 1:
            p.append("Debt share must be between 0 and 1.")
        if not 0 <= self.repayment_sweep_pct <= 1:
            p.append("Repayment sweep must be between 0 and 1.")
        for name in ("land_month", "approval_start", "construction_start", "sales_start"):
            if getattr(self, name) < 1:
                p.append(f"{name} must be >= 1.")
        return p


BASE_CASE = ProjectInputs()
