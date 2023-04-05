"""Tests for getters."""

from napalm.base.test.getters import BaseTestGetters


import pytest


@pytest.mark.usefixtures("set_device_parameters")
class TestGetter(BaseTestGetters):
    """Test get_* methods."""

    def test_get_config_filtered(self):
        pytest.skip("This test is not implemented on {self.device.platform}")

