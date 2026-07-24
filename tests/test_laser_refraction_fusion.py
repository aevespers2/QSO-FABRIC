import json
import math
import unittest

from qso_runtime.laser_refraction_fusion import (
    OpticalInput,
    PlasmaInput,
    SimulationLimits,
    optical_transfer,
    photon_momentum_magnitude,
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

    def test_deterministic_report_and_strict_json(self) -> None:
        first = run_simulation()
        second = run_simulation()
        self.assertEqual(first["report_sha256"], second["report_sha256"])
        self.assertEqual(first["states"], second["states"])
        json.dumps(first, allow_nan=False)

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
        with self.assertRaises(ValueError):
            run_simulation(OpticalInput(power_w=11.0), limits=SimulationLimits(max_power_w=10.0))
        with self.assertRaises(ValueError):
            run_simulation(limits=SimulationLimits(max_steps=0))
        with self.assertRaises(TypeError):
            run_simulation(limits=SimulationLimits(max_steps=True))

    def test_momentum_conventions_are_explicit(self) -> None:
        values = {
            convention: optical_transfer(OpticalInput(momentum_convention=convention))["torque_vector_nm"]
            for convention in ("abraham", "minkowski", "vacuum")
        }
        self.assertNotEqual(values["abraham"], values["minkowski"])
        self.assertNotEqual(values["vacuum"], values["minkowski"])
        with self.assertRaises(ValueError):
            photon_momentum_magnitude(1e-9, 1.0, "other")  # type: ignore[arg-type]

    def test_fusion_proxy_is_labeled(self) -> None:
        report = run_simulation()
        self.assertIn("not an engineering design", report["scope"])
        self.assertTrue(any("normalized research proxy" in item for item in report["uncertainties"]))

    def test_non_finite_inputs_fail_closed(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    run_simulation(OpticalInput(power_w=value))
                with self.assertRaises(ValueError):
                    run_simulation(time_step_s=value)

    def test_boolean_numeric_inputs_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            run_simulation(OpticalInput(topological_charge=True))
        with self.assertRaises(TypeError):
            run_simulation(OpticalInput(power_w=True))
        with self.assertRaises(TypeError):
            run_simulation(OpticalInput(interface_offset_m=(0.0, False, 0.0)))

    def test_unknown_enums_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            run_simulation(OpticalInput(momentum_convention="other"))  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            run_simulation(plasma=PlasmaInput(reaction="other"))  # type: ignore[arg-type]

    def test_vector_and_charge_bounds_fail_closed(self) -> None:
        with self.assertRaises(TypeError):
            run_simulation(OpticalInput(interface_offset_m=(0.0, 0.0)))  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            run_simulation(
                OpticalInput(interface_offset_m=(11.0, 0.0, 0.0)),
                limits=SimulationLimits(max_interface_offset_m=10.0),
            )
        with self.assertRaises(ValueError):
            run_simulation(
                OpticalInput(topological_charge=11),
                limits=SimulationLimits(max_abs_topological_charge=10),
            )


if __name__ == "__main__":
    unittest.main()
