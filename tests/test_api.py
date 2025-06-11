import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from airport_controllers_api import load_data, get_controllers

@pytest.fixture(scope="module", autouse=True)
def setup_data():
    load_data()


def test_edja_topdown_controllers():
    ctrs = get_controllers('EDJA')
    ids = {c['id'] for c in ctrs}
    expected = {'ILR', 'SWA', 'FUE', 'ZUG', 'STA', 'TRU', 'RDG'}
    assert expected.issubset(ids)
    # EDJA has no other references, so exactly this set
    assert ids == expected

