from dataclasses import asdict

import pytest

from qso_runtime.warp_field_experiment import (
    GridSpec,
    LearningSpec,
    WarpParameters,
    run_experiment,
)


def test_zero_velocity_has_zero_inferred_energy() -> None:
    report = run_experiment(
        GridSpec(half_extent_m=12.0, points_per_axis=17),
        WarpParameters(
            bubble_radius_m=3.0,
            wall_inverse_width_per_m=0.8,
            coordinate_velocity_fraction_c=0.0,
        ),
        LearningSpec(iterations=0, seed=7),
    )
    diagnostics = report.final_diagnostics
    assert diagnostics["finite"] is True
    assert diagnostics["total_energy_j"] == pytest.approx(0.0, abs=1e-12)
    assert diagnostics["absolute_mass_equivalent_kg"] == pytest.approx(0.0, abs=1e-12)


def test_nonzero_shift_reports_negative_and_absolute_energy_burden() -> None:
    report = run_experiment(
        GridSpec(half_extent_m=16.0, points_per_axis=21),
        WarpParameters(
            bubble_radius_m=4.0,
            wall_inverse_width_per_m=0.7,
            coordinate_velocity_fraction_c=0.02,
        ),
        LearningSpec(iterations=0, seed=11),
    )
    diagnostics = report.final_diagnostics
    assert diagnostics["finite"] is True
    assert diagnostics["negative_energy_j"] < 0.0
    assert diagnostics["absolute_mass_equivalent_kg"] > 0.0
    assert diagnostics["resolution_indicator"] > 0.0


def test_learning_is_reproducible_for_fixed_seed() -> None:
    args = (
        GridSpec(half_extent_m=14.0, points_per_axis=17),
        WarpParameters(
            bubble_radius_m=3.0,
            wall_inverse_width_per_m=0.6,
            coordinate_velocity_fraction_c=0.015,
        ),
        LearningSpec(iterations=2, seed=2987),
    )
    first = run_experiment(*args)
    second = run_experiment(*args)
    assert first.reproducibility_hash == second.reproducibility_hash
    assert first.final_parameters == second.final_parameters
    assert first.final_diagnostics == second.final_diagnostics


def test_grid_rejects_even_resolution() -> None:
    with pytest.raises(ValueError):
        run_experiment(
            GridSpec(half_extent_m=10.0, points_per_axis=18),
            WarpParameters(bubble_radius_m=2.0),
            LearningSpec(iterations=0),
        )
