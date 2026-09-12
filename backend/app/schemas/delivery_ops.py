from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.delivery_ops.types import (
    DemoDatasetMetadata,
    PlatformDeliveryManifest,
    SubsystemCatalogEntry,
)


class SubsystemCatalogEntrySchema(SubsystemCatalogEntry):
    pass


class DemoDatasetMetadataSchema(DemoDatasetMetadata):
    pass


class PlatformDeliveryManifestSchema(PlatformDeliveryManifest):
    pass


class PlatformDeliveryManifestResponse(BaseModel):
    manifest: PlatformDeliveryManifestSchema


class SubsystemCatalogResponse(BaseModel):
    total_subsystems: int
    subsystems: List[SubsystemCatalogEntrySchema] = []


class DemoDatasetsResponse(BaseModel):
    total_datasets: int
    datasets: List[DemoDatasetMetadataSchema] = []
