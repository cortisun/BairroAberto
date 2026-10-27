"""Run with: python -m unittest discover -s tests -v

No Sims installation is needed. We exercise only the read-only planning layer.
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE_PATH = os.path.join(ROOT, "src", "open_neighborhood", "probe.py")
SPEC = importlib.util.spec_from_file_location("probe_under_test", PROBE_PATH)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class FakeField:
    def __init__(self, name):
        self.name = name


class FakeDescriptor:
    fields = [FakeField("zone_instance_id"), FakeField("lot_instance_id")]


class FakeLot:
    DESCRIPTOR = FakeDescriptor()

    def __init__(self, zone, lot):
        self.zone_instance_id = zone
        self.lot_instance_id = lot


class FakeZone:
    neighborhood_id = 123
    world_id = 456


class FakeProto:
    def __init__(self, lots):
        self.lots = lots


class FakePersistence:
    def __init__(self, proto):
        self.proto = proto

    def get_neighborhood_proto_buff(self, neighborhood_id):
        if neighborhood_id != 123:
            raise AssertionError("wrong neighborhood")
        return self.proto


class FakeServices:
    def __init__(self, lots):
        self.persistence = FakePersistence(FakeProto(lots))

    def current_zone(self):
        return FakeZone()

    def current_zone_id(self):
        return 11

    def get_zone_manager(self):
        return {11: object()}

    def get_persistence_service(self):
        return self.persistence

    def load_zone(self, target):
        raise AssertionError("unexpected zone load")


class BrokenServices(FakeServices):
    def get_persistence_service(self):
        raise RuntimeError("mock failure")


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.services = FakeServices([FakeLot(11, 101), FakeLot(22, 202)])

    def test_overview_distinguishes_loaded_from_neighbor(self):
        report = "\n".join(probe.overview(self.services))
        self.assertIn("lotes_no_bairro=2", report)
        self.assertIn("zona=11 descricao=<ausente> ativo=True no_ZoneManager=True", report)
        self.assertIn("zona=22 descricao=<ausente> ativo=False no_ZoneManager=False", report)

    def test_inspect_neighbor_does_not_load_it(self):
        report = "\n".join(probe.inspect_neighbor(self.services, 22))
        self.assertIn("no_ZoneManager=False", report)
        self.assertIn("lot_instance_id=202", report)
        self.assertIn("campos_do_registro=zone_instance_id, lot_instance_id", report)

    def test_missing_neighbor_is_reported(self):
        report = "\n".join(probe.inspect_neighbor(self.services, 999))
        self.assertIn("zona nao encontrada", report)

    def test_service_failure_does_not_escape(self):
        report = "\n".join(probe.overview(BrokenServices([])))
        self.assertIn("persistence: RuntimeError", report)

    def test_overview_is_bounded(self):
        lots = [FakeLot(1000 + index, 2000 + index) for index in range(40)]
        report = probe.overview(FakeServices(lots))
        self.assertIn("[8 lotes omitidos]", "\n".join(report))
        self.assertEqual(sum(line.startswith("zona=") for line in report), 32)

    def test_safe_attr_does_not_repr_game_object(self):
        class Dangerous:
            def __repr__(self):
                raise AssertionError("repr must not execute")

        class Holder:
            child = Dangerous()

        self.assertEqual(probe.safe_attr(Holder(), "child"), "<Dangerous>")


if __name__ == "__main__":
    unittest.main()
