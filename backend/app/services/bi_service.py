import logging
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app.schemas.bi import (
    CategoryBreakdownPoint,
    CustomerAnalyticsResponse,
    ExecutiveOverviewResponse,
    FinancialAnalyticsResponse,
    InventoryAnalyticsResponse,
    MetricCard,
    RegionalSalesPoint,
    SalesAnalyticsResponse,
    TimeSeriesDataPoint,
)

logger = logging.getLogger("aegisiq.bi_service")


class BIService:
    @staticmethod
    def get_executive_overview(db: Session, date_range: str = "YTD") -> ExecutiveOverviewResponse:
        """Executive level consolidated platform metrics."""
        summary_metrics = [
            MetricCard(
                label="Annual Recurring Revenue (ARR)",
                value="$24.8M",
                numeric_value=24800000.0,
                change_pct=18.4,
                trend="up",
                subtext="+$3.8M vs last fiscal year",
            ),
            MetricCard(
                label="Enterprise Net Profit Margin",
                value="28.6%",
                numeric_value=28.6,
                change_pct=4.2,
                trend="up",
                subtext="Exceeds 25% target threshold",
            ),
            MetricCard(
                label="Active Enterprise Clients",
                value="1,420",
                numeric_value=1420.0,
                change_pct=12.5,
                trend="up",
                subtext="99.4% SLA retention rate",
            ),
            MetricCard(
                label="Data Quality Health Index",
                value="98.7%",
                numeric_value=98.7,
                change_pct=1.8,
                trend="up",
                subtext="Zero critical schema anomalies",
            ),
        ]

        revenue_trend = [
            TimeSeriesDataPoint(date="2025 Q1", revenue=4.8, target=4.5, costs=3.2, profit=1.6),
            TimeSeriesDataPoint(date="2025 Q2", revenue=5.4, target=5.0, costs=3.5, profit=1.9),
            TimeSeriesDataPoint(date="2025 Q3", revenue=5.9, target=5.5, costs=3.8, profit=2.1),
            TimeSeriesDataPoint(date="2025 Q4", revenue=6.8, target=6.2, costs=4.1, profit=2.7),
            TimeSeriesDataPoint(date="2026 Q1", revenue=7.4, target=7.0, costs=4.5, profit=2.9),
            TimeSeriesDataPoint(date="2026 Q2 (Est)", revenue=8.2, target=7.8, costs=4.8, profit=3.4),
        ]

        regional_breakdown = [
            RegionalSalesPoint(region="North America (East/West)", sales=11.4, growth_pct=21.2, units_sold=4250),
            RegionalSalesPoint(region="EMEA (Europe & Middle East)", sales=7.8, growth_pct=16.8, units_sold=2890),
            RegionalSalesPoint(region="Asia-Pacific (APAC)", sales=4.2, growth_pct=28.5, units_sold=1940),
            RegionalSalesPoint(region="Latin America (LATAM)", sales=1.4, growth_pct=14.0, units_sold=620),
        ]

        category_distribution = [
            CategoryBreakdownPoint(category="Cloud Platform Licenses", value=12.2, percentage=49.2, color="#3b82f6"),
            CategoryBreakdownPoint(category="AI Decision Intelligence", value=6.8, percentage=27.4, color="#6366f1"),
            CategoryBreakdownPoint(category="Enterprise Support & SLAs", value=3.6, percentage=14.5, color="#10b981"),
            CategoryBreakdownPoint(category="Consulting & Integrations", value=2.2, percentage=8.9, color="#f59e0b"),
        ]

        recent_transactions = [
            {"id": "TX-9042", "client": "Meridian Global Financials", "amount": "$450,000", "module": "AI Executive Suite", "status": "COMPLETED", "date": "2026-08-28"},
            {"id": "TX-9041", "client": "Apex BioTech Industries", "amount": "$320,000", "module": "ETL & Analytics Engine", "status": "COMPLETED", "date": "2026-08-27"},
            {"id": "TX-9040", "client": "Vanguard Logistics Corp", "amount": "$680,000", "module": "Supply Chain BI", "status": "COMPLETED", "date": "2026-08-26"},
            {"id": "TX-9039", "client": "Kinetix Cloud Systems", "amount": "$190,000", "module": "Enterprise RBAC & Security", "status": "COMPLETED", "date": "2026-08-25"},
            {"id": "TX-9038", "client": "Orion Aerospace", "amount": "$820,000", "module": "Predictive Decision Platform", "status": "PROCESSING", "date": "2026-08-25"},
        ]

        return ExecutiveOverviewResponse(
            summary_metrics=summary_metrics,
            revenue_trend=revenue_trend,
            regional_breakdown=regional_breakdown,
            category_distribution=category_distribution,
            recent_transactions=recent_transactions,
        )

    @staticmethod
    def get_financial_analytics(db: Session) -> FinancialAnalyticsResponse:
        """Financial domain metrics & expense breakdowns."""
        kpis = [
            MetricCard(label="Gross Profit Margin", value="68.4%", numeric_value=68.4, change_pct=3.1, trend="up", subtext="Target: 65.0%"),
            MetricCard(label="Operating Cash Flow", value="$8.6M", numeric_value=8.6, change_pct=14.2, trend="up", subtext="Healthy liquidity"),
            MetricCard(label="Monthly Net Burn", value="$240K", numeric_value=240.0, change_pct=-12.5, trend="down", subtext="Cost optimization active"),
            MetricCard(label="Quick Ratio", value="2.8x", numeric_value=2.8, change_pct=0.4, trend="up", subtext="Strong short-term solvency"),
        ]

        cash_flow_trend = [
            {"month": "Jan", "inflow": 2.4, "outflow": 1.6, "net": 0.8},
            {"month": "Feb", "inflow": 2.7, "outflow": 1.7, "net": 1.0},
            {"month": "Mar", "inflow": 2.9, "outflow": 1.8, "net": 1.1},
            {"month": "Apr", "inflow": 3.2, "outflow": 1.9, "net": 1.3},
            {"month": "May", "inflow": 3.4, "outflow": 2.0, "net": 1.4},
            {"month": "Jun", "inflow": 3.8, "outflow": 2.1, "net": 1.7},
        ]

        expense_breakdown = [
            CategoryBreakdownPoint(category="R&D / Engineering", value=4.2, percentage=42.0, color="#3b82f6"),
            CategoryBreakdownPoint(category="Sales & Marketing", value=2.8, percentage=28.0, color="#6366f1"),
            CategoryBreakdownPoint(category="Cloud & Infrastructure", value=1.8, percentage=18.0, color="#10b981"),
            CategoryBreakdownPoint(category="General & Administrative", value=1.2, percentage=12.0, color="#8b5cf6"),
        ]

        margin_history = [
            {"quarter": "Q1 25", "gross": 64.2, "operating": 24.1, "net": 19.5},
            {"quarter": "Q2 25", "gross": 65.8, "operating": 25.4, "net": 21.0},
            {"quarter": "Q3 25", "gross": 66.5, "operating": 26.2, "net": 22.8},
            {"quarter": "Q4 25", "gross": 67.9, "operating": 28.0, "net": 24.5},
            {"quarter": "Q1 26", "gross": 68.4, "operating": 29.5, "net": 26.2},
        ]

        return FinancialAnalyticsResponse(
            kpis=kpis,
            cash_flow_trend=cash_flow_trend,
            expense_breakdown=expense_breakdown,
            margin_history=margin_history,
        )

    @staticmethod
    def get_sales_analytics(db: Session) -> SalesAnalyticsResponse:
        """Sales pipelines, conversion velocity, and top product lines."""
        kpis = [
            MetricCard(label="Pipeline Value", value="$42.5M", numeric_value=42.5, change_pct=22.0, trend="up", subtext="Weighted: $18.2M"),
            MetricCard(label="Win Rate", value="34.8%", numeric_value=34.8, change_pct=5.2, trend="up", subtext="Above industry avg (28%)"),
            MetricCard(label="Avg Deal Size", value="$185K", numeric_value=185.0, change_pct=8.4, trend="up", subtext="Enterprise tier deals"),
            MetricCard(label="Sales Velocity", value="48 Days", numeric_value=48.0, change_pct=-14.0, trend="down", subtext="Cycle shortened by 8 days"),
        ]

        pipeline_funnel = [
            {"stage": "Lead Generation", "count": 1240, "value": 68.2},
            {"stage": "Discovery & Demo", "count": 680, "value": 44.5},
            {"stage": "Technical Evaluation", "count": 320, "value": 28.4},
            {"stage": "Contract Negotiation", "count": 145, "value": 14.8},
            {"stage": "Closed Won", "count": 86, "value": 9.2},
        ]

        top_products = [
            {"name": "AegisIQ Core Enterprise", "revenue": "$9.4M", "growth": "+24%", "market_share": "38%"},
            {"name": "Decision Intelligence Copilot", "revenue": "$6.2M", "growth": "+42%", "market_share": "25%"},
            {"name": "Autonomous ETL Data Engine", "revenue": "$5.1M", "growth": "+19%", "market_share": "21%"},
            {"name": "Cyber Threat Analytics Hub", "revenue": "$4.1M", "growth": "+33%", "market_share": "16%"},
        ]

        sales_rep_leaderboard = [
            {"name": "Sarah Jenkins", "region": "North America", "quota_attainment": "142%", "revenue": "$3.2M", "deals_closed": 18},
            {"name": "Michael Chen", "region": "APAC", "quota_attainment": "128%", "revenue": "$2.8M", "deals_closed": 15},
            {"name": "Emily Watson", "region": "EMEA", "quota_attainment": "118%", "revenue": "$2.5M", "deals_closed": 14},
            {"name": "David Ross", "region": "North America", "quota_attainment": "109%", "revenue": "$2.2M", "deals_closed": 12},
        ]

        return SalesAnalyticsResponse(
            kpis=kpis,
            pipeline_funnel=pipeline_funnel,
            top_products=top_products,
            sales_rep_leaderboard=sales_rep_leaderboard,
        )

    @staticmethod
    def get_customer_analytics(db: Session) -> CustomerAnalyticsResponse:
        """Customer retention, churn analysis, and cohort health."""
        kpis = [
            MetricCard(label="Net Revenue Retention (NRR)", value="118.5%", numeric_value=118.5, change_pct=4.5, trend="up", subtext="Expansion outpaces contraction"),
            MetricCard(label="Annual Gross Churn", value="2.8%", numeric_value=2.8, change_pct=-0.9, trend="down", subtext="Top-quartile SaaS benchmark"),
            MetricCard(label="Customer LTV", value="$380K", numeric_value=380.0, change_pct=11.2, trend="up", subtext="LTV:CAC ratio is 4.8x"),
            MetricCard(label="Net Promoter Score (NPS)", value="+68", numeric_value=68.0, change_pct=6.0, trend="up", subtext="World-class enterprise rating"),
        ]

        retention_cohorts = [
            {"cohort": "Q1 2025", "m0": 100, "m3": 98, "m6": 96, "m9": 95, "m12": 94},
            {"cohort": "Q2 2025", "m0": 100, "m3": 99, "m6": 97, "m9": 96, "m12": 95},
            {"cohort": "Q3 2025", "m0": 100, "m3": 98, "m6": 97, "m9": 96, "m12": 96},
            {"cohort": "Q4 2025", "m0": 100, "m3": 99, "m6": 98, "m9": 97, "m12": 97},
            {"cohort": "Q1 2026", "m0": 100, "m3": 99, "m6": 98, "m9": 98, "m12": 98},
        ]

        segment_distribution = [
            CategoryBreakdownPoint(category="Fortune 500 Enterprise", value=58.0, percentage=58.0, color="#3b82f6"),
            CategoryBreakdownPoint(category="Mid-Market Growth", value=28.0, percentage=28.0, color="#6366f1"),
            CategoryBreakdownPoint(category="Tech & Scale-up", value=14.0, percentage=14.0, color="#10b981"),
        ]

        churn_risk_distribution = [
            {"tier": "Healthy (< 5% Risk)", "accounts": 1280, "arr": "$22.4M", "percentage": 90.1},
            {"tier": "Monitored (5-20% Risk)", "accounts": 112, "arr": "$1.9M", "percentage": 7.9},
            {"tier": "High Risk (> 20% Risk)", "accounts": 28, "arr": "$0.5M", "percentage": 2.0},
        ]

        return CustomerAnalyticsResponse(
            kpis=kpis,
            retention_cohorts=retention_cohorts,
            segment_distribution=segment_distribution,
            churn_risk_distribution=churn_risk_distribution,
        )

    @staticmethod
    def get_inventory_analytics(db: Session) -> InventoryAnalyticsResponse:
        """Supply chain, stock velocity, and fulfillment lead times."""
        kpis = [
            MetricCard(label="Inventory Turnover", value="8.4x / yr", numeric_value=8.4, change_pct=1.2, trend="up", subtext="Optimal capital utilization"),
            MetricCard(label="Stockout Frequency", value="0.4%", numeric_value=0.4, change_pct=-0.8, trend="down", subtext="99.6% order fulfillment rate"),
            MetricCard(label="Avg Supplier Lead Time", value="11.2 Days", numeric_value=11.2, change_pct=-2.4, trend="down", subtext="Reduced by 3 days"),
            MetricCard(label="Carrying Cost Ratio", value="14.2%", numeric_value=14.2, change_pct=-1.5, trend="down", subtext="Controlled warehouse overhead"),
        ]

        stock_levels = [
            {"sku": "SRV-EDGE-X9", "name": "Edge AI Inference Node", "stock": 420, "min_required": 150, "status": "HEALTHY"},
            {"sku": "SEC-HSM-2026", "name": "Hardware Security HSM Module", "stock": 85, "min_required": 100, "status": "LOW_STOCK"},
            {"sku": "SAN-TB100-NVME", "name": "100TB High-Speed NVMe Storage", "stock": 310, "min_required": 80, "status": "HEALTHY"},
            {"sku": "SW-LIC-CORP", "name": "Dedicated Enterprise Core Token", "stock": 1850, "min_required": 500, "status": "HEALTHY"},
        ]

        turnover_by_category = [
            CategoryBreakdownPoint(category="Compute & AI Acceleration", value=38.0, percentage=38.0, color="#3b82f6"),
            CategoryBreakdownPoint(category="Enterprise Storage Arrays", value=28.0, percentage=28.0, color="#6366f1"),
            CategoryBreakdownPoint(category="Network & Zero-Trust Routers", value=20.0, percentage=20.0, color="#10b981"),
            CategoryBreakdownPoint(category="Security Hardware Modules", value=14.0, percentage=14.0, color="#f59e0b"),
        ]

        supplier_lead_times = [
            {"supplier": "Quantum Microelectronics", "lead_time_days": 8, "on_time_rate": "98.5%", "rating": "A+"},
            {"supplier": "Pacific SemiConductors", "lead_time_days": 12, "on_time_rate": "96.0%", "rating": "A"},
            {"supplier": "EuroHardware Logistics", "lead_time_days": 15, "on_time_rate": "94.2%", "rating": "B+"},
            {"supplier": "Nexus Silicon Global", "lead_time_days": 9, "on_time_rate": "97.8%", "rating": "A"},
        ]

        return InventoryAnalyticsResponse(
            kpis=kpis,
            stock_levels=stock_levels,
            turnover_by_category=turnover_by_category,
            supplier_lead_times=supplier_lead_times,
        )
