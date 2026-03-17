import json
import pytest
import os
import sys
import unittest
from unittest.mock import MagicMock, MagicMock, patch

from agentbay import BrowserContext, BrowserSyncMode, CreateSessionParams
from agentbay import AgentBay


MINIMAL_PATHS = [
    "/Local State",
    "/Default/Cookies",
    "/Default/Cookies-journal",
]

STANDARD_PATHS = [
    "/Local State",
    "/Default/Cookies",
    "/Default/Cookies-journal",
    "/Default/Local Storage",
    "/Default/IndexedDB",
    "/Default/Session Storage",
    "/Default/Login Data",
    "/Default/Login Data-journal",
    "/Default/Login Data For Account",
    "/Default/Login Data For Account-journal",
    "/Default/Web Data",
    "/Default/Web Data-journal",
    "/Default/Preferences",
    "/Default/Secure Preferences",
    "/Default/TransportSecurity",
    "/Default/Network Persistent State",
    "/Default/GPUCache",
    "/Default/Affiliation Database",
    "/Default/Affiliation Database-journal",
]


def _build_policy_dict(white_list_paths):
    """Helper to build and serialize a SyncPolicy with given whitelist paths."""
    from agentbay import BWList, SyncPolicy, UploadPolicy, WhiteList

    upload_policy = UploadPolicy(auto_upload=True)
    white_lists = [WhiteList(path=p, exclude_paths=[]) for p in white_list_paths]
    bw_list = BWList(white_lists=white_lists)
    sync_policy = SyncPolicy(upload_policy=upload_policy, bw_list=bw_list)

    policy_json = json.dumps(
        sync_policy,
        default=lambda obj: (
            obj.__dict__() if hasattr(obj, "__dict__") else str(obj)
        ),
        ensure_ascii=False,
    )
    return json.loads(policy_json)


class TestAsyncBrowserContextPolicy(unittest.TestCase):
    """Test that browser_context policy includes BWList with white lists."""

    @pytest.mark.sync
    def test_default_sync_mode_is_standard(self):
        """Default BrowserContext should use STANDARD sync mode."""
        bc = BrowserContext(context_id="test-ctx", auto_upload=True)
        self.assertEqual(bc.sync_mode, BrowserSyncMode.STANDARD)

    @pytest.mark.sync
    def test_explicit_minimal_sync_mode(self):
        bc = BrowserContext(
            context_id="test-ctx", auto_upload=True,
            sync_mode=BrowserSyncMode.MINIMAL,
        )
        self.assertEqual(bc.sync_mode, BrowserSyncMode.MINIMAL)

    @pytest.mark.sync
    def test_standard_mode_policy(self):
        """STANDARD mode policy should contain 19 whitelist entries."""
        policy_dict = _build_policy_dict(STANDARD_PATHS)

        self.assertIn("bwList", policy_dict)
        self.assertIn("whiteLists", policy_dict["bwList"])

        white_lists = policy_dict["bwList"]["whiteLists"]
        self.assertEqual(len(white_lists), 19,
                         f"Expected 19 white lists, got {len(white_lists)}")

        paths = [wl["path"] for wl in white_lists]
        for expected_path in STANDARD_PATHS:
            self.assertIn(expected_path, paths,
                          f"Expected path {expected_path} not found in white lists")

    @pytest.mark.sync
    def test_minimal_mode_policy(self):
        """MINIMAL mode policy should contain 3 whitelist entries."""
        policy_dict = _build_policy_dict(MINIMAL_PATHS)

        self.assertIn("bwList", policy_dict)
        self.assertIn("whiteLists", policy_dict["bwList"])

        white_lists = policy_dict["bwList"]["whiteLists"]
        self.assertEqual(len(white_lists), 3,
                         f"Expected 3 white lists, got {len(white_lists)}")

        paths = [wl["path"] for wl in white_lists]
        for expected_path in MINIMAL_PATHS:
            self.assertIn(expected_path, paths,
                          f"Expected path {expected_path} not found in white lists")


if __name__ == "__main__":
    unittest.main()
