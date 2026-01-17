import unittest


from agentbay._async.beta_volume import Volume


class TestAsyncBetaVolumeModel(unittest.TestCase):
    def test_volume_exposes_only_id_and_name(self):
        volume = Volume(id="vo-test", name="test-volume")
        self.assertEqual(volume.id, "vo-test")
        self.assertEqual(volume.name, "test-volume")

        # These fields are not used by the SDK and should not be part of the model.
        self.assertFalse(hasattr(volume, "belonging_image_id"))
        self.assertFalse(hasattr(volume, "status"))
        self.assertFalse(hasattr(volume, "created_at"))


if __name__ == "__main__":
    unittest.main()

