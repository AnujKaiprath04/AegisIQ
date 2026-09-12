from app.prediction_engine.types import CustomerLTVResult


class CustomerLTVCalculator:
    """Probabilistic Customer Lifetime Value (CLV / LTV) Forecasting Engine."""

    @classmethod
    def calculate_clv(
        cls,
        account_id: str = "ACC-NEXUS-002",
        company_name: str = "Nexus FinTech Labs",
        monthly_revenue_usd: float = 25000.0,
        gross_margin_pct: float = 0.684,
        monthly_churn_rate: float = 0.015,
        annual_discount_rate: float = 0.08,
    ) -> CustomerLTVResult:
        # Expected lifetime in months
        safe_churn = max(0.001, monthly_churn_rate)
        lifetime_months = int(round(1.0 / safe_churn))

        # Monthly gross profit margin
        monthly_margin = monthly_revenue_usd * gross_margin_pct
        expected_total_margin = monthly_margin * lifetime_months

        # Discounted Cash Flow CLV formula
        monthly_discount = annual_discount_rate / 12.0
        # CLV = Margin * ( (1 - (1+d)^-L) / d )
        clv_dcf = monthly_margin * ((1.0 - (1.0 + monthly_discount) ** (-lifetime_months)) / monthly_discount)
        net_present_clv = round(clv_dcf, 2)

        if net_present_clv >= 500000.0:
            tier = "TIER_1_STRATEGIC_ENTERPRISE"
        elif net_present_clv >= 150000.0:
            tier = "TIER_2_HIGH_GROWTH_ACCOUNT"
        else:
            tier = "TIER_3_CORE_COMMERCIAL"

        return CustomerLTVResult(
            account_id=account_id,
            company_name=company_name,
            predicted_lifetime_months=lifetime_months,
            expected_margin_usd=round(expected_total_margin, 2),
            net_present_clv_usd=net_present_clv,
            customer_tier=tier,
        )
