"""Tests static native inspection without importing Sims 4."""
import importlib.util
import os
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULE_PATH = os.path.join(ROOT, "src", "open_neighborhood", "introspection.py")
SPEC = importlib.util.spec_from_file_location("introspection_under_test", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class IntrospectionTests(unittest.TestCase):
    def test_reports_metadata_without_invoking_function(self):
        calls = []

        def dangerous(zone_id):
            """Mock native API docs."""
            calls.append(zone_id)
            raise AssertionError("Never call native API")

        native_mod = types.SimpleNamespace(get_zones_cached_objects=dangerous)
        lines = module.native_info({"_buildbuy": native_mod}, "_buildbuy", "get_zones_cached_objects")
        self.assertEqual(calls, [])
        self.assertIn("assinatura=(zone_id)", "\n".join(lines))
        self.assertIn("Mock native API docs", "\n".join(lines))

    def test_blocks_other_modules(self):
        lines = module.native_info({}, "subprocess", "run")
        self.assertIn("nao permitido", "\n".join(lines))

    def test_class_info_does_not_invoke_property(self):
        class Zone:
            lot = None

            @property
            def load_neighbor(self):
                raise AssertionError("Property getter should not run")

        lines = module.class_info(Zone())
        self.assertIn("load_neighbor [property]", "\n".join(lines))


if __name__ == "__main__":
    unittest.main()
