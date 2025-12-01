import os
import time
import unittest
import httpx
from agentbay import AsyncAgentBay


class TestContextFileUrlsIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        api_key = os.environ.get("AGENTBAY_API_KEY")
        if not api_key or os.environ.get("CI"):
            raise unittest.SkipTest(
                "Skipping integration test: No API key available or running in CI"
            )
        self.agent_bay = AsyncAgentBay(api_key)

        # Create a test context
        self.context_name = f"test-file-url-py-{int(time.time())}"
        context_result = await self.agent_bay.context.create(self.context_name)
        if not context_result.success or not context_result.context:
            raise unittest.SkipTest("Failed to create context for file URL test")
        self.context = context_result.context
        print(f"Created context: {self.context.name} (ID: {self.context.id})")

    async def asyncTearDown(self):
        # Clean up created context
        if hasattr(self, "context"):
            try:
                await self.agent_bay.context.delete(self.context)
                print(f"Deleted context: {self.context.name} (ID: {self.context.id})")
            except Exception as e:
                print(f"Warning: Failed to delete context {self.context.name}: {e}")

    async def test_get_file_upload_url(self):
        """
        Create a context and request a presigned upload URL for a test path.
        Validate that a URL is returned.
        """
        test_path = "/tmp/integration_upload_test.txt"
        result = await self.agent_bay.context.get_file_upload_url(
            self.context.id, test_path
        )

        self.assertTrue(
            result.request_id is not None and isinstance(result.request_id, str)
        )
        self.assertTrue(result.success, "get_file_upload_url should be successful")
        self.assertTrue(
            isinstance(result.url, str) and len(result.url) > 0,
            "URL should be non-empty",
        )
        if result.expire_time is not None:
            self.assertTrue(isinstance(result.expire_time, int))

        print(f"Upload URL: {result.url[:80]}... (RequestID: {result.request_id})")

        # Use the obtained presigned URL to upload content to OSS
        upload_content = (
            f"agentbay integration upload test at {int(time.time())}\n".encode("utf-8")
        )
        async with httpx.AsyncClient() as client:
            response = await client.put(
                result.url, content=upload_content, timeout=30.0
            )

        self.assertIn(
            response.status_code,
            (200, 204),
            f"Upload failed with status code {response.status_code}",
        )
        etag = response.headers.get("ETag")
        print(
            f"Uploaded {len(upload_content)} bytes, status={response.status_code}, ETag={etag}"
        )

        # Fetch a presigned download URL for the same file and verify content
        dl_result = await self.agent_bay.context.get_file_download_url(
            self.context.id, test_path
        )
        self.assertTrue(dl_result.success, "get_file_download_url should be successful")
        self.assertTrue(
            isinstance(dl_result.url, str) and len(dl_result.url) > 0,
            "Download URL should be non-empty",
        )
        print(
            f"Download URL: {dl_result.url[:80]}... (RequestID: {dl_result.request_id})"
        )

        async with httpx.AsyncClient() as client:
            dl_resp = await client.get(dl_result.url, timeout=30.0)

        self.assertEqual(
            dl_resp.status_code,
            200,
            f"Download failed with status code {dl_resp.status_code}",
        )
        self.assertEqual(
            dl_resp.content,
            upload_content,
            "Downloaded content does not match uploaded content",
        )
        print(f"Downloaded {len(dl_resp.content)} bytes, content matches uploaded data")

        # List files to verify presence of the uploaded file under /tmp
        file_name = os.path.basename(test_path)

        async def list_contains():
            res = await self.agent_bay.context.list_files(
                self.context.id, "/tmp", page_number=1, page_size=50
            )
            if not res or not res.success:
                return False, res, "/tmp"
            found_local = any(
                (getattr(e, "file_path", "") == test_path)
                or (getattr(e, "file_name", "") == file_name)
                for e in res.entries
            )
            if found_local or len(res.entries) > 0:
                return found_local, res, "/tmp"
            return False, res, "/tmp"

        found = False
        last_lf_res = None
        chosen_parent = None
        retries_presence = 0
        for _ in range(30):
            found, last_lf_res, chosen_parent = await list_contains()
            if found:
                break
            retries_presence += 1
            await asyncio.sleep(2.0)  # Use asyncio.sleep
        print(f"List files retry attempts (presence check): {retries_presence}")

        if last_lf_res and chosen_parent:
            total = (
                last_lf_res.count
                if getattr(last_lf_res, "count", None) is not None
                else len(last_lf_res.entries)
            )
            print(
                f"List files: checked parent={chosen_parent}, total={total}, contains={found}"
            )
        else:
            print("List files: no listing result available")

        if last_lf_res and len(last_lf_res.entries) > 0:
            self.assertTrue(found, "Uploaded file should appear in list_files")

        # Delete the file and verify it disappears
        op = await self.agent_bay.context.delete_file(self.context.id, test_path)
        self.assertTrue(op.success, "delete_file should be successful")
        print(f"Deleted file: {test_path}")

        removed = False
        retries_deletion = 0
        for _ in range(20):
            present, _, _ = await list_contains()
            if last_lf_res and len(last_lf_res.entries) > 0:
                if not present:
                    removed = True
                    break
                removed = False
            else:
                removed = True
                break
            retries_deletion += 1
            await asyncio.sleep(1.0)
        print(f"List files retry attempts (deletion check): {retries_deletion}")
        self.assertTrue(
            removed,
            "Deleted file should not appear in list_files when listing is available",
        )
        if last_lf_res:
            prev = (
                last_lf_res.count
                if getattr(last_lf_res, "count", None) is not None
                else len(last_lf_res.entries)
            )
            print(
                f"List files: {file_name} absent after delete (listing availability: {prev})"
            )

        try:
            post_dl = await self.agent_bay.context.get_file_download_url(
                self.context.id, test_path
            )
            if (
                post_dl.success
                and isinstance(post_dl.url, str)
                and len(post_dl.url) > 0
            ):
                async with httpx.AsyncClient() as client:
                    post_resp = await client.get(post_dl.url, timeout=30.0)
                print(
                    f"Post-delete download status (informational): {post_resp.status_code}"
                )
            else:
                print("Post-delete: download URL not available, treated as deleted")
        except Exception as e:
            print(
                f"Post-delete: download URL request failed as expected: {type(e).__name__}"
            )


if __name__ == "__main__":
    import asyncio

    unittest.main()
