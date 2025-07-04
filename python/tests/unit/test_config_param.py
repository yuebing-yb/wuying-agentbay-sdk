import unittest
from unittest.mock import mock_open, patch

import os
import tempfile
from unittest import TestCase
from unittest.mock import patch, mock_open

from agentbay.config import load_config, default_config
from agentbay import Config
from pathlib import Path

class LoadConfigTestCase(unittest.TestCase):
    def setUp(self):
        # 创建临时 .env 文件目录
        self.test_dir = tempfile.TemporaryDirectory()
        self.env_file = Path(self.test_dir.name) / ".env"

    def tearDown(self):
        self.test_dir.cleanup()

    def test_load_from_passed_config(self):
        """测试从传入的 Config 对象加载配置"""
        custom_cfg = Config(
            region_id="custom-region",
            endpoint="custom-endpoint",
            timeout_ms=5000,
        )
        result = load_config(custom_cfg)

        self.assertEqual(result["region_id"], "custom-region")
        self.assertEqual(result["endpoint"], "custom-endpoint")
        self.assertEqual(result["timeout_ms"], 5000)

    def test_load_from_env_file(self):
        """测试从 .env 文件中加载配置"""
        with open(self.env_file, "w") as f:
            f.write(
                "AGENTBAY_REGION_ID=env-region\n"
                "AGENTBAY_ENDPOINT=env-endpoint\n"
                "AGENTBAY_TIMEOUT_MS=10000\n"
            )

        with os.scandir(self.test_dir.name) as it:
            print("Files in temp dir:", [entry.name for entry in it])

        os.environ.pop("AGENTBAY_REGION_ID", None)
        os.environ.pop("AGENTBAY_ENDPOINT", None)
        os.environ.pop("AGENTBAY_TIMEOUT_MS", None)

        os.chdir(self.test_dir.name)
        result = load_config(None)

        self.assertEqual(result["region_id"], "env-region")
        self.assertEqual(result["endpoint"], "env-endpoint")
        self.assertEqual(result["timeout_ms"], "10000")

    @patch("pathlib.Path.is_file", return_value=False)
    def test_load_from_system_env_vars(self, mock_is_file):
        """测试从系统环境变量加载配置"""
        os.environ["AGENTBAY_REGION_ID"] = "sys-region"
        os.environ["AGENTBAY_ENDPOINT"] = "sys-endpoint"
        os.environ["AGENTBAY_TIMEOUT_MS"] = "15000"

        result = load_config(None)

        self.assertEqual(result["region_id"], "sys-region")
        self.assertEqual(result["endpoint"], "sys-endpoint")
        self.assertEqual(result["timeout_ms"], "15000")

    @patch("pathlib.Path.is_file", return_value=False)
    def test_use_default_config_when_no_source_provided(self, mock_is_file):
        """测试当没有提供任何配置源时使用默认值"""
        # 清除所有相关环境变量
        os.environ.pop("AGENTBAY_REGION_ID", None)
        os.environ.pop("AGENTBAY_ENDPOINT", None)
        os.environ.pop("AGENTBAY_TIMEOUT_MS", None)

        result = load_config(None)

        default = default_config()
        self.assertEqual(result["region_id"], default["region_id"])
        self.assertEqual(result["endpoint"], default["endpoint"])
        self.assertEqual(result["timeout_ms"], default["timeout_ms"])

if __name__ == '__main__':
    unittest.main()