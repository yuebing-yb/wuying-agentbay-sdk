# =============================================================================
# conftest.py  –  Shared fixtures for _sync integration tests
#
# This file is loaded automatically by pytest; no explicit import is needed.
# It exposes the ``make_session`` factory fixture for every test file under
# the _sync/ directory.
#
# Key capabilities:
#   - Wraps all three SyncSessionLifecycle creation modes in one entry point:
#       default_create / create_with_context_name / create_with_browser_name
#   - Unified SessionLifecycleError handling:
#       "no authorized app"  → pytest.skip  (environment not authorised)
#       any other failure    → pytest.fail  (code / network issue)
#   - scope="function": each session is deleted immediately after its test
#     function finishes.
#
# When adding a new creation mode, update session_life_functional.py and add
# the corresponding branch in _factory; keep _async/conftest.py in sync.
# =============================================================================
"""
Shared pytest fixtures for _sync integration tests.

Provides a factory fixture ``make_session`` that creates a
SyncSessionLifecycle instance on demand, supports all three creation modes
(default / context_name / browser_name), and cleans up all sessions when
the test function ends.

Usage::

    def test_something(make_session):
        lc = make_session("linux_latest")
        status = lc.get_status()
        assert status

    def test_browser(make_session):
        lc = make_session("linux_latest", browser_name="ctx", browser_kwargs={"auto_upload": True})
        assert lc._result.session.session_id

    def test_ctx_sync(make_session):
        lc = make_session("linux_latest", context_name="ctx", context_path="/data", context_policy=my_policy)
        assert lc._result.session.session_id
"""

import pytest

from .._common import SyncSessionLifecycle, SessionLifecycleError


@pytest.fixture(scope="function")
def make_session():
    """
    Factory fixture: create a SyncSessionLifecycle with any imageId and
    creation mode.  All sessions created through this factory are
    automatically deleted when the test function ends.

    Args passed to the factory callable:
        image_id (str): Required.  The image ID to create the session with.
        context_name (str): Optional context name for create_with_context_name.
        context_path (str): Optional path for create_with_context_name.
        context_policy: Required SyncPolicy when context_name is provided.
        browser_name (str): Optional context name for create_with_browser_name.
        browser_kwargs (dict): Optional kwargs forwarded to BrowserContext.

    Returns:
        SyncSessionLifecycle with a cached session result.

    Raises (inside the factory):
        pytest.skip  – when "no authorized app" is in the error message.
        pytest.fail  – for all other creation failures.
    """
    created: list[SyncSessionLifecycle] = []

    def _factory(image_id: str = None, *, params=None, context_name=None, context_path=None, context_policy=None, browser_name=None, browser_kwargs=None):
        lc = SyncSessionLifecycle()
        try:
            if context_name is not None:
                lc.create_with_context_name(image_id, context_name, path=context_path or "", policy=context_policy)
            elif browser_name is not None:
                lc.create_with_browser_name(image_id, browser_name, **(browser_kwargs or {}))
            else:
                lc.default_create(image_id, params=params)
        except SessionLifecycleError as e:
            if "no authorized app" in str(e):
                pytest.skip(str(e))
            pytest.fail(str(e))
        created.append(lc)
        return lc

    yield _factory

    # Teardown: clean up all sessions created during this test function
    for lc in created:
        try:
            result = lc.delete()
            assert result.success, f"Session delete failed: {result.error_message}"
        except SessionLifecycleError as e:
            print(f"Warning: teardown delete failed: {e}")

