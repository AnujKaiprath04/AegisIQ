import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.kpi import KPIMetric
from app.schemas.kpi import KPICalculateRequest, KPICalculateResponse, KPITargetUpdate

logger = logging.getLogger("aegisiq.kpi_service")

# Default standard KPI baseline records
STANDARD_KPIS = [
    {
        "code": "GROSS_MARGIN",
        "name": "Gross Profit Margin",
        "category": "FINANCIAL",
        "description": "Percentage of revenue retained after deducting Cost of Goods Sold (COGS).",
        "formula_expression": "((Revenue - COGS) / Revenue) * 100",
        "unit": "%",
        "current_value": 68.4,
        "target_value": 65.0,
        "benchmark_value": 62.0,
        "variance_pct": 5.23,
        "trend_direction": "UP",
        "status": "ON_TRACK",
        "period": "Q1 2026",
    },
    {
        "code": "CAC",
        "name": "Customer Acquisition Cost",
        "category": "SALES",
        "description": "Total sales & marketing expenditure divided by new customers acquired.",
        "formula_expression": "Sales & Mktg Expenses / New Customers",
        "unit": "$",
        "current_value": 14200.0,
        "target_value": 16000.0,
        "benchmark_value": 18500.0,
        "variance_pct": -11.25,
        "trend_direction": "DOWN",
        "status": "ON_TRACK",
        "period": "Q1 2026",
    },
    {
        "code": "LTV_CAC",
        "name": "LTV to CAC Ratio",
        "category": "CUSTOMERS",
        "description": "Customer lifetime value relative to customer acquisition cost. Benchmark > 3.0x.",
        "formula_expression": "Customer LTV / CAC",
        "unit": "x",
        "current_value": 4.8,
        "target_value": 4.0,
        "benchmark_value": 3.0,
        "variance_pct": 20.0,
        "trend_direction": "UP",
        "status": "ON_TRACK",
        "period": "Q1 2026",
    },
    {
        "code": "QUICK_RATIO",
        "name": "Quick Liquidity Ratio",
        "category": "FINANCIAL",
        "description": "Acid-test measurement of short-term liquid assets against current liabilities.",
        "formula_expression": "(Cash + Receivables) / Current Liabilities",
        "unit": "x",
        "current_value": 2.8,
        "target_value": 2.5,
        "benchmark_value": 1.5,
        "variance_pct": 12.0,
        "trend_direction": "UP",
        "status": "ON_TRACK",
        "period": "Q1 2026",
    },
    {
        "code": "INVENTORY_TURNOVER",
        "name": "Inventory Turnover Velocity",
        "category": "OPERATIONS",
        "description": "Frequency of inventory sold and replaced over annual operational cycle.",
        "formula_expression": "COGS / Average Inventory",
        "unit": "x / yr",
        "current_value": 8.4,
        "target_value": 8.0,
        "benchmark_value": 6.5,
        "variance_pct": 5.0,
        "trend_direction": "UP",
        "status": "ON_TRACK",
        "period": "Q1 2026",
    },
    {
        "code": "CHURN_RATE",
        "name": "Annual Gross Churn Rate",
        "category": "CUSTOMERS",
        "description": "Percentage of enterprise subscribers terminating subscriptions annually.",
        "formula_expression": "(Lost Accounts / Total Accounts) * 100",
        "unit": "%",
        "current_value": 2.8,
        "target_value": 3.5,
        "benchmark_value": 5.0,
        "variance_pct": -20.0,
        "trend_direction": "DOWN",
        "status": "ON_TRACK",
        "period": "Q1 2026",
    },
    {
        "code": "EBITDA_MARGIN",
        "name": "EBITDA Profit Margin",
        "category": "FINANCIAL",
        "description": "Earnings Before Interest, Taxes, Depreciation, and Amortization relative to revenue.",
        "formula_expression": "(EBITDA / Total Revenue) * 100",
        "unit": "%",
        "current_value": 34.2,
        "target_value": 30.0,
        "benchmark_value": 26.0,
        "variance_pct": 14.0,
        "trend_direction": "UP",
        "status": "ON_TRACK",
        "period": "Q1 2026",
    },
]


class KPIService:
    @staticmethod
    def seed_initial_kpis(db: Session):
        """Seed baseline standard enterprise KPIs if table is empty."""
        for item in STANDARD_KPIS:
            existing = db.query(KPIMetric).filter(KPIMetric.code == item["code"]).first()
            if not existing:
                metric = KPIMetric(**item)
                db.add(metric)
        db.commit()

    @staticmethod
    def get_all_kpis(db: Session, category: Optional[str] = None) -> List[KPIMetric]:
        KPIService.seed_initial_kpis(db)
        query = db.query(KPIMetric)
        if category:
            query = query.filter(KPIMetric.category == category.upper())
        return query.order_by(KPIMetric.id.asc()).all()

    @staticmethod
    def update_kpi_target(db: Session, kpi_id: int, target_in: KPITargetUpdate) -> KPIMetric:
        metric = db.query(KPIMetric).filter(KPIMetric.id == kpi_id).first()
        if not metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"KPI Metric with ID {kpi_id} not found.",
            )

        metric.target_value = target_in.target_value
        if target_in.period:
            metric.period = target_in.period

        # Recalculate variance
        if metric.target_value > 0:
            diff = metric.current_value - metric.target_value
            variance = round((diff / metric.target_value) * 100, 2)
            metric.variance_pct = variance

            # Update status based on metric nature
            if metric.code in ["CAC", "CHURN_RATE"]:  # Lower is better
                if metric.current_value <= metric.target_value:
                    metric.status = "ON_TRACK"
                elif metric.current_value <= metric.target_value * 1.15:
                    metric.status = "WARNING"
                else:
                    metric.status = "CRITICAL"
            else:  # Higher is better
                if metric.current_value >= metric.target_value:
                    metric.status = "ON_TRACK"
                elif metric.current_value >= metric.target_value * 0.85:
                    metric.status = "WARNING"
                else:
                    metric.status = "CRITICAL"

        db.commit()
        db.refresh(metric)
        return metric

    @staticmethod
    def calculate_custom_formula(req: KPICalculateRequest) -> KPICalculateResponse:
        """Dynamic formula computation engine for standard enterprise metrics."""
        f_type = req.formula_type.upper()
        p = req.parameters

        if f_type == "GROSS_MARGIN":
            rev = float(p.get("revenue", 1000000))
            cogs = float(p.get("cogs", 350000))
            val = round(((rev - cogs) / max(rev, 1)) * 100, 2)
            status_val = "ON_TRACK" if val >= 60 else "WARNING"
            return KPICalculateResponse(
                formula_type=f_type,
                name="Gross Profit Margin",
                calculated_value=val,
                formatted_value=f"{val}%",
                unit="%",
                status=status_val,
                interpretation=f"For every dollar in revenue, organization retains {val} cents in gross profit.",
                inputs_used={"revenue": rev, "cogs": cogs},
            )

        elif f_type == "CAC":
            expenses = float(p.get("sales_marketing_expenses", 500000))
            new_cust = float(p.get("new_customers", 35))
            val = round(expenses / max(new_cust, 1), 2)
            return KPICalculateResponse(
                formula_type=f_type,
                name="Customer Acquisition Cost",
                calculated_value=val,
                formatted_value=f"${val:,.2f}",
                unit="$",
                status="ON_TRACK" if val < 20000 else "WARNING",
                interpretation=f"Acquiring one customer requires an average investment of ${val:,.2f}.",
                inputs_used={"sales_marketing_expenses": expenses, "new_customers": new_cust},
            )

        elif f_type == "LTV_CAC":
            ltv = float(p.get("customer_ltv", 95000))
            cac = float(p.get("cac", 18000))
            val = round(ltv / max(cac, 1), 2)
            return KPICalculateResponse(
                formula_type=f_type,
                name="LTV:CAC Ratio",
                calculated_value=val,
                formatted_value=f"{val}x",
                unit="ratio",
                status="ON_TRACK" if val >= 3.0 else "WARNING",
                interpretation=f"Unit economics are {'healthy and scalable' if val >= 3.0 else 'sub-optimal (target > 3.0x)'}.",
                inputs_used={"customer_ltv": ltv, "cac": cac},
            )

        elif f_type == "QUICK_RATIO":
            cash = float(p.get("cash_and_equivalents", 4500000))
            receivables = float(p.get("receivables", 1200000))
            liabilities = float(p.get("current_liabilities", 2000000))
            val = round((cash + receivables) / max(liabilities, 1), 2)
            return KPICalculateResponse(
                formula_type=f_type,
                name="Quick Liquidity Ratio",
                calculated_value=val,
                formatted_value=f"{val}x",
                unit="ratio",
                status="ON_TRACK" if val >= 1.5 else "CRITICAL",
                interpretation=f"Enterprise possesses ${val} in liquid assets for every $1.00 of immediate short-term obligations.",
                inputs_used={"cash_and_equivalents": cash, "receivables": receivables, "current_liabilities": liabilities},
            )

        elif f_type == "EBITDA_MARGIN":
            ebitda = float(p.get("ebitda", 3200000))
            rev = float(p.get("revenue", 10000000))
            val = round((ebitda / max(rev, 1)) * 100, 2)
            return KPICalculateResponse(
                formula_type=f_type,
                name="EBITDA Profit Margin",
                calculated_value=val,
                formatted_value=f"{val}%",
                unit="%",
                status="ON_TRACK" if val >= 25 else "WARNING",
                interpretation=f"Operational efficiency yield is {val}% before accounting adjustments.",
                inputs_used={"ebitda": ebitda, "revenue": rev},
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formula type '{req.formula_type}' is not recognized.",
            )
