from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.delivery_ops import (
    DemoDatasetMetadataSchema,
    DemoDatasetsResponse,
    PlatformDeliveryManifestResponse,
    PlatformDeliveryManifestSchema,
    SubsystemCatalogEntrySchema,
    SubsystemCatalogResponse,
)
from app.delivery_ops.engine import EnterpriseDeliveryEngine

router = APIRouter(prefix="/ops/delivery", tags=["Part 4 - Module 10: Project Packaging & Delivery"])


@router.get("/manifest", response_model=PlatformDeliveryManifestResponse)
def get_delivery_manifest(
    current_user: User = Depends(get_current_user),
):
    """Retrieve master platform delivery manifest certifying 100% completion of all 10 modules in Part 4."""
    manifest = EnterpriseDeliveryEngine.get_manifest()
    return PlatformDeliveryManifestResponse(manifest=PlatformDeliveryManifestSchema(**manifest.model_dump()))


@router.get("/subsystems", response_model=SubsystemCatalogResponse)
def get_subsystem_catalog(
    current_user: User = Depends(get_current_user),
):
    """List all 48 subsystems across Parts 1, 2, 3, and 4."""
    subsystems = EnterpriseDeliveryEngine.get_subsystems()
    return SubsystemCatalogResponse(
        total_subsystems=len(subsystems),
        subsystems=[SubsystemCatalogEntrySchema(**s.model_dump()) for s in subsystems],
    )


@router.get("/demo-data", response_model=DemoDatasetsResponse)
def get_demo_datasets(
    current_user: User = Depends(get_current_user),
):
    """List pre-packaged enterprise demo datasets for Financial KPIs, Churn, and Cybersecurity logs."""
    datasets = EnterpriseDeliveryEngine.get_demo_datasets()
    return DemoDatasetsResponse(
        total_datasets=len(datasets),
        datasets=[DemoDatasetMetadataSchema(**d.model_dump()) for d in datasets],
    )
