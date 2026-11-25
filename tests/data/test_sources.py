"""Each source can be read from another copy, e.g. a local clone."""

import pytest

from bsutennis.data.sources import archive, mcp


@pytest.mark.parametrize(
    "variable, download, cached",
    [
        ("BSUTENNIS_ARCHIVE_URL", archive.download, f"archive/{archive.COMMIT[:7]}"),
        ("BSUTENNIS_MCP_URL", mcp._download, f"mcp/{mcp.COMMIT[:7]}"),
    ],
)
def test_another_copy(tmp_path, monkeypatch, variable, download, cached):
    copy = tmp_path / "copy"
    (copy / "atp").mkdir(parents=True)
    (copy / "atp" / "file.csv").write_text("a,b\n1,2\n")
    monkeypatch.setenv(variable, copy.as_uri())
    monkeypatch.setenv("BSUTENNIS_CACHE", str(tmp_path / "cache"))

    path = download("atp/file.csv")
    assert path == tmp_path / "cache" / cached / "atp" / "file.csv"
    assert path.read_text() == "a,b\n1,2\n"
