"""
Pydantic schemas for gearbox design configuration, calculation results,
validation, BOM, and API responses.
"""
from __future__ import annotations

import math
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class GearType(str, Enum):
    """Supported gear types. Only SPUR_EXTERNAL is fully implemented."""
    SPUR_EXTERNAL = "spur_external"
    SPUR_INTERNAL = "spur_internal"
    HELICAL_EXTERNAL = "helical_external"


class PressureAngle(str, Enum):
    DEG_14_5 = "14.5"
    DEG_20 = "20"
    DEG_25 = "25"


class BearingArrangement(str, Enum):
    """Bearing arrangement style for the shafts."""
    SIMPLE = "simple"          # one bearing per shaft end
    FIXED_FREE = "fixed_free"   # locating + floating
    CROSS_LOCATED = "cross_located"


class ProjectInfo(BaseModel):
    project_name: str = Field(default="Single-Stage Spur Gearbox", min_length=1, max_length=120)
    project_description: str = Field(default="", max_length=1000)
    designer_name: str = Field(default="", max_length=120)
    units: str = Field(default="mm")
    drawing_scale: str = Field(default="1:1")
    drawing_number: str = Field(default="GB-001")


class GearParameters(BaseModel):
    gear_type: GearType = GearType.SPUR_EXTERNAL
    input_teeth: int = Field(default=20, ge=8, le=300, description="Input (pinion) tooth count")
    output_teeth: int = Field(default=60, ge=8, le=400, description="Output (gear) tooth count")
    module: float = Field(default=2.0, gt=0, le=50, description="Module in mm")
    pressure_angle: PressureAngle = PressureAngle.DEG_20
    face_width: float = Field(default=20.0, gt=0, le=500, description="Face width in mm")
    backlash: float = Field(default=0.0, ge=0, le=5, description="Circular backlash allowance in mm")
    input_bore: float = Field(default=15.0, gt=0, le=200, description="Input gear bore diameter mm")
    output_bore: float = Field(default=25.0, gt=0, le=200, description="Output gear bore diameter mm")

    @field_validator("module")
    @classmethod
    def validate_module(cls, v: float) -> float:
        if v < 0.1:
            raise ValueError("Module must be at least 0.1 mm")
        return v


class ShaftParameters(BaseModel):
    input_shaft_diameter: float = Field(default=15.0, gt=0, le=300)
    output_shaft_diameter: float = Field(default=25.0, gt=0, le=300)
    input_shaft_length: float = Field(default=120.0, gt=0, le=2000)
    output_shaft_length: float = Field(default=140.0, gt=0, le=2000)
    shaft_shoulder: float = Field(default=3.0, gt=0, le=50, description="Shoulder step height mm")
    keyway_width: float = Field(default=5.0, gt=0, le=50, description="Keyway width mm")
    keyway_height: float = Field(default=5.0, gt=0, le=50, description="Keyway height mm")
    bearing_seat_diameter_in: float = Field(default=17.0, gt=0, le=300, description="Input bearing seat dia mm")
    bearing_seat_diameter_out: float = Field(default=30.0, gt=0, le=300, description="Output bearing seat dia mm")


class HousingParameters(BaseModel):
    housing_length: float = Field(default=200.0, gt=0, le=5000)
    housing_width: float = Field(default=80.0, gt=0, le=2000)
    housing_height: float = Field(default=160.0, gt=0, le=2000)
    wall_thickness: float = Field(default=10.0, gt=0, le=200)
    cover_thickness: float = Field(default=12.0, gt=0, le=200)
    base_thickness: float = Field(default=15.0, gt=0, le=200)
    mounting_hole_diameter: float = Field(default=10.0, gt=0, le=100)
    mounting_hole_count: int = Field(default=4, ge=2, le=24)


class AssemblyParameters(BaseModel):
    bearing_arrangement: BearingArrangement = BearingArrangement.SIMPLE
    gear_axial_offset: float = Field(default=0.0, description="Axial offset between gear pairs mm")
    input_shaft_z: float = Field(default=0.0, description="Input shaft centre Z position mm")
    cover_fastener_diameter: float = Field(default=6.0, gt=0, le=50)
    include_fasteners: bool = Field(default=True)
    include_keys: bool = Field(default=True)
    include_bearings: bool = Field(default=True)


class InputSpeed(BaseModel):
    """Optional input speed for output-speed calculation."""
    input_speed_rpm: float = Field(default=1450.0, gt=0, description="Input shaft speed in RPM")


class GearboxDesign(BaseModel):
    """Full design configuration submitted by the user."""
    project_info: ProjectInfo = Field(default_factory=ProjectInfo)
    gear_parameters: GearParameters = Field(default_factory=GearParameters)
    shaft_parameters: ShaftParameters = Field(default_factory=ShaftParameters)
    housing_parameters: HousingParameters = Field(default_factory=HousingParameters)
    assembly_parameters: AssemblyParameters = Field(default_factory=AssemblyParameters)
    input_speed_rpm: float = Field(default=1450.0, gt=0)


# ---- Calculation result models ----

class GearDimensions(BaseModel):
    teeth: int
    module: float
    pressure_angle_deg: float
    pitch_diameter: float
    base_diameter: float
    addendum: float
    dedendum: float
    outside_diameter: float
    root_diameter: float
    face_width: float
    bore_diameter: float
    circular_pitch: float
    tooth_thickness: float


class CalculationResults(BaseModel):
    input_gear: GearDimensions
    output_gear: GearDimensions
    centre_distance: float
    reduction_ratio: float
    input_pitch_diameter: float
    output_pitch_diameter: float
    output_speed_rpm: float
    pressure_angle_deg: float
    module: float
    circular_pitch: float
    base_circle_input: float
    base_circle_output: float


# ---- Validation ----

class ValidationIssue(BaseModel):
    field: str
    message: str
    severity: str  # "error" | "warning" | "info"


class ValidationResult(BaseModel):
    is_valid: bool
    issues: list[ValidationIssue] = []
    checks_run: int = 0


# ---- Component / BOM ----

class ComponentInfo(BaseModel):
    item_number: int
    part_number: str
    name: str
    quantity: int
    material: str
    principal_dimensions: str
    notes: str
    validation_status: str  # "verified" | "approximate" | "not_verified"


class BOM(BaseModel):
    components: list[ComponentInfo]
    total_parts: int


# ---- Job tracking ----

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStage(str, Enum):
    VALIDATING = "validating"
    CALCULATING = "calculating"
    GENERATING_COMPONENTS = "generating_components"
    GENERATING_DRAWINGS = "generating_drawings"
    BUILDING_ASSEMBLY = "building_assembly"
    EXPORTING_PREVIEWS = "exporting_previews"
    CREATING_BOM = "creating_bom"
    GENERATING_REPORTS = "generating_reports"
    RUNNING_VALIDATION = "running_validation"
    COMPLETED = "completed"
    FAILED = "failed"


class JobInfo(BaseModel):
    job_id: str
    design_id: str
    status: JobStatus
    stage: JobStage
    progress: float = 0.0  # 0–100
    message: str = ""
    error: str = ""
    created_at: str = ""
    files: dict[str, str] = {}  # format -> filename


class DesignRecord(BaseModel):
    design_id: str
    project_name: str
    drawing_number: str
    created_at: str
    config: GearboxDesign
    calculations: Optional[CalculationResults] = None
    validation: Optional[ValidationResult] = None
    bom: Optional[BOM] = None
    files: dict[str, str] = {}  # format -> relative path


class DrawingInfo(BaseModel):
    drawing_id: str
    name: str
    description: str
    filename: str
    dxf_available: bool


class DesignSummary(BaseModel):
    design_id: str
    project_name: str
    drawing_number: str
    created_at: str
    reduction_ratio: float
    module: float
    input_teeth: int
    output_teeth: int
    centre_distance: float
    input_pitch_diameter: float
    output_pitch_diameter: float
    status: str
    files: dict[str, str] = {}


# ---- Health ----

class HealthResponse(BaseModel):
    status: str
    version: str
    cad_engine: str
    available_formats: list[str]
