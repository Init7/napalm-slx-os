# Copyright 2016 Dravetech AB. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""Tests."""

import json
import unittest

from napalm.base.test.base import TestConfigNetworkDriver, TestGettersNetworkDriver
from napalm.base.test.double import BaseTestDouble

from napalm_slx_os import slx_os


class TestConfigDriver(unittest.TestCase, TestConfigNetworkDriver):
    """Group of tests that test Configuration related methods."""

    @classmethod
    def setUpClass(cls):
        """Run before starting the tests."""
        hostname = '127.0.0.1'
        username = 'vagrant'
        password = 'vagrant'
        cls.vendor = 'slx_os'

        optional_args = {'port': 12443, }
        cls.device = slx_os.SLXOSDriver(hostname, username, password, timeout=60,
                                        optional_args=optional_args)
        cls.device.open()

        cls.device.load_replace_candidate(filename='%s/initial.conf' % cls.vendor)
        cls.device.commit_config()


class TestGetterDriver(unittest.TestCase, TestGettersNetworkDriver):
    """Group of tests that test getters."""

    @classmethod
    def setUpClass(cls):
        """Run before starting the tests."""
        cls.mock = True

        hostname = '127.0.0.1'
        username = 'vagrant'
        password = 'vagrant'
        cls.vendor = 'slx_os'

        optional_args = {'port': 12443, }
        cls.device = slx_os.SLXOSDriver(hostname, username, password, timeout=60,
                                        optional_args=optional_args)

        if cls.mock:
            cls.device.device = FakeDevice()
        else:
            cls.device.open()


class FakeDevice(BaseTestDouble):
    """Test double."""

    @staticmethod
    def read_json_file(filename):
        """Return the content of a file with content formatted as json."""
        with open(filename) as data_file:
            return json.load(data_file)

    @staticmethod
    def read_txt_file(filename):
        """Return the content of a file."""
        with open(filename) as data_file:
            return data_file.read()

    def send_command(self, command, **kwargs):
        filename = "{}.txt".format(self.sanitize_text(command))
        full_path = self.find_file(filename)
        result = self.read_txt_file(full_path)
        return str(result)
