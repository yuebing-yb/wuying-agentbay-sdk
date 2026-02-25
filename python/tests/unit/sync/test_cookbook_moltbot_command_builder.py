import importlib.util
import unittest
from pathlib import Path

import pytest


def _load_cookbook_module():
    repo_root = Path(__file__).resolve().parents[4]
    script_path = repo_root / "cookbook" / "moltbot" / "python" / "main.py"
    spec = importlib.util.spec_from_file_location("cookbook_moltbot_main", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load cookbook module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCookbookMoltbotCommandBuilder(unittest.TestCase):
    @pytest.mark.sync
    def test_build_command_without_feishu(self):
        module = _load_cookbook_module()
        env = module.MoltbotEnv(
            dashscope_api_key="dashscope-key",
            dingtalk_client_id=None,
            dingtalk_client_secret=None,
            feishu_app_id=None,
            feishu_app_secret=None,
        )
        cmd = module.build_moltbot_config_command(env, bot_cmd="moltbot")
        expected = (
            "moltbot config set models.providers.bailian.apiKey dashscope-key && "
            "moltbot gateway restart"
        )
        self.assertEqual(cmd, expected)

    @pytest.mark.sync
    def test_build_command_with_feishu(self):
        module = _load_cookbook_module()
        env = module.MoltbotEnv(
            dashscope_api_key=None,
            dingtalk_client_id="dt-id",
            dingtalk_client_secret="dt-secret",
            feishu_app_id="fs id",
            feishu_app_secret="fs-secret",
        )
        cmd = module.build_moltbot_config_command(env, bot_cmd="clawdbot")
        expected = (
            "clawdbot config set channels.feishu.appId 'fs id' && "
            "clawdbot config set channels.feishu.appSecret fs-secret && "
            "clawdbot config set channels.dingtalk.clientId dt-id && "
            "clawdbot config set channels.dingtalk.clientSecret dt-secret && "
            "clawdbot gateway restart"
        )
        self.assertEqual(cmd, expected)

    @pytest.mark.sync
    def test_build_command_feishu_partial_raises(self):
        module = _load_cookbook_module()
        env = module.MoltbotEnv(
            dashscope_api_key=None,
            dingtalk_client_id="dt-id",
            dingtalk_client_secret="dt-secret",
            feishu_app_id="fs-id",
            feishu_app_secret=None,
        )
        with self.assertRaises(ValueError) as ctx:
            module.build_moltbot_config_command(env, bot_cmd="moltbot")
        self.assertIn("FEISHU_APP_ID", str(ctx.exception))

    @pytest.mark.sync
    def test_build_command_dingtalk_partial_raises(self):
        module = _load_cookbook_module()
        env = module.MoltbotEnv(
            dashscope_api_key=None,
            dingtalk_client_id="dt-id",
            dingtalk_client_secret=None,
            feishu_app_id=None,
            feishu_app_secret=None,
        )
        with self.assertRaises(ValueError) as ctx:
            module.build_moltbot_config_command(env, bot_cmd="moltbot")
        self.assertIn("DINGTALK_CLIENT_ID", str(ctx.exception))

    @pytest.mark.sync
    def test_build_command_none_when_no_config(self):
        module = _load_cookbook_module()
        env = module.MoltbotEnv(
            dashscope_api_key=None,
            dingtalk_client_id=None,
            dingtalk_client_secret=None,
            feishu_app_id=None,
            feishu_app_secret=None,
        )
        cmd = module.build_moltbot_config_command(env, bot_cmd="moltbot")
        self.assertIsNone(cmd)

