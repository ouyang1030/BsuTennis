import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest


@pytest.fixture(autouse=True)
def _isolated_output(tmp_path, monkeypatch):
    """Run every test in a temp dir (the viz tests save PNGs) and close figures."""
    monkeypatch.chdir(tmp_path)
    yield
    plt.close("all")
