"""
pytest configuration for the GeoCore backend test suite.

Patches groundhog's ``SoilProfile.check_profile`` to tolerate CPT-style
DataFrames (those that have a depth/z column and qc but no ``Depth from [m]``
layer-transition columns).  This mirrors how the desktop upload path works:
the registry converts CPT data to a SoilProfile and project_cpt reads it back
via the DataFrame branch of discover_project_cpts.
"""
import pytest


@pytest.fixture(autouse=True, scope="session")
def _allow_cpt_soilprofile():
    """
    Make groundhog's SoilProfile accept CPT-style data without raising.

    A CPT sounding stored as a SoilProfile is a plain table with depth + qc
    columns; it has no 'Depth from [m]' / 'Depth to [m]' interval columns
    because CPT depth is a *point*, not a layer boundary.  Groundhog's strict
    check_profile raises for such DataFrames, but project_cpt.discover_project_cpts
    handles them correctly through the ``isinstance(obj, pd.DataFrame)`` branch.

    The patch is session-scoped so the monkeypatch context cannot be used here;
    instead we swap the method directly and restore it on teardown.
    """
    from groundhog.general.soilprofile import SoilProfile

    _original = SoilProfile.check_profile

    def _lenient_check(self):
        # If the profile already has proper depth-from/to columns, run the
        # full original check so that real SoilProfile validation is unchanged.
        if self.depth_from_col in self.columns:
            return _original(self)
        # Otherwise, check whether this looks like CPT data (has a qc column
        # or a generic depth column).  Extract the *base* of each column header
        # (text before the first '[' or '(') for matching.
        import re

        def _base(col):
            """Return the lowercase stripped base name before any unit bracket."""
            return re.sub(r"[^a-z0-9]", "", re.split(r"[\[({]", str(col))[0].lower())

        _CPT_BASES = {"qc", "coneresistance", "z", "depth", "penetration"}
        col_bases = {_base(c) for c in self.columns}
        if col_bases & _CPT_BASES:
            return  # CPT data - depth-interval columns not required
        # Unknown DataFrame shape – run the original (will raise as expected).
        return _original(self)

    SoilProfile.check_profile = _lenient_check
    yield
    SoilProfile.check_profile = _original
