"""Read-only event field capture for the authorized S40-T020 diagnostic repeat.

Called synchronously inside the existing flux callback; never advances Fluent.
SV_MASS_IMBALANCE is preserved as raw solver storage, not relabelled as a
scaled equation residual or an independently verified physical mass balance.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import numpy as np


class SpikeSchedule:
    """One speed-triggered event per 250 iterations, with N+1/N+5 samples."""
    def __init__(self):
        self.used_bins = set()
        self.followups = set()

    def reasons(self, iteration, speed):
        reasons = []
        if iteration in {0, 50, 2600, 2700, 2800} or iteration % 500 == 0:
            reasons.append('scheduled')
        if iteration in self.followups:
            reasons.append('event_followup')
            self.followups.remove(iteration)
        band = (iteration - 1) // 250
        if iteration > 0 and speed >= 500 and band not in self.used_bins:
            self.used_bins.add(band)
            self.followups.update(n for n in (iteration + 1, iteration + 5) if n <= 5000)
            reasons.append('speed_ge_500_m_s_first_in_250_iteration_band')
        return reasons


class Phase07bSpikeMonitor:
    VARIABLES = [('mixture', v) for v in ('SV_U', 'SV_V', 'SV_W', 'SV_P',
                 'SV_K', 'SV_D', 'SV_MASS_IMBALANCE')] + [
                 ('phase-2', 'SV_VOF'), ('phase-2', 'SV_MASS_IMBALANCE')]

    def __init__(self, solver, zones, directory, *, solve_n_phase=False):
        self.solver = solver
        self.solve_n_phase = solve_n_phase
        self.zones = list(zones)
        self.directory = Path(directory)
        self.directory.mkdir()
        self.schedule = SpikeSchedule()
        self.last_iteration = 0
        self.snapshots = []
        self.geometry = {}
        self.error = None
        self.file = (self.directory / 'spike-history.jsonl').open('x')

    def value(self, name):
        return float(self.solver.settings.setup.named_expressions[name].get_value())

    def fetch(self, domain, variable):
        data = self.solver.fields.solution_variable_data.get_data(
            variable_name=variable, zone_names=self.zones, domain_name=domain)
        arrays = {}
        for i, zone in enumerate(self.zones):
            array = np.asarray(data[zone])
            expected = len(self.geometry[f'z{i}_mixture_SV_VOLUME']) if self.geometry else None
            if expected is not None:
                assert array.size == expected * (3 if variable == 'SV_CENTROID' else 1)
            assert np.isfinite(array).all(), (domain, variable, zone)
            arrays[f'z{i}_{domain}_{variable}'] = array
        return arrays

    def prepare(self):
        for variable in ('SV_VOLUME', 'SV_CENTROID'):
            self.geometry.update(self.fetch('mixture', variable))
        phase_coordinates = self.fetch('phase-2', 'SV_CENTROID')
        for i in range(len(self.zones)):
            assert np.array_equal(self.geometry[f'z{i}_mixture_SV_CENTROID'],
                                  phase_coordinates[f'z{i}_phase-2_SV_CENTROID'])
        assert sum(len(self.geometry[f'z{i}_mixture_SV_VOLUME']) for i in range(len(self.zones))) == 620431
        np.savez_compressed(self.directory / 'geometry.npz', **self.geometry)
        self.snapshot(0, self.value('P7bMaximumSpeed'), ['scheduled_initial_proof'])
        self.persist()

    def snapshot(self, iteration, speed, reasons):
        start = time.monotonic()
        assert self.value('P7bGlobalIteration') == iteration
        fields = {}
        for domain, variable in self.VARIABLES:
            fields.update(self.fetch(domain, variable))
        if self.solve_n_phase:
            fields.update(self.fetch('phase-1', 'SV_VOF'))
        maxima = {'speed': [], 'k': [], 'epsilon': []}
        water = 0.0
        raw_water = 0.0
        phase_sum_ranges = []
        locations = []
        for i, zone in enumerate(self.zones):
            prefix = f'z{i}_mixture_'
            speeds = np.sqrt(sum(fields[prefix + 'SV_' + v] ** 2 for v in 'UVW'))
            k, epsilon = fields[prefix + 'SV_K'], fields[prefix + 'SV_D']
            alpha = fields[f'z{i}_phase-2_SV_VOF']
            raw_water += float(np.dot(alpha, self.geometry[prefix + 'SV_VOLUME']))
            if self.solve_n_phase:
                phase_sum = alpha + fields[f'z{i}_phase-1_SV_VOF']
                assert np.isfinite(phase_sum).all() and (phase_sum > 0).all(), 'Invalid raw N-phase sum'
                phase_sum_ranges.append({'zone': zone, 'minimum': float(phase_sum.min()),
                                         'maximum': float(phase_sum.max())})
                alpha = alpha / phase_sum
            water += float(np.dot(alpha, self.geometry[prefix + 'SV_VOLUME']))
            xyz = self.geometry[prefix + 'SV_CENTROID'].reshape(-1, 3)
            for label, array in [('speed', speeds), ('k', k), ('epsilon', epsilon)]:
                maxima[label].append(float(array.max()))
                indices = np.argsort(array)[-10:][::-1]
                locations.append({'zone': zone, 'ranked_by': label, 'top_cells': [
                    {'local_array_index': int(j), 'xyz_m': xyz[j].tolist(),
                     'speed_m_s': float(speeds[j]), 'k': float(k[j]),
                     'epsilon': float(epsilon[j]), 'alpha_l': float(alpha[j]),
                     'alpha_l_raw': float(fields[f'z{i}_phase-2_SV_VOF'][j]),
                     'pressure': float(fields[prefix + 'SV_P'][j]),
                     'mixture_mass_imbalance_raw': float(fields[prefix + 'SV_MASS_IMBALANCE'][j]),
                     'phase2_mass_imbalance_raw': float(fields[f'z{i}_phase-2_SV_MASS_IMBALANCE'][j])}
                    for j in indices]})
        native = {'speed': speed, 'k': self.value('P7bDiagnosticMaxK'),
                  'epsilon': self.value('P7bDiagnosticMaxEpsilon'),
                  'water': self.value('P7bWaterVolume')}
        for name in maxima:
            assert np.isclose(max(maxima[name]), native[name], rtol=1e-9, atol=1e-12), (name, maxima[name], native[name])
        assert np.isclose(water, native['water'], rtol=1e-9, atol=1e-12), ('inventory parity', water, native['water'])
        assert self.value('P7bGlobalIteration') == iteration, 'Solver advanced during snapshot'
        path = self.directory / f'fields-n{iteration:05d}.npz'
        assert not path.exists(), 'Refuse snapshot overwrite'
        np.savez_compressed(path, **fields)
        metadata = {'iteration': iteration, 'reasons': reasons, 'native': native,
                    'inventory_reconstruction': {'mode': 'cellwise_normalized_raw_phase_vector' if self.solve_n_phase else 'raw_secondary_fraction',
                        'raw_liquid_volume_m3': raw_water, 'comparison_liquid_volume_m3': water,
                        'native_difference_m3': water-native['water'], 'raw_phase_sum_ranges': phase_sum_ranges,
                        'basis': 'E6 idle N50 native ordinary/normalized/native-VOF report comparison; parity verified independently at every snapshot'},
                    'field_file': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'zones': self.zones, 'locations': locations,
                    'same_iteration_before_after': True, 'elapsed_s': time.monotonic() - start,
                    'claim_limit': 'SV_MASS_IMBALANCE stored raw; not a scaled equation residual. Array indices are snapshot-local, not global cell IDs.'}
        (self.directory / f'fields-n{iteration:05d}.json').write_text(json.dumps(metadata, indent=2))
        self.snapshots.append({'iteration': iteration, 'reasons': reasons, 'path': str(path),
                               'sha256': metadata['sha256'], 'elapsed_s': metadata['elapsed_s']})

    def capture(self, session, iteration, flux_row):
        try:
            assert iteration == self.last_iteration + 1
            assert self.value('P7bGlobalIteration') == iteration
            speed = self.value('P7bMaximumSpeed')
            assert np.isfinite(speed)
            reasons = self.schedule.reasons(iteration, speed)
            if reasons:
                self.snapshot(iteration, speed, reasons)
            self.file.write(json.dumps({'iteration': iteration, 'max_speed_m_s': speed,
                'captured_utc': datetime.now(timezone.utc).isoformat(), 'snapshot_reasons': reasons}) + '\n')
            self.file.flush()
            self.last_iteration = iteration
            if reasons:
                self.persist()
        except Exception as exc:
            self.error = {'iteration': iteration, 'type': type(exc).__name__, 'message': str(exc)}
            self.persist()
            raise

    def manifest(self):
        return {'last_iteration': self.last_iteration, 'snapshots': self.snapshots,
                'solve_n_phase': self.solve_n_phase,
                'error': self.error, 'directory': str(self.directory),
                'trigger': 'first max speed >=500 m/s in each 250-iteration band; followups +1/+5',
                'claim_limit': 'Speed-triggered sample, not exhaustive capture of every residual spike; periodic context plus raw global histories retained.'}

    def persist(self):
        (self.directory / 'manifest.json').write_text(json.dumps(self.manifest(), indent=2))

    def assert_complete(self, iteration):
        assert self.error is None and self.last_iteration == iteration, self.manifest()
        self.persist()

    def close(self):
        self.file.close()
        self.persist()
