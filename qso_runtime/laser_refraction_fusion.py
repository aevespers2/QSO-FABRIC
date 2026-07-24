from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

C = 299_792_458.0
H = 6.626_070_15e-34
HBAR = H / (2.0 * math.pi)
E_CHARGE = 1.602_176_634e-19
AMU = 1.660_539_066_60e-27

MomentumConvention = Literal["abraham", "minkowski", "vacuum"]


@dataclass(frozen=True)
class OpticalInput:
    wavelength_m: float = 1_064e-9
    power_w: float = 1_000.0
    pulse_duration_s: float = 1e-9
    incidence_angle_deg: float = 30.0
    refractive_index_in: float = 1.0
    refractive_index_out: float = 1.5
    interface_offset_m: tuple[float, float, float] = (0.0, 1e-3, 0.0)
    topological_charge: int = 1
    helicity: int = 1
    absorption_fraction: float = 0.2
    angular_momentum_coupling: float = 0.35
    momentum_convention: MomentumConvention = "vacuum"


@dataclass(frozen=True)
class PlasmaInput:
    effective_mass_kg: float = 1e-9
    effective_radius_m: float = 5e-4
    initial_angular_velocity_rad_s: float = 0.0
    rotational_damping_s_inv: float = 2e5
    ion_temperature_kev: float = 10.0
    ion_density_m3: float = 1e26
    confinement_time_s: float = 1e-6
    reaction: Literal["DT", "DD"] = "DT"


@dataclass(frozen=True)
class SimulationLimits:
    max_steps: int = 20_000
    max_duration_s: float = 1e-3
    max_power_w: float = 1e12
    max_density_m3: float = 1e32


@dataclass(frozen=True)
class StepState:
    step: int
    time_s: float
    angular_velocity_rad_s: float
    rotational_energy_j: float
    torque_nm: float
    fusion_rate_proxy_s_inv: float
    fusion_events_proxy: float


def _validate(optical: OpticalInput, plasma: PlasmaInput, limits: SimulationLimits) -> None:
    if optical.wavelength_m <= 0 or optical.power_w < 0 or optical.pulse_duration_s <= 0:
        raise ValueError("wavelength and pulse duration must be positive; power must be non-negative")
    if optical.power_w > limits.max_power_w:
        raise ValueError("power exceeds configured simulation bound")
    if not 0.0 <= optical.incidence_angle_deg < 90.0:
        raise ValueError("incidence angle must be in [0, 90) degrees")
    if optical.refractive_index_in <= 0 or optical.refractive_index_out <= 0:
        raise ValueError("refractive indices must be positive")
    if optical.helicity not in (-1, 0, 1):
        raise ValueError("helicity must be -1, 0, or 1")
    if not 0.0 <= optical.absorption_fraction <= 1.0:
        raise ValueError("absorption_fraction must be in [0, 1]")
    if not 0.0 <= optical.angular_momentum_coupling <= 1.0:
        raise ValueError("angular_momentum_coupling must be in [0, 1]")
    if plasma.effective_mass_kg <= 0 or plasma.effective_radius_m <= 0:
        raise ValueError("plasma effective mass and radius must be positive")
    if plasma.rotational_damping_s_inv < 0 or plasma.ion_temperature_kev <= 0:
        raise ValueError("damping must be non-negative and temperature must be positive")
    if plasma.ion_density_m3 <= 0 or plasma.ion_density_m3 > limits.max_density_m3:
        raise ValueError("ion density is outside configured simulation bounds")
    if plasma.confinement_time_s <= 0:
        raise ValueError("confinement time must be positive")


def _unit_direction(angle_rad: float) -> tuple[float, float, float]:
    return (math.sin(angle_rad), 0.0, math.cos(angle_rad))


def _scale(vector: tuple[float, float, float], scalar: float) -> tuple[float, float, float]:
    return tuple(component * scalar for component in vector)  # type: ignore[return-value]


def _subtract(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(x - y for x, y in zip(a, b))  # type: ignore[return-value]


def _cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm(vector: tuple[float, float, float]) -> float:
    return math.sqrt(sum(component * component for component in vector))


def refracted_angle_rad(optical: OpticalInput) -> float:
    incidence = math.radians(optical.incidence_angle_deg)
    sine_out = optical.refractive_index_in * math.sin(incidence) / optical.refractive_index_out
    if abs(sine_out) > 1.0:
        raise ValueError("configuration produces total internal reflection; transmission model is not applicable")
    return math.asin(sine_out)


def photon_momentum_magnitude(wavelength_m: float, refractive_index: float, convention: MomentumConvention) -> float:
    vacuum_momentum = H / wavelength_m
    if convention == "abraham":
        return vacuum_momentum / refractive_index
    if convention == "minkowski":
        return vacuum_momentum * refractive_index
    return vacuum_momentum


def optical_transfer(optical: OpticalInput) -> dict[str, Any]:
    incidence = math.radians(optical.incidence_angle_deg)
    refraction = refracted_angle_rad(optical)
    photon_energy = H * C / optical.wavelength_m
    photon_flux = optical.power_w / photon_energy if optical.power_w else 0.0
    photons_in_pulse = photon_flux * optical.pulse_duration_s

    incident_momentum = photon_momentum_magnitude(
        optical.wavelength_m, optical.refractive_index_in, optical.momentum_convention
    )
    transmitted_momentum = photon_momentum_magnitude(
        optical.wavelength_m, optical.refractive_index_out, optical.momentum_convention
    )
    p_in = _scale(_unit_direction(incidence), incident_momentum)
    p_out = _scale(_unit_direction(refraction), transmitted_momentum)
    delta_p = _subtract(p_in, p_out)

    extrinsic_per_photon = _cross(optical.interface_offset_m, delta_p)
    intrinsic_per_photon = (0.0, 0.0, (optical.topological_charge + optical.helicity) * HBAR)
    total_per_photon = tuple(
        optical.angular_momentum_coupling * (external + optical.absorption_fraction * intrinsic)
        for external, intrinsic in zip(extrinsic_per_photon, intrinsic_per_photon)
    )
    torque = _scale(total_per_photon, photon_flux)
    impulse = _scale(total_per_photon, photons_in_pulse)

    return {
        "incidence_angle_deg": optical.incidence_angle_deg,
        "refraction_angle_deg": math.degrees(refraction),
        "photon_energy_j": photon_energy,
        "photon_flux_s_inv": photon_flux,
        "photons_in_pulse": photons_in_pulse,
        "momentum_convention": optical.momentum_convention,
        "incident_momentum_kg_m_s": p_in,
        "transmitted_momentum_kg_m_s": p_out,
        "momentum_transfer_per_photon_kg_m_s": delta_p,
        "extrinsic_angular_momentum_per_photon_j_s": extrinsic_per_photon,
        "intrinsic_angular_momentum_per_photon_j_s": intrinsic_per_photon,
        "coupled_angular_momentum_per_photon_j_s": total_per_photon,
        "torque_vector_nm": torque,
        "angular_impulse_vector_j_s": impulse,
    }


def _fusion_reactivity_proxy(temperature_kev: float, reaction: str) -> float:
    # Smooth Gamow-like surrogate. It is intentionally dimensionless and normalized,
    # not a replacement for evaluated Bosch-Hale or experimental cross-section data.
    if reaction == "DT":
        scale, barrier, peak = 1.0, 19.94, 14.0
    else:
        scale, barrier, peak = 0.018, 31.4, 35.0
    t = max(temperature_kev, 1e-9)
    gamow = math.exp(-barrier / (t ** (1.0 / 3.0)))
    broad_peak = math.exp(-0.5 * (math.log(t / peak) / 1.1) ** 2)
    return scale * gamow * broad_peak


def _fusion_rate_proxy(plasma: PlasmaInput, angular_velocity_rad_s: float) -> float:
    volume = 4.0 * math.pi * plasma.effective_radius_m**3 / 3.0
    base = 0.25 * plasma.ion_density_m3**2 * volume * _fusion_reactivity_proxy(
        plasma.ion_temperature_kev, plasma.reaction
    )
    edge_speed = abs(angular_velocity_rad_s) * plasma.effective_radius_m
    subrelativistic_rotation = min(edge_speed / C, 0.05)
    rotation_factor = 1.0 + 4.0 * subrelativistic_rotation
    return base * rotation_factor * 1e-40


def run_simulation(
    optical: OpticalInput | None = None,
    plasma: PlasmaInput | None = None,
    *,
    time_step_s: float = 1e-9,
    limits: SimulationLimits | None = None,
) -> dict[str, Any]:
    optical = optical or OpticalInput()
    plasma = plasma or PlasmaInput()
    limits = limits or SimulationLimits()
    _validate(optical, plasma, limits)
    if time_step_s <= 0:
        raise ValueError("time_step_s must be positive")

    duration = min(optical.pulse_duration_s, plasma.confinement_time_s, limits.max_duration_s)
    steps = max(1, min(limits.max_steps, math.ceil(duration / time_step_s)))
    dt = duration / steps
    transfer = optical_transfer(optical)
    torque_vector = transfer["torque_vector_nm"]
    torque_magnitude = _norm(tuple(torque_vector))
    inertia = 0.4 * plasma.effective_mass_kg * plasma.effective_radius_m**2
    omega = plasma.initial_angular_velocity_rad_s
    states: list[StepState] = []
    cumulative_events = 0.0

    for step in range(steps + 1):
        time_s = step * dt
        rate = _fusion_rate_proxy(plasma, omega)
        if step > 0:
            cumulative_events += rate * dt
        states.append(
            StepState(
                step=step,
                time_s=time_s,
                angular_velocity_rad_s=omega,
                rotational_energy_j=0.5 * inertia * omega**2,
                torque_nm=torque_magnitude,
                fusion_rate_proxy_s_inv=rate,
                fusion_events_proxy=cumulative_events,
            )
        )
        if step == steps:
            break
        domega = (torque_magnitude / inertia - plasma.rotational_damping_s_inv * omega) * dt
        omega += domega

    payload = {
        "model": "qso-laser-refraction-angular-momentum-v1",
        "scope": "simulation-only; not an engineering design or validated fusion predictor",
        "optical_input": asdict(optical),
        "plasma_input": asdict(plasma),
        "limits": asdict(limits),
        "time_step_s": dt,
        "steps": steps,
        "moment_of_inertia_kg_m2": inertia,
        "optical_transfer": transfer,
        "states": [asdict(state) for state in states],
        "final": asdict(states[-1]),
        "uncertainties": [
            "Optical momentum in matter depends on the selected Abraham, Minkowski, or vacuum bookkeeping convention.",
            "The plasma is reduced to one rigid rotational degree of freedom with linear damping.",
            "The fusion-rate quantity is a normalized research proxy, not a cross-section calculation or yield forecast.",
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["report_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the bounded QSO laser-refraction angular-momentum fusion proxy simulator"
    )
    parser.add_argument("--output", type=Path, default=Path("artifacts/laser_refraction_fusion.json"))
    parser.add_argument("--power-w", type=float, default=OpticalInput.power_w)
    parser.add_argument("--wavelength-m", type=float, default=OpticalInput.wavelength_m)
    parser.add_argument("--incidence-deg", type=float, default=OpticalInput.incidence_angle_deg)
    parser.add_argument("--n-in", type=float, default=OpticalInput.refractive_index_in)
    parser.add_argument("--n-out", type=float, default=OpticalInput.refractive_index_out)
    parser.add_argument("--pulse-s", type=float, default=OpticalInput.pulse_duration_s)
    parser.add_argument("--topological-charge", type=int, default=OpticalInput.topological_charge)
    parser.add_argument("--helicity", type=int, choices=(-1, 0, 1), default=OpticalInput.helicity)
    parser.add_argument("--temperature-kev", type=float, default=PlasmaInput.ion_temperature_kev)
    parser.add_argument("--density-m3", type=float, default=PlasmaInput.ion_density_m3)
    parser.add_argument("--reaction", choices=("DT", "DD"), default=PlasmaInput.reaction)
    parser.add_argument("--momentum", choices=("abraham", "minkowski", "vacuum"), default="vacuum")
    args = parser.parse_args()

    optical = OpticalInput(
        wavelength_m=args.wavelength_m,
        power_w=args.power_w,
        pulse_duration_s=args.pulse_s,
        incidence_angle_deg=args.incidence_deg,
        refractive_index_in=args.n_in,
        refractive_index_out=args.n_out,
        topological_charge=args.topological_charge,
        helicity=args.helicity,
        momentum_convention=args.momentum,
    )
    plasma = PlasmaInput(
        ion_temperature_kev=args.temperature_kev,
        ion_density_m3=args.density_m3,
        reaction=args.reaction,
    )
    report = run_simulation(optical, plasma)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "report_sha256": report["report_sha256"],
                "final_angular_velocity_rad_s": report["final"]["angular_velocity_rad_s"],
                "fusion_events_proxy": report["final"]["fusion_events_proxy"],
            }
        )
    )


if __name__ == "__main__":
    main()
