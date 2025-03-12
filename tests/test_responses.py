import glob
import os
import pytest
from pathlib import Path
from typing import Dict, Any

# These will be imported from the schemas repository
from schemas.python.can_frame import CANIDFormat
from schemas.python.json_formatter import format_file
from schemas.python.signals_testing import obd_testrunner_by_year

REPO_ROOT = Path(__file__).parent.parent.absolute()

TEST_CASES = [
    {
        "model_year": 2014,
        "tests": [
            # Ambient air temperature
            ("""
18DAF1601039627028F8FC00
18DAF1602100000004020100
18DAF1602200000000002A00
18DAF160232A000000000000
18DAF1602400000000000000
18DAF1602500000000000000
18DAF1602600000000000000
18DAF1602700000000000000
18DAF1602800005555555555
""", {"ACCORD_AAT": 2}),
            ("""
18DAF1601039627028F8FC00
18DAF1602100000004070101
18DAF1602200000000002900
18DAF1602329000000000000
18DAF1602400000000000000
18DAF1602500000000000000
18DAF1602600000000000000
18DAF1602700000000000000
18DAF1602800005555555555
""", {"ACCORD_AAT": 1}),

            # ODO + runtime
            ("""
18DAF1101039622660801FFF
18DAF11021F3F7F000000000
18DAF1102200000000000000
18DAF110230000005F1F0101
18DAF1102400040040408300
18DAF1102501017700000590
18DAF11026045C045500023F
18DAF11027C4005B001E0000
18DAF1102800005555555555
""", {
    "ACCORD_ODO": 147396.0,
    "ACCORD_RUNTM": 91,
    }),
            ("""
18DAF1101039622660801FFF
18DAF11021F3F7F000000000
18DAF1102200000000000000
18DAF110230000006B1F0201
18DAF1102400040040408300
18DAF110250101760000045E
18DAF11026013B01AD00023F
18DAF11027CF03C204B50000
18DAF1102800005555555555
""", {
    "ACCORD_ODO": 147407.0,
    "ACCORD_RUNTM": 962,
    }),
        ]
    },
    {
        "model_year": 2018,
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
        "model_year": 2022,
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
        "model_year": 2023,
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
        "model_year": 2024,
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

@pytest.mark.parametrize(
    "test_group",
    TEST_CASES,
    ids=lambda test_case: f"MY{test_case['model_year']}"
)
def test_signals(test_group: Dict[str, Any]):
    """Test signal decoding against known responses."""
    for response_hex, expected_values in test_group["tests"]:
        try:
            obd_testrunner_by_year(
                test_group['model_year'],
                response_hex,
                expected_values,
                can_id_format=CANIDFormat.TWENTY_NINE_BIT
            )
        except Exception as e:
            pytest.fail(
                f"Failed on response {response_hex} "
                f"(Model Year: {test_group['model_year']}: {e}"
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
