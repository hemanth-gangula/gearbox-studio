"""
CAD generation tests — verify DXF files, 3D meshes, and STEP files.
"""
import pytest
import os
import tempfile
import ezdxf

from app.schemas.design import GearboxDesign
from app.calculations.gear_calcs import calculate_design
from app.cad.dxf_generator import generate_all_drawings
from app.cad.mesh_generator import generate_all_meshes, get_component_info_list
from app.cad.step_exporter import generate_step_file


@pytest.fixture
def design():
    return GearboxDesign()


@pytest.fixture
def calc(design):
    return calculate_design(design)


@pytest.fixture
def output_dir():
    d = tempfile.mkdtemp()
    return d


class TestDXFGeneration:
    """Test DXF drawing generation."""

    def test_generate_all_drawings(self, design, calc, output_dir):
        drawings = generate_all_drawings(design, calc, output_dir)
        assert len(drawings) == 9, f"Expected 9 drawings, got {len(drawings)}"

    def test_dxf_files_exist(self, design, calc, output_dir):
        drawings = generate_all_drawings(design, calc, output_dir)
        for d in drawings:
            filepath = os.path.join(output_dir, d.filename)
            assert os.path.isfile(filepath), f"File {d.filename} not found"
            assert os.path.getsize(filepath) > 0, f"File {d.filename} is empty"

    def test_dxf_can_be_reopened(self, design, calc, output_dir):
        drawings = generate_all_drawings(design, calc, output_dir)
        for d in drawings:
            filepath = os.path.join(output_dir, d.filename)
            doc = ezdxf.readfile(filepath)
            assert doc is not None

    def test_dxf_layers_exist(self, design, calc, output_dir):
        drawings = generate_all_drawings(design, calc, output_dir)
        filepath = os.path.join(output_dir, drawings[0].filename)
        doc = ezdxf.readfile(filepath)
        msp = doc.modelspace()
        # Check that geometry exists (lines, circles, text, polylines)
        entities = list(msp)
        assert len(entities) > 10, "Drawing should contain significant geometry"

    def test_dxf_has_titleblock(self, design, calc, output_dir):
        drawings = generate_all_drawings(design, calc, output_dir)
        filepath = os.path.join(output_dir, drawings[0].filename)
        doc = ezdxf.readfile(filepath)
        msp = doc.modelspace()
        # Check for text entities (title block text)
        texts = [e for e in msp if e.dxftype() == "TEXT"]
        assert len(texts) > 0, "Title block should contain text"

    def test_dxf_dimensions_match_config(self, design, calc, output_dir):
        """Verify that the DXF drawings use the configured parameters."""
        drawings = generate_all_drawings(design, calc, output_dir)
        # Check that the gear drawing has circles of the right radius
        gear_drawing = next(d for d in drawings if "input_gear" in d.drawing_id)
        filepath = os.path.join(output_dir, gear_drawing.filename)
        doc = ezdxf.readfile(filepath)
        msp = doc.modelspace()
        circles = [e for e in msp if e.dxftype() == "CIRCLE"]
        assert len(circles) > 0, "Gear drawing should contain circles"
        # The outside diameter circle should have radius = 44/2 = 22
        radii = [c.dxf.radius for c in circles]
        assert 22.0 in radii or any(abs(r - 22.0) < 0.1 for r in radii), \
            f"Expected circle with radius 22.0 (outside diameter 44mm), got radii: {radii}"


class TestMeshGeneration:
    """Test 3D mesh generation."""

    def test_generate_meshes(self, design, calc, output_dir):
        components, glb_path = generate_all_meshes(design, calc, output_dir)
        assert len(components) == 10, f"Expected 10 components, got {len(components)}"

    def test_glb_file_exists(self, design, calc, output_dir):
        components, glb_path = generate_all_meshes(design, calc, output_dir)
        assert os.path.isfile(glb_path), "GLB file not found"
        assert os.path.getsize(glb_path) > 1000, "GLB file is too small"

    def test_component_meshes_have_geometry(self, design, calc, output_dir):
        components, _ = generate_all_meshes(design, calc, output_dir)
        for comp in components:
            assert len(comp.mesh.vertices) > 0, f"Component {comp.name} has no vertices"
            assert len(comp.mesh.faces) > 0, f"Component {comp.name} has no faces"

    def test_components_have_unique_ids(self, design, calc, output_dir):
        components, _ = generate_all_meshes(design, calc, output_dir)
        item_numbers = [c.item_number for c in components]
        assert len(item_numbers) == len(set(item_numbers)), "Item numbers should be unique"

    def test_component_info_list(self, design, calc, output_dir):
        components, _ = generate_all_meshes(design, calc, output_dir)
        comp_infos = get_component_info_list(components)
        assert len(comp_infos) == len(components)

    def test_stl_files_generated(self, design, calc, output_dir):
        components, _ = generate_all_meshes(design, calc, output_dir)
        stl_files = [f for f in os.listdir(output_dir) if f.endswith('.stl')]
        assert len(stl_files) > 0, "No STL files generated"

    def test_components_json_generated(self, design, calc, output_dir):
        import json
        components, _ = generate_all_meshes(design, calc, output_dir)
        json_path = os.path.join(output_dir, "components.json")
        assert os.path.isfile(json_path)
        with open(json_path) as f:
            data = json.load(f)
        assert len(data) == len(components)


class TestStepExport:
    """Test STEP file generation."""

    def test_step_file_generated(self, design, calc, output_dir):
        components, _ = generate_all_meshes(design, calc, output_dir)
        step_path = os.path.join(output_dir, "test_assembly.stp")
        generate_step_file(components, step_path, "test_assembly.stp")
        assert os.path.isfile(step_path), "STEP file not found"
        assert os.path.getsize(step_path) > 1000, "STEP file is too small"

    def test_step_file_valid_header(self, design, calc, output_dir):
        components, _ = generate_all_meshes(design, calc, output_dir)
        step_path = os.path.join(output_dir, "test_assembly.stp")
        generate_step_file(components, step_path, "test_assembly.stp")
        with open(step_path) as f:
            content = f.read()
        assert "ISO-10303-21" in content, "Missing STEP header"
        assert "END-ISO-10303-21" in content, "Missing STEP footer"
        assert "FACETED_BREP" in content or "CLOSED_SHELL" in content, "Missing B-rep entities"
