import glob
import os
import pytest
from pathlib import Path
from typing import Dict, Any

# These will be imported from the schemas repository
from schemas.python.can_frame import CANIDFormat
from schemas.python.json_formatter import format_file
from schemas.python.signals_testing import obd_testrunner

REPO_ROOT = Path(__file__).parent.parent.absolute()

TEST_CASES = [
    {
        "model_year": "2018",
        "signalset": "default.json",
        "tests": [
            # Ambient air temperature
            ("""
18DAF1601039627028F8F000
18DAF1602100000004040100
18DAF1602200000000004600
18DAF1602346000000000000
18DAF1602400000000000000
18DAF1602500000000000000
18DAF1602600000000000000
18DAF1602700000000000000
18DAF1602800005555555555
""", {"ACCORD_AAT": 30}),
            ("""
18DAF1601039627028F8F000
18DAF1602100000004070101
18DAF1602200000000004900
18DAF1602349000000000000
18DAF1602400000000000000
18DAF1602500000000000000
18DAF1602600000000000000
18DAF1602700000000000000
18DAF1602800005555555555
""", {"ACCORD_AAT": 33}),
        ]
    },
    {
        "model_year": "2022",
        "signalset": "default.json",
        "tests": [
            # Ambient air temperature
            ("""
18DAF1601039627028F8F000
18DAF1602100000004040100
18DAF1602200000000003300
18DAF160232D000000000000
18DAF1602400000000000000
18DAF1602500000000000000
18DAF1602600000000000000
18DAF1602700000000000000
18DAF1602800005555555555
""", {"ACCORD_AAT": 5}),
        ]
    },
    {
        "model_year": "2023",
        "signalset": "default.json",
        "tests": [
            # Ambient air temperature
            ("""
18DAF1601039627028F8F000
18DAF1602100000004020100
18DAF1602200000000004600
18DAF1602346000000000000
18DAF1602400000000000000
18DAF1602500000000000000
18DAF1602600000000000000
18DAF1602700000000000000
18DAF1602800005555555555
""", {"ACCORD_AAT": 30}),
            ("""
18DAF1601039627028F8F000
18DAF1602100000004070101
18DAF1602200000000004500
18DAF1602344000000000000
18DAF1602400000000000000
18DAF1602500000000000000
18DAF1602600000000000000
18DAF1602700000000000000
18DAF1602800005555555555
""", {"ACCORD_AAT": 28}),
        ]
    },
    {
        "model_year": "2024",
        "signalset": "default.json",
        "tests": [
            # Ambient air temperature
            ("""
18DAF1601039627028F8F000
18DAF1602100000004020100
18DAF1602200000000003E00
18DAF160233E000000000000
18DAF1602400000000000000
18DAF1602500000000000000
18DAF1602600000000000000
18DAF1602700000000000000
18DAF1602800005555555555
""", {"ACCORD_AAT": 22}),
            ("""
18DAF1601039627028F8F000
18DAF1602100000004070101
18DAF1602200000000004100
18DAF1602341000000000000
18DAF1602400000000000000
18DAF1602500000000000000
18DAF1602600000000000000
18DAF1602700000000000000
18DAF1602800005555555555
""", {"ACCORD_AAT": 25}),
        ]
    },
]

def load_signalset(filename: str) -> str:
    """Load a signalset JSON file from the standard location."""
    signalset_path = REPO_ROOT / "signalsets" / "v3" / filename
    with open(signalset_path) as f:
        return f.read()

@pytest.mark.parametrize(
    "test_group",
    TEST_CASES,
    ids=lambda test_case: f"MY{test_case['model_year']}"
)
def test_signals(test_group: Dict[str, Any]):
    """Test signal decoding against known responses."""
    signalset_json = load_signalset(test_group["signalset"])

    # Run each test case in the group
    for response_hex, expected_values in test_group["tests"]:
        try:
            obd_testrunner(
                signalset_json,
                response_hex,
                expected_values,
                can_id_format=CANIDFormat.TWENTY_NINE_BIT
            )
        except Exception as e:
            pytest.fail(
                f"Failed on response {response_hex} "
                f"(Model Year: {test_group['model_year']}, "
                f"Signalset: {test_group['signalset']}): {e}"
            )

def get_json_files():
    """Get all JSON files from the signalsets/v3 directory."""
    signalsets_path = os.path.join(REPO_ROOT, 'signalsets', 'v3')
    json_files = glob.glob(os.path.join(signalsets_path, '*.json'))
    # Convert full paths to relative filenames
    return [os.path.basename(f) for f in json_files]

@pytest.mark.parametrize("test_file",
    get_json_files(),
    ids=lambda x: x.split('.')[0].replace('-', '_')  # Create readable test IDs
)
def test_formatting(test_file):
    """Test signal set formatting for all vehicle models in signalsets/v3/."""
    signalset_path = os.path.join(REPO_ROOT, 'signalsets', 'v3', test_file)

    formatted = format_file(signalset_path)

    with open(signalset_path) as f:
        assert f.read() == formatted

if __name__ == '__main__':
    pytest.main([__file__])
