import unittest


from agentbay._sync.beta_volume import Volume


class TestAsyncBetaVolumeModel(unittest.TestCase):
    def test_volume_exposes_id_name_and_status(self):
        volume = Volume(id="vo-test", name="test-volume", status="Available")
        self.assertEqual(volume.id, "vo-test")
        self.assertEqual(volume.name, "test-volume")
        self.assertEqual(volume.status, "Available")

        # These fields are not used by the SDK and should not be part of the model.
        self.assertFalse(hasattr(volume, "belonging_image_id"))
        self.assertFalse(hasattr(volume, "created_at"))


if __name__ == "__main__":
    unittest.main()

