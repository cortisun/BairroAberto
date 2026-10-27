"""Mock tests only: TS4 native placement must still be validated in the game."""
import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "src", "open_neighborhood", "neighbor_preview.py")

fake_diag = types.SimpleNamespace(_mods_dir=lambda: "", log_exception=lambda *a: None)
fake_package = types.ModuleType("open_neighborhood")
fake_package.diag = fake_diag
with mock.patch.dict(sys.modules, {"open_neighborhood": fake_package}):
    spec = importlib.util.spec_from_file_location("preview_under_test", PATH)
    preview = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(preview)


class MockObject:
    def __init__(self, definition=123, pos=(10, 2, 30), parent=None):
        self.definition = types.SimpleNamespace(id=definition)
        translation = types.SimpleNamespace(x=pos[0], y=pos[1], z=pos[2])
        orientation = types.SimpleNamespace(x=0, y=0, z=0, w=1)
        transform = types.SimpleNamespace(translation=translation, orientation=orientation)
        routing_surface = types.SimpleNamespace(secondary_id=0, type=0)
        self.location = types.SimpleNamespace(transform=transform, routing_surface=routing_surface)
        self.is_sim = False
        self.parent = parent
        self.is_in_inventory = False

    def __str__(self):
        return "Chair"


class MockServices:
    def __init__(self, zone_id=100):
        self.zone_id = zone_id
        self.zone = types.SimpleNamespace(neighborhood_id=201, world_id=301)
        self.objects = {1: MockObject(), 2: MockObject(parent=object())}

    def current_zone(self):
        return self.zone

    def current_zone_id(self):
        return self.zone_id

    def object_manager(self):
        return self.objects


class PreviewTests(unittest.TestCase):
    def tearDown(self):
        preview._preview_objects = []

    def test_capture_skips_attached_objects(self):
        data = preview.capture(MockServices())
        self.assertEqual(data["source_zone_id"], 100)
        self.assertEqual(len(data["objects"]), 1)
        self.assertEqual(data["objects"][0]["definition_id"], 123)

    def test_snapshot_rejects_corrupt_position(self):
        self.assertIsNone(preview.snapshot_object(MockObject(pos=(float("nan"), 0, 0))))

    def test_capture_roundtrip_and_wrong_world_guard(self):
        data = preview.capture(MockServices())
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch.object(preview, "capture_path", return_value=os.path.join(temp, "capture.json")):
                preview.save_capture(data)
                loaded = preview.load_capture()
                self.assertEqual(json.dumps(loaded, sort_keys=True), json.dumps(data, sort_keys=True))
        with self.assertRaises(ValueError):
            preview.selected(data, 0, MockServices(zone_id=100))
        other = MockServices(zone_id=400)
        other.zone.world_id = 302
        with self.assertRaises(ValueError):
            preview.selected(data, 0, other)
        self.assertEqual(preview.selected(data, 0, MockServices(zone_id=400))["definition_id"], 123)

    def test_invalid_capture_is_rejected(self):
        data = preview.capture(MockServices())
        data["objects"][0]["position"] = [float("inf"), 0, 0]
        with self.assertRaises(ValueError):
            preview.validate(data)

    def test_cleanup_touches_only_tracked_objects(self):
        class Created:
            destroyed = False

            def destroy(self, **kwargs):
                self.destroyed = True

        created = Created()
        untouched = Created()
        preview._preview_objects = [created]
        self.assertEqual(preview.cleanup(), (1, 0))
        self.assertTrue(created.destroyed)
        self.assertFalse(untouched.destroyed)


if __name__ == "__main__":
    unittest.main()
