import os
import json
import logging
import pandas as pd
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, Base, engine
from app.models.user import User, Role
from app.models.audit import UserActivityLog
from app.models.dataset import Dataset, DataQualityReport
from app.core.security import get_password_hash
from app.services.kpi_service import KPIService

logger = logging.getLogger("aegisiq.seed")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ROLES_DATA = [
    {
        "name": "Admin",
        "description": "Full enterprise administrator access to all modules, users, security logs, and configuration.",
        "permissions": "all:all,users:manage,roles:manage,datasets:manage,etl:manage,bi:manage,reports:manage,security:view",
    },
    {
        "name": "Executive",
        "description": "C-level executive access to high-level strategic KPI dashboards, company summaries, and decision reports.",
        "permissions": "bi:view,kpi:view,reports:view,reports:export,exec:summary",
    },
    {
        "name": "Business Analyst",
        "description": "Business intelligence analyst access to interactive dashboards, custom KPI creation, data slices, and report generation.",
        "permissions": "bi:view,bi:create,kpi:manage,reports:manage,datasets:view",
    },
    {
        "name": "Data Analyst",
        "description": "Data engineering access to dataset uploads, ETL pipeline execution, data cleaning, and data quality reports.",
        "permissions": "datasets:manage,etl:manage,bi:view,data_quality:view",
    },
    {
        "name": "Viewer",
        "description": "Read-only access to published enterprise dashboards and standard BI reports.",
        "permissions": "bi:view,reports:view",
    },
]

USERS_DATA = [
    {
        "email": "admin@aegisiq.com",
        "password": "Admin@12345",
        "full_name": "Alexander Hayes (Chief Administrator)",
        "job_title": "Enterprise System Administrator",
        "department": "Information Technology",
        "phone_number": "+1-555-0100",
        "role": "Admin",
        "is_superuser": True,
    },
    {
        "email": "executive@aegisiq.com",
        "password": "Exec@12345",
        "full_name": "Victoria Sterling (Chief Executive Officer)",
        "job_title": "Chief Executive Officer",
        "department": "Executive Leadership",
        "phone_number": "+1-555-0101",
        "role": "Executive",
        "is_superuser": False,
    },
    {
        "email": "business.analyst@aegisiq.com",
        "password": "Analyst@12345",
        "full_name": "Marcus Vance (Senior BI Analyst)",
        "job_title": "Lead Business Intelligence Analyst",
        "department": "Strategic Finance & BI",
        "phone_number": "+1-555-0102",
        "role": "Business Analyst",
        "is_superuser": False,
    },
    {
        "email": "data.analyst@aegisiq.com",
        "password": "Data@12345",
        "full_name": "Elena Rostova (Data Engineer)",
        "job_title": "Senior Data & ETL Engineer",
        "department": "Data Engineering",
        "phone_number": "+1-555-0103",
        "role": "Data Analyst",
        "is_superuser": False,
    },
    {
        "email": "viewer@aegisiq.com",
        "password": "Viewer@12345",
        "full_name": "David Kim (Operations Viewer)",
        "job_title": "Operations Specialist",
        "department": "Supply Chain & Operations",
        "phone_number": "+1-555-0104",
        "role": "Viewer",
        "is_superuser": False,
    },
]


def seed_demo_datasets(db: Session, admin_user: User):
    """Seed standard enterprise datasets for immediate interactive exploration."""
    datasets_spec = [
        {
            "name": "Enterprise Sales Transactions (2025-2026)",
            "description": "Global enterprise client deals, contract values, territories, product modules, and quota attributions.",
            "filename": "enterprise_sales_2025_2026.csv",
            "data": [
                {"deal_id": "DEAL-1001", "account_name": "Meridian Global", "region": "North America", "product": "AI Decision Intelligence", "contract_value": 450000, "close_date": "2026-01-15", "sales_rep": "Sarah Jenkins", "status": "Closed Won"},
                {"deal_id": "DEAL-1002", "account_name": "Apex BioTech", "region": "EMEA", "product": "Autonomous ETL Engine", "contract_value": 320000, "close_date": "2026-01-22", "sales_rep": "Emily Watson", "status": "Closed Won"},
                {"deal_id": "DEAL-1003", "account_name": "Vanguard Logistics", "region": "North America", "product": "Supply Chain BI", "contract_value": 680000, "close_date": "2026-02-04", "sales_rep": "Sarah Jenkins", "status": "Closed Won"},
                {"deal_id": "DEAL-1004", "account_name": "Kinetix Cloud", "region": "APAC", "product": "Enterprise RBAC Hub", "contract_value": 190000, "close_date": "2026-02-18", "sales_rep": "Michael Chen", "status": "Closed Won"},
                {"deal_id": "DEAL-1005", "account_name": "Orion Aerospace", "region": "North America", "product": "Predictive Decision Platform", "contract_value": 820000, "close_date": "2026-03-01", "sales_rep": "David Ross", "status": "Closed Won"},
                {"deal_id": "DEAL-1006", "account_name": "Nordic Retail Group", "region": "EMEA", "product": "AI Decision Intelligence", "contract_value": 240000, "close_date": "2026-03-12", "sales_rep": "Emily Watson", "status": "Closed Won"},
                {"deal_id": "DEAL-1007", "account_name": "Pacific Financials", "region": "APAC", "product": "Autonomous ETL Engine", "contract_value": 510000, "close_date": "2026-03-20", "sales_rep": "Michael Chen", "status": "Closed Won"},
            ],
        },
        {
            "name": "Financial General Ledger & Cost Allocations",
            "description": "Monthly departmental expenditures, R&D outlays, marketing ROI, and operating margins.",
            "filename": "financial_general_ledger.csv",
            "data": [
                {"period": "2026-01", "department": "R&D / Engineering", "budget": 1400000, "actual_spend": 1380000, "variance": -20000, "category": "Opex"},
                {"period": "2026-01", "department": "Sales & Marketing", "budget": 950000, "actual_spend": 920000, "variance": -30000, "category": "Opex"},
                {"period": "2026-01", "department": "Cloud & Infrastructure", "budget": 600000, "actual_spend": 590000, "variance": -10000, "category": "COGS"},
                {"period": "2026-02", "department": "R&D / Engineering", "budget": 1400000, "actual_spend": 1410000, "variance": 10000, "category": "Opex"},
                {"period": "2026-02", "department": "Sales & Marketing", "budget": 950000, "actual_spend": 940000, "variance": -10000, "category": "Opex"},
                {"period": "2026-02", "department": "Cloud & Infrastructure", "budget": 600000, "actual_spend": 605000, "variance": 5000, "category": "COGS"},
            ],
        },
        {
            "name": "Supply Chain & Hardware Inventory",
            "description": "High-performance AI compute nodes, security HSMs, and warehouse fulfillment metrics.",
            "filename": "supply_chain_inventory.csv",
            "data": [
                {"sku": "SRV-EDGE-X9", "product_name": "Edge AI Inference Node", "category": "Compute", "stock_on_hand": 420, "reorder_level": 150, "unit_cost": 4200, "lead_time_days": 8},
                {"sku": "SEC-HSM-2026", "product_name": "Hardware Security HSM", "category": "Security", "stock_on_hand": 85, "reorder_level": 100, "unit_cost": 2800, "lead_time_days": 12},
                {"sku": "SAN-TB100-NVME", "product_name": "100TB High-Speed NVMe", "category": "Storage", "stock_on_hand": 310, "reorder_level": 80, "unit_cost": 8500, "lead_time_days": 15},
                {"sku": "NET-ROUTER-ZT", "product_name": "Zero-Trust Mesh Router", "category": "Network", "stock_on_hand": 620, "reorder_level": 200, "unit_cost": 1400, "lead_time_days": 7},
            ],
        },
    ]

    for spec in datasets_spec:
        existing = db.query(Dataset).filter(Dataset.name == spec["name"]).first()
        if not existing:
            file_path = os.path.join(UPLOAD_DIR, spec["filename"])
            df = pd.DataFrame(spec["data"])
            df.to_csv(file_path, index=False)

            schema_meta = []
            for col in df.columns:
                schema_meta.append({
                    "name": col,
                    "data_type": "numeric" if pd.api.types.is_numeric_dtype(df[col]) else "text",
                    "null_count": 0,
                    "null_percentage": 0.0,
                    "unique_count": int(df[col].nunique()),
                    "sample_values": df[col].head(3).tolist(),
                    "min_value": float(df[col].min()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                    "max_value": float(df[col].max()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                    "mean_value": float(df[col].mean()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                })

            ds = Dataset(
                name=spec["name"],
                description=spec["description"],
                file_format="csv",
                storage_path=file_path,
                file_size_bytes=os.path.getsize(file_path),
                row_count=len(df),
                column_count=len(df.columns),
                source_type="ENTERPRISE_SEED",
                schema_json=json.dumps(schema_meta),
                quality_score=99.4,
                created_by_user_id=admin_user.id if admin_user else None,
            )
            db.add(ds)
            db.commit()
            db.refresh(ds)

            # Add quality report
            qr = DataQualityReport(
                dataset_id=ds.id,
                completeness_score=100.0,
                uniqueness_score=100.0,
                validity_score=99.5,
                consistency_score=98.5,
                overall_score=99.4,
                metrics_json=json.dumps({"duplicates_removed": 0, "nulls_imputed": 0, "outliers_adjusted": 0}),
            )
            db.add(qr)
            db.commit()
            logger.info(f"Seeded enterprise dataset: {ds.name}")


def seed_database(db: Session = None):
    """Seed initial enterprise roles, demo accounts, KPIs, and sample datasets."""
    close_after = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        close_after = True

    try:
        logger.info("Seeding enterprise roles...")
        role_map = {}
        for role_spec in ROLES_DATA:
            role = db.query(Role).filter(Role.name == role_spec["name"]).first()
            if not role:
                role = Role(
                    name=role_spec["name"],
                    description=role_spec["description"],
                    permissions=role_spec["permissions"],
                )
                db.add(role)
                db.flush()
                logger.info(f"Created role: {role.name}")
            role_map[role.name] = role

        db.commit()

        logger.info("Seeding enterprise demo users...")
        admin_user = None
        for user_spec in USERS_DATA:
            user = db.query(User).filter(User.email == user_spec["email"]).first()
            if not user:
                assigned_role = role_map.get(user_spec["role"])
                user = User(
                    email=user_spec["email"],
                    hashed_password=get_password_hash(user_spec["password"]),
                    full_name=user_spec["full_name"],
                    job_title=user_spec["job_title"],
                    department=user_spec["department"],
                    phone_number=user_spec["phone_number"],
                    is_active=True,
                    is_superuser=user_spec["is_superuser"],
                    roles=[assigned_role] if assigned_role else [],
                )
                db.add(user)
                db.flush()
                
                log = UserActivityLog(
                    user_id=user.id,
                    user_email=user.email,
                    action="ACCOUNT_SEEDED",
                    status="SUCCESS",
                    details=f"Demo account initialized with role: {user_spec['role']}",
                )
                db.add(log)
                logger.info(f"Created demo user: {user.email} [{user_spec['role']}]")
            
            if user.is_superuser:
                admin_user = user

        db.commit()

        # Seed KPIs
        logger.info("Seeding enterprise KPIs...")
        KPIService.seed_initial_kpis(db=db)

        # Seed Demo Datasets
        if admin_user:
            logger.info("Seeding enterprise demo datasets...")
            seed_demo_datasets(db=db, admin_user=admin_user)

        logger.info("Database seeding completed successfully.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise e
    finally:
        if close_after:
            db.close()
    
