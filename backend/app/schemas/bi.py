from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class MetricCard(BaseModel):
    label: str
    value: str
    numeric_value: float
    change_pct: float
    trend: str  # up, down, neutral
    subtext: str


class TimeSeriesDataPoint(BaseModel):
    date: str
    revenue: float
    target: float
    costs: float
    profit: float


class CategoryBreakdownPoint(BaseModel):
    category: str
    value: float
    percentage: float
    color: Optional[str] = None


class RegionalSalesPoint(BaseModel):
    region: str
    sales: float
    growth_pct: float
    units_sold: int


class ExecutiveOverviewResponse(BaseModel):
    summary_metrics: List[MetricCard]
    revenue_trend: List[TimeSeriesDataPoint]
    regional_breakdown: List[RegionalSalesPoint]
    category_distribution: List[CategoryBreakdownPoint]
    recent_transactions: List[Dict[str, Any]]


class FinancialAnalyticsResponse(BaseModel):
    kpis: List[MetricCard]
    cash_flow_trend: List[Dict[str, Any]]
    expense_breakdown: List[CategoryBreakdownPoint]
    margin_history: List[Dict[str, Any]]


class SalesAnalyticsResponse(BaseModel):
    kpis: List[MetricCard]
    pipeline_funnel: List[Dict[str, Any]]
    top_products: List[Dict[str, Any]]
    sales_rep_leaderboard: List[Dict[str, Any]]


class CustomerAnalyticsResponse(BaseModel):
    kpis: List[MetricCard]
    retention_cohorts: List[Dict[str, Any]]
    segment_distribution: List[CategoryBreakdownPoint]
    churn_risk_distribution: List[Dict[str, Any]]


class InventoryAnalyticsResponse(BaseModel):
    kpis: List[MetricCard]
    stock_levels: List[Dict[str, Any]]
    turnover_by_category: List[CategoryBreakdownPoint]
    supplier_lead_times: List[Dict[str, Any]]
