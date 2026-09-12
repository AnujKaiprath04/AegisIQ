import math
from app.prediction_engine.types import InventoryOptimizationResult


class InventoryOptimizer:
    """Operations Research & Inventory Optimization Engine (EOQ, Safety Stock, Reorder Point)."""

    Z_TABLE = {
        0.90: 1.28,
        0.95: 1.65,
        0.98: 2.05,
        0.99: 2.33,
    }

    @classmethod
    def optimize(
        cls,
        sku_id: str = "SKU-OPT-100",
        product_name: str = "Enterprise Fiber Switch 48-Port",
        annual_demand_units: int = 12000,
        order_cost_usd: float = 250.0,
        unit_holding_cost_usd: float = 45.0,
        lead_time_days: int = 14,
        daily_demand_std_dev: float = 8.5,
        service_level: float = 0.95,
    ) -> InventoryOptimizationResult:
        # 1. Economic Order Quantity (EOQ)
        eoq = math.sqrt((2.0 * annual_demand_units * order_cost_usd) / unit_holding_cost_usd)
        eoq_units = max(1, int(round(eoq)))

        # 2. Safety Stock
        z = cls.Z_TABLE.get(service_level, 1.65)
        safety_stock = z * daily_demand_std_dev * math.sqrt(lead_time_days)
        safety_stock_units = max(1, int(round(safety_stock)))

        # 3. Reorder Point (ROP)
        daily_demand = annual_demand_units / 365.0
        lead_time_demand = daily_demand * lead_time_days
        rop_units = int(round(lead_time_demand + safety_stock_units))

        # 4. Holding Cost
        holding_cost = round((eoq_units / 2.0) * unit_holding_cost_usd, 2)

        return InventoryOptimizationResult(
            sku_id=sku_id,
            product_name=product_name,
            economic_order_quantity_units=eoq_units,
            safety_stock_units=safety_stock_units,
            reorder_point_units=rop_units,
            estimated_annual_holding_cost_usd=holding_cost,
            service_level_achieved=service_level,
        )
