import json
from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from audit.validate_omega_ledger import LEDGER, validate


def test_omega_ledger_is_valid():
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert validate(data) == []


def test_reference_frequency_is_exact():
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert data["reference"]["f0_hz"] == 141.7001


def test_dependency_graph_is_closed():
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    ids = {claim["id"] for claim in data["claims"]}
    assert all(dep in ids for claim in data["claims"] for dep in claim["depends_on"])
