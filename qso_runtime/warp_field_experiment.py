from __future__ import annotations

"""Numerical 3+1 warp-field experiment for QSO-FABRIC.

This module evaluates an explicit metric ansatz on a Cartesian grid. It does not
claim physical realization of a warp field. Its outputs are numerical-relativity
observables, constraint diagnostics, and mass-energy estimates for the selected
ansatz and discretization.

The initial implementation uses a flat spatial metric with an Alcubierre-class
shift vector. The architecture keeps the metric source, diagnostics, weighing,
and optimizer separable so a BSSN/CCZ4 backend can replace the finite-difference
ansatz without changing the experiment record format.
"""

import argparse
import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Callable

import numpy as np

C = 299_792_458.0
G = 6.67430e-11
PI = math.pi


@dataclass(frozen=True)
class GridSpec:
    half_extent_m: float = 40.0
    points_per_axis: int = 65

    def validate(self) -> None:
        if self.half_extent_m <= 0:
            raise ValueError("half_extent_m must be positive")
        if self.points_per_axis < 17 or self.points_per_axis % 2 == 0:
            raise ValueError("points_per_axis must be odd and at least 17")


@dataclass(frozen=True)
class WarpParameters:
    bubble_radius_m: float = 10.0
    wall_inverse_width_per_m: float = 0.8
    coordinate_velocity_fraction_c: float = 0.05
    center_x_m: float = 0.0

    def validate(self, grid: GridSpec) -> None:
        if self.bubble_radius_m <= 0:
            raise ValueError("bubble_radius_m must be positive")
        if self.wall_inverse_width_per_m <= 0:
            raise ValueError("wall_inverse_width_per_m must be positive")
        if abs(self.coordinate_velocity_fraction_c) >= 1.0:
            raise ValueError("coordinate velocity must remain subluminal in this backend")
        if self.bubble_radius_m >= 0.8 * grid.half_extent_m:
            raise ValueError("bubble must leave a substantial asymptotic boundary region")


@dataclass(frozen=True)
class LearningSpec:
    iterations: int = 12
    learning_rate: float = 0.08
    perturbation: float = 0.04
    target_effective_mass_kg: float = 0.0
    constraint_weight: float = 1.0
    boundary_weight: float = 1.0
    parameter_weight: float = 1e-4
    seed: int = 2987


@dataclass
class FieldDiagnostics:
    dx_m: float
    total_energy_j: float
    positive_energy_j: float
    negative_energy_j: float
    effective_mass_kg: float
    absolute_mass_equivalent_kg: float
    min_energy_density_j_m3: float
    max_energy_density_j_m3: float
    hamiltonian_l2_j_m3: float
    momentum_l2_si: float
    boundary_shift_max: float
    boundary_gradient_max_per_m: float
    resolution_indicator: float
    finite: bool


@dataclass
class TrialRecord:
    iteration: int
    parameters: dict[str, float]
    loss: float
    diagnostics: dict[str, Any]


@dataclass
class ExperimentReport:
    schema: str
    backend: str
    created_unix_s: float
    initial_parameters: dict[str, float]
    final_parameters: dict[str, float]
    initial_diagnostics: dict[str, Any]
    final_diagnostics: dict[str, Any]
    convergence: list[dict[str, Any]] = field(default_factory=list)
    reproducibility_hash: str = ""
    interpretation: dict[str, str] = field(default_factory=dict)


class AlcubierreShiftBackend:
    """Flat-slice Alcubierre-class shift backend in Cartesian coordinates.

    Lapse alpha=1, gamma_ij=delta_ij, and beta^x=-v f(r), beta^y=beta^z=0.
    The extrinsic curvature is K_ij=(d_i beta_j+d_j beta_i)/2 under the
    stationary-slice convention used here. All spatial derivatives are taken
    with respect to metres, so the curvature prefactor converts the Hamiltonian
    source to SI energy density.
    """

    name = "alcubierre-flat-slice-fd-v1"

    @staticmethod
    def shape(radius: np.ndarray, bubble_radius: float, sigma: float) -> np.ndarray:
        denominator = 2.0 * np.tanh(sigma * bubble_radius)
        return (
            np.tanh(sigma * (radius + bubble_radius))
            - np.tanh(sigma * (radius - bubble_radius))
        ) / denominator

    def evaluate(self, grid: GridSpec, params: WarpParameters) -> FieldDiagnostics:
        grid.validate()
        params.validate(grid)
        n = grid.points_per_axis
        axis = np.linspace(-grid.half_extent_m, grid.half_extent_m, n, dtype=np.float64)
        dx = float(axis[1] - axis[0])
        x, y, z = np.meshgrid(axis, axis, axis, indexing="ij", sparse=True)
        radius = np.sqrt((x - params.center_x_m) ** 2 + y**2 + z**2)
        f = self.shape(radius, params.bubble_radius_m, params.wall_inverse_width_per_m)
        beta_x = -params.coordinate_velocity_fraction_c * f

        dbdx, dbdy, dbdz = np.gradient(beta_x, dx, edge_order=2)

        # Symmetric extrinsic-curvature tensor for the single nonzero shift component.
        k_xx = dbdx
        k_xy = 0.5 * dbdy
        k_xz = 0.5 * dbdz
        trace_k = k_xx
        kij_kij = k_xx**2 + 2.0 * k_xy**2 + 2.0 * k_xz**2

        # R^(3)=0 for gamma_ij=delta_ij. Hamiltonian source in SI energy density.
        geometric_source = trace_k**2 - kij_kij
        energy_density = (C**4 / (16.0 * PI * G)) * geometric_source

        cell_volume = dx**3
        total_energy = float(np.sum(energy_density, dtype=np.float64) * cell_volume)
        positive_energy = float(np.sum(np.clip(energy_density, 0.0, None), dtype=np.float64) * cell_volume)
        negative_energy = float(np.sum(np.clip(energy_density, None, 0.0), dtype=np.float64) * cell_volume)

        # Momentum constraint M_i = d_j(K^j_i-delta^j_i K). Flat connection.
        # Components simplify for this backend but are evaluated explicitly.
        a_xx = k_xx - trace_k
        a_yx = k_xy
        a_zx = k_xz
        a_xy = k_xy
        a_yy = -trace_k
        a_zy = np.zeros_like(k_xx)
        a_xz = k_xz
        a_yz = np.zeros_like(k_xx)
        a_zz = -trace_k
        mx = np.gradient(a_xx, dx, axis=0, edge_order=2) + np.gradient(a_yx, dx, axis=1, edge_order=2) + np.gradient(a_zx, dx, axis=2, edge_order=2)
        my = np.gradient(a_xy, dx, axis=0, edge_order=2) + np.gradient(a_yy, dx, axis=1, edge_order=2) + np.gradient(a_zy, dx, axis=2, edge_order=2)
        mz = np.gradient(a_xz, dx, axis=0, edge_order=2) + np.gradient(a_yz, dx, axis=1, edge_order=2) + np.gradient(a_zz, dx, axis=2, edge_order=2)
        momentum_norm = np.sqrt(mx**2 + my**2 + mz**2)

        boundary = np.concatenate(
            [
                beta_x[0, :, :].ravel(), beta_x[-1, :, :].ravel(),
                beta_x[:, 0, :].ravel(), beta_x[:, -1, :].ravel(),
                beta_x[:, :, 0].ravel(), beta_x[:, :, -1].ravel(),
            ]
        )
        boundary_grad = np.concatenate(
            [
                dbdx[0, :, :].ravel(), dbdx[-1, :, :].ravel(),
                dbdy[:, 0, :].ravel(), dbdy[:, -1, :].ravel(),
                dbdz[:, :, 0].ravel(), dbdz[:, :, -1].ravel(),
            ]
        )

        # The Hamiltonian residual is zero algebraically only if the inferred rho is
        # admitted as the source. We therefore report the source magnitude as the
        # stress-energy burden required by the ansatz, not as a solved-vacuum residual.
        h_l2 = float(np.sqrt(np.mean(energy_density**2, dtype=np.float64)))
        m_l2 = float(np.sqrt(np.mean(momentum_norm**2, dtype=np.float64)))
        finite = bool(np.isfinite(energy_density).all() and np.isfinite(momentum_norm).all())

        # Resolution indicator: wall e-folding scale represented by grid intervals.
        wall_scale = 1.0 / params.wall_inverse_width_per_m
        resolution_indicator = wall_scale / dx

        return FieldDiagnostics(
            dx_m=dx,
            total_energy_j=total_energy,
            positive_energy_j=positive_energy,
            negative_energy_j=negative_energy,
            effective_mass_kg=total_energy / C**2,
            absolute_mass_equivalent_kg=(positive_energy - negative_energy) / C**2,
            min_energy_density_j_m3=float(np.min(energy_density)),
            max_energy_density_j_m3=float(np.max(energy_density)),
            hamiltonian_l2_j_m3=h_l2,
            momentum_l2_si=m_l2,
            boundary_shift_max=float(np.max(np.abs(boundary))),
            boundary_gradient_max_per_m=float(np.max(np.abs(boundary_grad))),
            resolution_indicator=float(resolution_indicator),
            finite=finite,
        )


class SelfWeighingLearner:
    """Bounded simultaneous-perturbation optimizer over declared parameters."""

    def __init__(self, backend: AlcubierreShiftBackend, grid: GridSpec, spec: LearningSpec) -> None:
        self.backend = backend
        self.grid = grid
        self.spec = spec
        self.rng = np.random.default_rng(spec.seed)

    @staticmethod
    def _vector(params: WarpParameters) -> np.ndarray:
        return np.array(
            [params.bubble_radius_m, params.wall_inverse_width_per_m, params.coordinate_velocity_fraction_c],
            dtype=np.float64,
        )

    def _params(self, vector: np.ndarray, center_x_m: float) -> WarpParameters:
        radius = float(np.clip(vector[0], 0.5, 0.70 * self.grid.half_extent_m))
        sigma = float(np.clip(vector[1], 0.02, 8.0))
        velocity = float(np.clip(vector[2], -0.80, 0.80))
        return WarpParameters(radius, sigma, velocity, center_x_m)

    def loss(self, params: WarpParameters, diagnostics: FieldDiagnostics) -> float:
        mass_scale = max(abs(self.spec.target_effective_mass_kg), 1.0)
        mass_error = (diagnostics.effective_mass_kg - self.spec.target_effective_mass_kg) / mass_scale
        constraint_scale = max(diagnostics.absolute_mass_equivalent_kg, 1.0)
        constraint_term = (diagnostics.hamiltonian_l2_j_m3 * self.grid.half_extent_m**3 / C**2) / constraint_scale
        boundary_term = diagnostics.boundary_shift_max + self.grid.half_extent_m * diagnostics.boundary_gradient_max_per_m
        under_resolution = max(0.0, 4.0 - diagnostics.resolution_indicator)
        regularizer = self.spec.parameter_weight * (
            params.coordinate_velocity_fraction_c**2
            + (params.bubble_radius_m / self.grid.half_extent_m) ** 2
            + (params.wall_inverse_width_per_m * self.grid.half_extent_m / 20.0) ** 2
        )
        return float(
            mass_error**2
            + self.spec.constraint_weight * constraint_term**2
            + self.spec.boundary_weight * boundary_term**2
            + under_resolution**2
            + regularizer
        )

    def optimize(self, initial: WarpParameters) -> tuple[WarpParameters, list[TrialRecord]]:
        theta = self._vector(initial)
        records: list[TrialRecord] = []
        center = initial.center_x_m
        for iteration in range(self.spec.iterations):
            ck = self.spec.perturbation / ((iteration + 1) ** 0.101)
            ak = self.spec.learning_rate / ((iteration + 1) ** 0.602)
            delta = self.rng.choice(np.array([-1.0, 1.0]), size=theta.shape)
            plus = self._params(theta + ck * delta, center)
            minus = self._params(theta - ck * delta, center)
            d_plus = self.backend.evaluate(self.grid, plus)
            d_minus = self.backend.evaluate(self.grid, minus)
            l_plus = self.loss(plus, d_plus)
            l_minus = self.loss(minus, d_minus)
            gradient = ((l_plus - l_minus) / (2.0 * ck)) * delta
            gradient = np.clip(gradient, -10.0, 10.0)
            theta = theta - ak * gradient
            current = self._params(theta, center)
            diagnostics = self.backend.evaluate(self.grid, current)
            records.append(
                TrialRecord(
                    iteration=iteration,
                    parameters=asdict(current),
                    loss=self.loss(current, diagnostics),
                    diagnostics=asdict(diagnostics),
                )
            )
        return self._params(theta, center), records


def _canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def run_experiment(
    grid: GridSpec | None = None,
    initial: WarpParameters | None = None,
    learning: LearningSpec | None = None,
) -> ExperimentReport:
    grid = grid or GridSpec()
    initial = initial or WarpParameters()
    learning = learning or LearningSpec()
    backend = AlcubierreShiftBackend()
    initial_diagnostics = backend.evaluate(grid, initial)
    learner = SelfWeighingLearner(backend, grid, learning)
    final, convergence = learner.optimize(initial)
    final_diagnostics = backend.evaluate(grid, final)
    report = ExperimentReport(
        schema="qso.warp-field-experiment.v1",
        backend=backend.name,
        created_unix_s=time.time(),
        initial_parameters=asdict(initial),
        final_parameters=asdict(final),
        initial_diagnostics=asdict(initial_diagnostics),
        final_diagnostics=asdict(final_diagnostics),
        convergence=[asdict(item) for item in convergence],
        interpretation={
            "effective_mass_kg": "Volume integral of inferred Eulerian energy density divided by c^2.",
            "absolute_mass_equivalent_kg": "Integral of absolute positive and negative energy burden divided by c^2.",
            "hamiltonian_l2_j_m3": "RMS stress-energy density required by the selected spatial metric, lapse, and shift ansatz.",
            "momentum_l2_si": "RMS momentum-constraint source magnitude before assigning matter momentum density.",
            "scope": "Numerical model output; not evidence that the metric or required stress-energy can be physically produced.",
        },
    )
    hash_payload = asdict(report)
    hash_payload["created_unix_s"] = 0.0
    hash_payload["reproducibility_hash"] = ""
    report.reproducibility_hash = _canonical_hash(hash_payload)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the QSO self-weighing adaptive warp-field experiment")
    parser.add_argument("--extent", type=float, default=40.0, help="Grid half-extent in metres")
    parser.add_argument("--points", type=int, default=65, help="Odd grid points per axis")
    parser.add_argument("--radius", type=float, default=10.0, help="Bubble radius in metres")
    parser.add_argument("--sigma", type=float, default=0.8, help="Wall inverse width per metre")
    parser.add_argument("--velocity", type=float, default=0.05, help="Coordinate velocity as a fraction of c")
    parser.add_argument("--iterations", type=int, default=12)
    parser.add_argument("--target-mass", type=float, default=0.0, help="Target signed effective mass in kg")
    parser.add_argument("--seed", type=int, default=2987)
    parser.add_argument("--output", type=Path, default=Path("artifacts/warp_field_report.json"))
    args = parser.parse_args()

    report = run_experiment(
        GridSpec(args.extent, args.points),
        WarpParameters(args.radius, args.sigma, args.velocity),
        LearningSpec(iterations=args.iterations, target_effective_mass_kg=args.target_mass, seed=args.seed),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(asdict(report), indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "backend": report.backend,
                "effective_mass_kg": report.final_diagnostics["effective_mass_kg"],
                "absolute_mass_equivalent_kg": report.final_diagnostics["absolute_mass_equivalent_kg"],
                "reproducibility_hash": report.reproducibility_hash,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
