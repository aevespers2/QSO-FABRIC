import math
import unittest

from qso_runtime.laser_refraction_fusion import (
    OpticalInput,
    PlasmaInput,
    SimulationLimits,
    optical_transfer,
    refracted_angle_rad,
    run_simulation,
)


class LaserRefractionFusionTests(unittest.TestCase):
    def test_snell_law(self) -> None:
        optical = OpticalInput(
            incidence_angle_deg=30.0,
            refractive_index_in=1.0,
            refractive_index_out=1.5,
        )
        theta_out = refracted_angle_rad(optical)
        self.assertAlmostEqual(
            optical.refractive_index_in * math.sin(math.radians(optical.incidence_angle_deg)),
            optical.refractive_index_out * math.sin(theta_out),
            places=14,
        )

    def test_total_internal_reflection_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            refracted_angle_rad(
                OpticalInput(
                    incidence_angle_deg=60.0,
                    refractive_index_in=1.5,
                    refractive_index_out=1.0,
                )
            )

    def test_zero_power_has_zero_torque(self) -> None:
        transfer = optical_transfer(OpticalInput(power_w=0.0))
        self.assertEqual(tuple(transfer["torque_vector_nm"]), (0.0, 0.0, 0.0))
        self.assertEqual(transfer["photons_in_pulse"], 0.0)

    def test_deterministic_report(self) -> None:
        first = run_simulation()
        second = run_simulation()
        self.assertEqual(first["report_sha256"], second["report_sha256"])
        self.assertEqual(first["states"], second["states"])

    def test_positive_coupled_torque_spins_plasma(self) -> None:
        report = run_simulation(
            OpticalInput(
                power_w=5_000.0,
                pulse_duration_s=5e-9,
                topological_charge=2,
                helicity=1,
                absorption_fraction=0.8,
                angular_momentum_coupling=0.9,
            ),
            PlasmaInput(rotational_damping_s_inv=0.0),
            time_step_s=1e-9,
        )
        self.assertGreater(report["final"]["angular_velocity_rad_s"], 0.0)
        self.assertGreater(report["final"]["rotational_energy_j"], 0.0)

    def test_limits_fail_closed(self) -> None:
        limits = SimulationLimits(max_power_w=10.0)
        with self.assertRaises(ValueError):
            run_simulation(OpticalInput(power_w=11.0), limits=limits)

    def test_momentum_conventions_are_explicit(self) -> None:
        values = {}
        for convention in ("abraham", "minkowski", "vacuum"):
            values[convention] = optical_transfer(
                OpticalInput(momentum_convention=convention)
            )["torque_vector_nm"]
        self.assertNotEqual(values["abraham"], values["minkowski"])
        self.assertNotEqual(values["vacuum"], values["minkowski"])

    def test_fusion_proxy_is_labeled(self) -> None:
        report = run_simulation()
        self.assertIn("not an engineering design", report["scope"])
        self.assertTrue(any("normalized research proxy" in item for item in report["uncertainties"]))


if __name__ == "__main__":
    unittest.main()
