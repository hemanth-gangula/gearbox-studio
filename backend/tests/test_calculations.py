"""
Calculation tests — verify engineering calculations for the default gear configuration.

Expected results for default config (z1=20, z2=60, m=2, α=20°):
- Input pitch diameter: 40 mm
- Output pitch diameter: 120 mm
- Centre distance: 80 mm
- Reduction ratio: 3:1
"""
import pytest
import math
from app.schemas.design import GearboxDesign, GearParameters, GearType, PressureAngle
from app.calculations.gear_calcs import calculate_design, compute_gear_dimensions
from app.validation.validator import validate_design


class TestDefaultCalculations:
    """Test the default configuration produces expected results."""

    @pytest.fixture
    def design(self):
        return GearboxDesign()

    @pytest.fixture
    def calc(self, design):
        return calculate_design(design)

    def test_input_pitch_diameter(self, calc):
        assert calc.input_pitch_diameter == 40.0, f"Expected 40.0, got {calc.input_pitch_diameter}"

    def test_output_pitch_diameter(self, calc):
        assert calc.output_pitch_diameter == 120.0, f"Expected 120.0, got {calc.output_pitch_diameter}"

    def test_centre_distance(self, calc):
        assert calc.centre_distance == 80.0, f"Expected 80.0, got {calc.centre_distance}"

    def test_reduction_ratio(self, calc):
        assert calc.reduction_ratio == 3.0, f"Expected 3.0, got {calc.reduction_ratio}"

    def test_output_speed(self, calc):
        expected = 1450.0 / 3.0
        assert abs(calc.output_speed_rpm - expected) < 0.1

    def test_base_circle_input(self, calc):
        expected = 40.0 * math.cos(math.radians(20))
        assert abs(calc.base_circle_input - expected) < 0.01

    def test_base_circle_output(self, calc):
        expected = 120.0 * math.cos(math.radians(20))
        assert abs(calc.base_circle_output - expected) < 0.01

    def test_addendum(self, calc):
        assert calc.input_gear.addendum == 2.0

    def test_dedendum(self, calc):
        assert calc.input_gear.dedendum == 2.5

    def test_outside_diameter_input(self, calc):
        assert calc.input_gear.outside_diameter == 44.0

    def test_root_diameter_input(self, calc):
        assert calc.input_gear.root_diameter == 35.0

    def test_circular_pitch(self, calc):
        expected = math.pi * 2.0
        assert abs(calc.circular_pitch - expected) < 0.001


class TestCustomConfigurations:
    """Test non-default configurations."""

    def test_module_3(self):
        design = GearboxDesign()
        design.gear_parameters.module = 3.0
        calc = calculate_design(design)
        assert calc.input_pitch_diameter == 60.0
        assert calc.output_pitch_diameter == 180.0
        assert calc.centre_distance == 120.0

    def test_teeth_25_75(self):
        design = GearboxDesign()
        design.gear_parameters.input_teeth = 25
        design.gear_parameters.output_teeth = 75
        calc = calculate_design(design)
        assert calc.input_pitch_diameter == 50.0
        assert calc.output_pitch_diameter == 150.0
        assert calc.reduction_ratio == 3.0
        assert calc.centre_distance == 100.0

    def test_pressure_angle_25(self):
        design = GearboxDesign()
        design.gear_parameters.pressure_angle = PressureAngle.DEG_25
        calc = calculate_design(design)
        expected_base = 40.0 * math.cos(math.radians(25))
        assert abs(calc.base_circle_input - expected_base) < 0.01


class TestValidation:
    """Test design validation."""

    def test_valid_default(self):
        design = GearboxDesign()
        calc = calculate_design(design)
        result = validate_design(design, calc)
        assert result.is_valid is True
        assert result.checks_run > 0

    def test_output_teeth_less_than_input(self):
        design = GearboxDesign()
        design.gear_parameters.output_teeth = 10
        design.gear_parameters.input_teeth = 20
        calc = calculate_design(design)
        result = validate_design(design, calc)
        assert result.is_valid is False
        assert any("Output gear tooth count should be greater" in i.message for i in result.issues)

    def test_shaft_larger_than_bore(self):
        design = GearboxDesign()
        design.gear_parameters.input_bore = 10.0
        design.shaft_parameters.input_shaft_diameter = 15.0
        calc = calculate_design(design)
        result = validate_design(design, calc)
        assert result.is_valid is False
        assert any("Input shaft diameter" in i.message for i in result.issues)

    def test_thin_face_width_warning(self):
        design = GearboxDesign()
        design.gear_parameters.face_width = 5.0  # Less than 3*module=6
        calc = calculate_design(design)
        result = validate_design(design, calc)
        # Should have a warning, not an error
        warnings = [i for i in result.issues if i.severity == "warning"]
        assert any("Face width" in i.message for i in warnings)

    def test_info_messages_present(self):
        design = GearboxDesign()
        calc = calculate_design(design)
        result = validate_design(design, calc)
        info_issues = [i for i in result.issues if i.severity == "info"]
        assert len(info_issues) >= 1
