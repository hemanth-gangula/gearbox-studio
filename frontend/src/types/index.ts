// TypeScript types matching the backend Pydantic schemas

export type GearType = 'spur_external' | 'spur_internal' | 'helical_external';
export type PressureAngle = '14.5' | '20' | '25';
export type BearingArrangement = 'simple' | 'fixed_free' | 'cross_located';
export type JobStatus = 'pending' | 'running' | 'completed' | 'failed';
export type JobStage = 'validating' | 'calculating' | 'generating_components' |
  'generating_drawings' | 'building_assembly' | 'exporting_previews' |
  'creating_bom' | 'generating_reports' | 'running_validation' | 'completed' | 'failed';

export interface ProjectInfo {
  project_name: string;
  project_description: string;
  designer_name: string;
  units: string;
  drawing_scale: string;
  drawing_number: string;
}

export interface GearParameters {
  gear_type: GearType;
  input_teeth: number;
  output_teeth: number;
  module: number;
  pressure_angle: PressureAngle;
  face_width: number;
  backlash: number;
  input_bore: number;
  output_bore: number;
}

export interface ShaftParameters {
  input_shaft_diameter: number;
  output_shaft_diameter: number;
  input_shaft_length: number;
  output_shaft_length: number;
  shaft_shoulder: number;
  keyway_width: number;
  keyway_height: number;
  bearing_seat_diameter_in: number;
  bearing_seat_diameter_out: number;
}

export interface HousingParameters {
  housing_length: number;
  housing_width: number;
  housing_height: number;
  wall_thickness: number;
  cover_thickness: number;
  base_thickness: number;
  mounting_hole_diameter: number;
  mounting_hole_count: number;
}

export interface AssemblyParameters {
  bearing_arrangement: BearingArrangement;
  gear_axial_offset: number;
  input_shaft_z: number;
  cover_fastener_diameter: number;
  include_fasteners: boolean;
  include_keys: boolean;
  include_bearings: boolean;
}

export interface GearboxDesign {
  project_info: ProjectInfo;
  gear_parameters: GearParameters;
  shaft_parameters: ShaftParameters;
  housing_parameters: HousingParameters;
  assembly_parameters: AssemblyParameters;
  input_speed_rpm: number;
}

export interface GearDimensions {
  teeth: number;
  module: number;
  pressure_angle_deg: number;
  pitch_diameter: number;
  base_diameter: number;
  addendum: number;
  dedendum: number;
  outside_diameter: number;
  root_diameter: number;
  face_width: number;
  bore_diameter: number;
  circular_pitch: number;
  tooth_thickness: number;
}

export interface CalculationResults {
  input_gear: GearDimensions;
  output_gear: GearDimensions;
  centre_distance: number;
  reduction_ratio: number;
  input_pitch_diameter: number;
  output_pitch_diameter: number;
  output_speed_rpm: number;
  pressure_angle_deg: number;
  module: number;
  circular_pitch: number;
  base_circle_input: number;
  base_circle_output: number;
}

export interface ValidationIssue {
  field: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export interface ValidationResult {
  is_valid: boolean;
  issues: ValidationIssue[];
  checks_run: number;
}

export interface ComponentInfo {
  item_number: number;
  part_number: string;
  name: string;
  quantity: number;
  material: string;
  principal_dimensions: string;
  notes: string;
  validation_status: string;
}

export interface BOM {
  components: ComponentInfo[];
  total_parts: number;
}

export interface JobInfo {
  job_id: string;
  design_id: string;
  status: JobStatus;
  stage: JobStage;
  progress: number;
  message: string;
  error: string;
  created_at: string;
  files: Record<string, string>;
}

export interface DrawingInfo {
  drawing_id: string;
  name: string;
  description: string;
  filename: string;
  dxf_available: boolean;
}

export interface DesignSummary {
  design_id: string;
  project_name: string;
  drawing_number: string;
  created_at: string;
  reduction_ratio: number;
  module: number;
  input_teeth: number;
  output_teeth: number;
  centre_distance: number;
  input_pitch_diameter: number;
  output_pitch_diameter: number;
  status: string;
  files: Record<string, string>;
}

export interface DesignRecord {
  design_id: string;
  project_name: string;
  drawing_number: string;
  created_at: string;
  config: GearboxDesign;
  calculations: CalculationResults | null;
  validation: ValidationResult | null;
  bom: BOM | null;
  files: Record<string, string>;
}

export interface FileListResponse {
  design_id: string;
  files: Record<string, {
    filename: string;
    size_bytes: number;
    available: boolean;
  }>;
}

export const defaultDesign: GearboxDesign = {
  project_info: {
    project_name: 'Single-Stage Spur Gearbox',
    project_description: 'Preliminary design of a single-stage external spur gear reduction unit.',
    designer_name: '',
    units: 'mm',
    drawing_scale: '1:1',
    drawing_number: 'GB-001',
  },
  gear_parameters: {
    gear_type: 'spur_external',
    input_teeth: 20,
    output_teeth: 60,
    module: 2.0,
    pressure_angle: '20',
    face_width: 20.0,
    backlash: 0.0,
    input_bore: 15.0,
    output_bore: 25.0,
  },
  shaft_parameters: {
    input_shaft_diameter: 15.0,
    output_shaft_diameter: 25.0,
    input_shaft_length: 120.0,
    output_shaft_length: 140.0,
    shaft_shoulder: 3.0,
    keyway_width: 5.0,
    keyway_height: 5.0,
    bearing_seat_diameter_in: 17.0,
    bearing_seat_diameter_out: 30.0,
  },
  housing_parameters: {
    housing_length: 200.0,
    housing_width: 80.0,
    housing_height: 160.0,
    wall_thickness: 10.0,
    cover_thickness: 12.0,
    base_thickness: 15.0,
    mounting_hole_diameter: 10.0,
    mounting_hole_count: 4,
  },
  assembly_parameters: {
    bearing_arrangement: 'simple',
    gear_axial_offset: 0.0,
    input_shaft_z: 0.0,
    cover_fastener_diameter: 6.0,
    include_fasteners: true,
    include_keys: true,
    include_bearings: true,
  },
  input_speed_rpm: 1450.0,
};
