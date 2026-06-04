# MIT License

# Copyright (c) 2026

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import io
import math
import struct
from datetime import datetime

import numpy as np
import pandas as pd
import scipy as sc
from baseclasses.chemical_energy import (
    CVProperties,
    EISPropertiesWithData,
    LSVProperties,
    VoltammetryCycleWithPlot,
)
from baseclasses.chemical_energy.chronoamperometry import CAProperties
from baseclasses.chemical_energy.chronopotentiometry import CPProperties
from baseclasses.chemical_energy.electrochemical_impedance_spectroscopy import EISCycle
from baseclasses.helper.utilities import convert_datetime
from nomad.units import ureg


def _try_convert_datetime(date_value):
    if isinstance(date_value, dict):
        try:
            return datetime(
                year=date_value.get('year'),
                month=date_value.get('month'),
                day=date_value.get('day'),
                hour=date_value.get('hour', 0),
                minute=date_value.get('minute', 0),
                second=date_value.get('second', 0),
            )
        except Exception:
            return None
    formats = ['%B %d, %Y   %H:%M:%S', '%b. %d, %Y   %H:%M:%S']
    for f in formats:
        try:
            return convert_datetime(date_value, f)
        except Exception:
            continue


def _get_clean_dict(d):

    def is_valid(value):
        if value is None:
            return False

        if isinstance(value, str):
            return value.strip() != ''

        if isinstance(value, (list, dict, tuple, set)):
            return len(value) > 0

        if isinstance(value, (pd.Series, np.ndarray)):
            return len(value) > 0 and not pd.isna(value).all()

        return not pd.isna(value)

    return {key: value for key, value in d.items() if is_valid(value)}


def _read_f32(data: bytes, offset: int) -> float:
    return struct.unpack_from('<f', data, offset)[0]


def _read_u32(data: bytes, offset: int) -> int:
    return struct.unpack_from('<I', data, offset)[0]


def _read_u16(data: bytes, offset: int) -> int:
    return struct.unpack_from('<H', data, offset)[0]


def _bin_params_ca(data: bytes) -> dict:
    return {
        'init_e_v': _read_f32(data, 0x0440),
        'high_e_v': _read_f32(data, 0x0444),
        'low_e_v': _read_f32(data, 0x0448),
        'init_scan_polarity': _read_f32(data, 0x0454),  # P=1, N=0?
        'step': _read_f32(data, 0x0458),
        'sample_interval_s': _read_f32(data, 0x045C),
        'sample_interval_dup': _read_f32(data, 0x0460),
        'sensitivity_av': _read_f32(data, 0x0464),
        'quiet_time_s': _read_f32(data, 0x0468),
        'pulse_width_s': _read_f32(data, 0x046C),
    }


def _bin_params_cp(data: bytes) -> dict:
    return {
        'high_e_limit_v': _read_f32(data, 0x0446),
        'low_e_limit_v': _read_f32(data, 0x044A),
        'init_scan_polarity': _read_f32(data, 0x045A),  # P=1, N=0?
        'data_interval_s': _read_f32(data, 0x045E),
        'data_interval_dup': _read_f32(data, 0x0462),
        'sensitivity_av': _read_f32(data, 0x0466),
        'cathodic_time_s': _read_f32(data, 0x046A),
        'cathodic_current_a': _read_f32(data, 0x04EA),
        'anodic_current_a': _read_f32(data, 0x04F2),
        'anodic_time_s': _read_f32(data, 0x0502),
    }


def _bin_params_cv(data: bytes) -> dict:
    return {
        'init_e_v': _read_f32(data, 0x043D),
        'final_e_v': _read_f32(data, 0x0441),
        'high_e_v': _read_f32(data, 0x0445),
        'low_e_v': _read_f32(data, 0x0449),
        'scan_rate_vs': _read_f32(data, 0x044D),
        'init_scan_polarity': _read_f32(data, 0x0455),  # P=1, N=0?
        'segment': _read_f32(data, 0x0459),
        'sample_interval_v': _read_f32(data, 0x045D),
        'sample_interval_dup': _read_f32(data, 0x0461),
        'sensitivity_av': _read_f32(data, 0x0465),
        'quiet_time_s': _read_f32(data, 0x0469),
        'comp_r_ohm': _read_f32(data, 0x04B5),
    }


def _bin_params_lsv(data: bytes) -> dict:
    return {
        'init_e_v': _read_f32(data, 0x0444),
        'final_e_v': _read_f32(data, 0x0448),
        'final_e_dup': _read_f32(data, 0x044C),
        'init_e_dup': _read_f32(data, 0x0450),
        'scan_rate_vs': _read_f32(data, 0x0454),
        'sample_interval_v': _read_f32(data, 0x0464),
        'sample_interval_dup': _read_f32(data, 0x0468),
        'sensitivity_av': _read_f32(data, 0x046C),
        'quiet_time_s': _read_f32(data, 0x0470),
        'comp_r_ohm': _read_f32(data, 0x04BC),
    }


def _bin_params_eis(data: bytes) -> dict:
    return {
        'init_e_v': _read_f32(data, 0x043A),
        'init_e_dup': _read_f32(data, 0x0442),
        'low_freq_hz': _read_f32(data, 0x0456),
        'sensitivity_av': _read_f32(data, 0x0462),
        'quiet_time_s': _read_f32(data, 0x0466),
        'amplitude_v': _read_f32(data, 0x047A),
        'high_freq_hz': _read_f32(data, 0x0492),
    }


def parse_metadata_chi_bin_file(filedata):
    # check magic bytes
    MAGIC = bytes([0x80, 0xF2, 0x1D, 0x00])
    if filedata[:4] != MAGIC:
        # invalid file
        return None, None

    def _read_technique_from_bin(data: bytes) -> tuple:
        """
        Reads technique abbreviations and technique names.

        Structure starting at offset 0x08:
          - If data[0x0a] is printable ASCII: 3-character code, length at 0x0b (IMP/EIS, LSV)
          - Otherwise: 2-character code, length at 0x0a (CA, CP, CV)
        In both cases, the length byte is followed by three null bytes, then the name.
        """
        b2 = data[0x0A]
        if 0x20 <= b2 < 0x7F:
            # 3-character code (e.g. IMP/EIS, LSV)
            code = data[0x08:0x0B].decode('ascii')
            name_len = data[0x0B]
            name = (
                data[0x0F : 0x0F + name_len]
                .decode('ascii', errors='replace')
                .rstrip('\x00')
            )
        else:
            # 2-character code (e.g. CV, CA, CP)
            code = data[0x08:0x0A].decode('ascii')
            name_len = data[0x0A]
            name = (
                data[0x0E : 0x0E + name_len]
                .decode('ascii', errors='replace')
                .rstrip('\x00')
            )
        return code, name

    def _read_timestamp_from_bin(data: bytes) -> dict:
        """
        Reads the timestamp.
        Format: uint16 sequence [0, year, 0, month, 0, day, 0, hour, 0, min, 0, sec]
        """
        for i in range(0x260, 0x2A0):  # byte-for-byte – CV liegt auf ungeradem Offset
            if i + 24 > len(data):
                break
            yr = _read_u16(data, i)
            if not (2000 <= yr <= 2100):
                continue
            vals = [_read_u16(data, i - 2 + j * 2) for j in range(12)]
            # Muster: gerade Indizes (Füllbytes) müssen 0 sein
            if all(vals[j] == 0 for j in range(0, 12, 2)):
                return {
                    'year': vals[1],
                    'month': vals[3],
                    'day': vals[5],
                    'hour': vals[7],
                    'minute': vals[9],
                    'second': vals[11],
                }
        return {}

    def _read_instrument_model(data: bytes) -> str:
        """
        Reads the internal instrument product code from the header.
        Pattern in 0x20–0x80: 4 null bytes, 1 byte length, 3 null bytes, ASCII string.
        Returns the stored code (e.g., ‘E1205’) and if known the CHI model name (e.g., ‘CHI760E’) as ‘instrument_model’.
        """
        # internal product code → CHI model name
        _MODEL_CODES = {
            'E1205': 'CHI760E',
            'E1208': 'CHI760E',
        }

        for i in range(0x20, 0x80):
            if i + 8 > len(data):
                break
            if data[i : i + 4] == b'\x00\x00\x00\x00':
                length = data[i + 4]
                if 0 < length <= 20 and data[i + 5 : i + 8] == b'\x00\x00\x00':
                    model_bytes = data[i + 8 : i + 8 + length]
                    if all(0x20 <= b < 0x7F for b in model_bytes):
                        internal_code = model_bytes.decode('ascii')
                        return _MODEL_CODES.get(internal_code, internal_code)
        return ''

    def _find_nrows_in_bin(data: bytes, row_size: int) -> int:
        """
        Find the number of data points by searching for the pattern
        [n, 0, n] (uint32 triplet) in the range 0x240–0x290.
        The correct solution is validated by the expected header size:
          header_size = len(data) - nrows * row_size  must be in the range [1000, 4000].
        """
        _HEADER_SIZE_MIN = 1000
        _HEADER_SIZE_MAX = 4000
        candidates = []
        for i in range(0x240, 0x290):
            if i + 12 > len(data):
                break
            v1 = _read_u32(data, i)
            v2 = _read_u32(data, i + 4)
            v3 = _read_u32(data, i + 8)
            if v1 > 0 and v2 == 0 and v1 == v3 and 10 < v1 < 500_000:
                header_size = len(data) - v1 * row_size
                if _HEADER_SIZE_MIN <= header_size <= _HEADER_SIZE_MAX:
                    candidates.append(v1)

        if not candidates:
            return None
        # If there are multiple matches, choose the smallest plausible one
        return min(candidates)

    instrument_model = _read_instrument_model(filedata)
    technique_code, technique_name = _read_technique_from_bin(filedata)
    metadata = {
        'datetime': _read_timestamp_from_bin(filedata),
        'method': technique_name,
        'station': instrument_model,
    }
    params = {
        'IMP': lambda: _bin_params_eis(filedata),
        'LSV': lambda: _bin_params_lsv(filedata),
        'CV': lambda: _bin_params_cv(filedata),
        'CA': lambda: _bin_params_ca(filedata),
        'CP': lambda: _bin_params_cp(filedata),
    }
    params_data = params[technique_code]()
    metadata.update(params_data)

    # row sizes in Bytes per technique
    _ROW_SIZES = {
        'IMP': 16,  # [freq_f32 × 2, Z'_f32, Z''_f32]
        'LSV': 4,  # current_f32
        'CV': 4,  # current_f32
        'CA': 4,  # current_f32
        'CP': 4,  # potential_f32
    }
    nrows = _find_nrows_in_bin(filedata, _ROW_SIZES[technique_code])
    return metadata, nrows


def get_data_from_eis_bin_file(filedata):
    # 16 byte rows: [freq_f32, freq_f32(dup), Z'_f32, Z''_f32]
    # Z-mod and phase are not stored and must be calculated
    metadata, nrows = parse_metadata_chi_bin_file(filedata)
    data_start = len(filedata) - nrows * 16
    freq, z_real, z_imag = [], [], []
    for i in range(nrows):
        base = data_start + i * 16
        freq.append(_read_f32(filedata, base + 0))  # bytes 0–3
        z_real.append(_read_f32(filedata, base + 8))  # bytes 8–11
        z_imag.append(_read_f32(filedata, base + 12))  # bytes 12–15

    z_mod = [math.sqrt(r**2 + im**2) for r, im in zip(z_real, z_imag)]
    z_phase = [math.degrees(math.atan2(im, r)) for r, im in zip(z_real, z_imag)]

    data = {
        'freq_hz': freq,
        'z_real_ohm': z_real,
        'z_imag_ohm': z_imag,
        'z_mod_ohm': z_mod,
        'phase_deg': z_phase,
    }
    metadata.update(data)
    return metadata


def get_data_from_ca_bin_file(filedata):
    # only current is stored; time calculated from data storage interval
    metadata, nrows = parse_metadata_chi_bin_file(filedata)
    data_start = len(filedata) - nrows * 4
    current = [_read_f32(filedata, data_start + i * 4) for i in range(nrows)]
    interval = metadata.get('sample_interval_s')
    time = interval * np.arange(1, nrows + 1)
    data = {
        'time_s': time,
        'current_a': current,
    }
    metadata.update(data)
    return metadata


def get_data_from_cp_bin_file(filedata):
    # only potential is stored; time calculated from data storage interval
    metadata, nrows = parse_metadata_chi_bin_file(filedata)
    data_start = len(filedata) - nrows * 4
    potential = [_read_f32(filedata, data_start + i * 4) for i in range(nrows)]
    interval = metadata['data_interval_s']
    time = interval * np.arange(1, nrows + 1)
    data = {
        'time_s': time,
        'potential_v': potential,
    }
    metadata.update(data)
    return metadata


def get_data_from_lsv_bin_file(filedata):
    # only current is stored; potential calculated from parameters
    metadata, nrows = parse_metadata_chi_bin_file(filedata)
    data_start = len(filedata) - nrows * 4
    current = [_read_f32(filedata, data_start + i * 4) for i in range(nrows)]
    init_e = metadata['init_e_v']
    interval = metadata['sample_interval_v']
    potential = init_e + np.arange(nrows) * interval
    data = {
        'potential_v': potential,
        'current_a': current,
    }
    metadata.update(data)
    return metadata


def get_data_from_cv_bin_file(filedata):
    # only current is stored; potential calculated from metadata
    metadata, nrows = parse_metadata_chi_bin_file(filedata)
    data_start = len(filedata) - nrows * 4
    current = [_read_f32(filedata, data_start + i * 4) for i in range(nrows)]
    potential = _reconstruct_cv_potential(
        metadata['init_e_v'],
        metadata['high_e_v'],
        metadata['low_e_v'],
        metadata['sample_interval_v'],
        nrows,
    )
    data = {
        'columns': ['potential_v', 'current_a'],
        'potential_v': potential,
        'current_a': current,
    }
    metadata.update(data)
    return metadata


def _reconstruct_cv_potential(
    init_e: float, high_e: float, low_e: float, interval: float, nrows: int
) -> list:
    """
    Reconstructs the potential sequence of a CV experiment using integer arithmetic
    (avoids floating-point accumulation errors during long scans).

    Structure:
      1. First half-scan: init_e → high_e  (n_up + 1 points)
      2. Complete cycles: high_e → low_e → high_e (n_down + n_down steps each)
    Stops as soon as nrows is reached.
    """
    # Derive the number of decimal places from the interval (e.g., 0.001 → 3 decimal places)
    ndec = max(0, -int(f'{interval:.2e}'.split('e')[1]))

    n_up = round((high_e - init_e) / interval)  # steps init → high
    n_half = round((high_e - low_e) / interval)  # steps high → low or in reverse

    potentials: list = []
    row = 0

    # First upward scan: init_e to high_e
    for step in range(n_up + 1):
        if row >= nrows:
            break
        potentials.append(round(init_e + step * interval, ndec))
        row += 1

    # Cycles: down → up
    while row < nrows:
        for step in range(1, n_half + 1):  # high_e → low_e
            if row >= nrows:
                break
            potentials.append(round(high_e - step * interval, ndec))
            row += 1
        for step in range(1, n_half + 1):  # low_e → high_e
            if row >= nrows:
                break
            potentials.append(round(low_e + step * interval, ndec))
            row += 1

    return potentials


def parse_chi_txt_file(filedata):
    lines = filedata.splitlines()

    metadata = {
        'datetime': lines[0].strip(),
        'method': lines[1].strip(),
        'instrument_model': lines[4].split(':', 1)[1].strip(),
    }

    for i, line in enumerate(lines):
        if '=' in line:
            key, value = line.split('=', 1)
            metadata[key.strip()] = value.strip()
        if 'Freq/Hz' in line or 'Potential/V' in line or 'Current/A' in line:
            break
    data = [lines[i]]
    data.extend(lines[i + 2 :])
    df = pd.read_csv(io.StringIO('\n'.join(data)), sep=None, engine='python')
    df.rename(columns=lambda x: x.strip(), inplace=True)
    return metadata, df


def get_data_from_eis_txt_file(filedata):
    metadata, data = parse_chi_txt_file(filedata)

    return {
        'station': metadata.get('instrument_model'),
        'datetime': metadata.get('datetime'),
        'method': metadata.get('method'),
        'freq_hz': data['Freq/Hz'],
        'phase_deg': data['Phase/deg'],
        'z_mod_ohm': data['Z/ohm'],
        'z_real_ohm': data["Z'/ohm"],
        'z_imag_ohm': data['Z"/ohm'],
        'init_e_v': metadata.get('Init E (V)'),
        'high_freq_hz': metadata.get('High Frequency (Hz)'),
        'low_freq_hz': metadata.get('Low Frequency (Hz)'),
        'amplitude_v': metadata.get('Amplitude (V)'),
        'quiet_time_s': metadata.get('Quiet Time (sec)'),
    }


def get_voltammetry_data_from_txt_file(filedata):
    metadata, data = parse_chi_txt_file(filedata)
    voltammetry_dict = {
        'station': metadata.get('instrument_model'),
        'datetime': metadata.get('datetime'),
        'method': metadata.get('method'),
        'current_a': data.get('Current/A'),
        'potential_v': data.get('Potential/V'),
        'charge_c': data.get('Charge/C'),
        'time_s': data.get('Time/sec'),
        'low_e_v': metadata.get('Low E (V)'),
        'high_e_v': metadata.get('High E (V)'),
        'init_e_v': metadata.get('Init E (V)'),
        'final_e_v': metadata.get('Final E (V)'),
        'sample_interval_v': metadata.get('Sample Interval (V)'),
        'sample_interval_s': metadata.get('Sample Interval (s)'),
        'pulse_width_s': metadata.get('Pulse Width (sec)'),
        'scan_rate_vs': metadata.get('Scan Rate (V/s)'),
        'data_interval_s': metadata.get('Data Storage Interval (s)'),
        'comp_r_ohm': metadata.get('Comp R (ohm)'),
        'cathodic_current_a': metadata.get('Cathodic Current (A)'),
        'anodic_current_a': metadata.get('Anodic Current (A)'),
        'cathodic_time_s': metadata.get('Cathodic Time (s)'),
        'anodic_time_s': metadata.get('Anodic Time (s)'),
        'high_e_limit_v': metadata.get('High E Limit (V)'),
        'low_e_limit_v': metadata.get('Low E Limit (V)'),
        'quiet_time_s': metadata.get('Quiet Time (sec)'),
    }
    if voltammetry_dict.get('time_s') is None:
        voltammetry_dict['time'] = np.linspace(
            0,
            (len(voltammetry_dict.get('potential_v', [])) - 1)
            * float(voltammetry_dict.get('sample_interval_v'))
            / float(voltammetry_dict.get('scan_rate_vs')),
            len(voltammetry_dict.get('potential_v', [])),
        )

    return _get_clean_dict(voltammetry_dict)


def _with_unit(value, unit):
    if value is None:
        return None
    if isinstance(value, (np.ndarray, pd.Series, list, tuple)):
        return np.asarray(value, dtype=float) * unit
    return float(value) * unit


def set_voltammetry_data(entry, data):
    entry.station = data.get('station')
    entry.time = _with_unit(data.get('time_s'), ureg('s'))
    entry.current = _with_unit(data.get('current_a'), ureg('A'))
    entry.voltage = _with_unit(data.get('potential_v'), ureg('V'))
    entry.charge = _with_unit(data.get('charge_c'), ureg('C'))
    entry.resistance = _with_unit(data.get('comp_r_ohm'), ureg('ohm'))


def set_chi_data_ca(entry, d):
    set_voltammetry_data(entry, d)
    entry.properties = CAProperties(
        sample_period=_with_unit(d.get('sample_interval_s'), ureg('s')),
        pre_step_potential=_with_unit(d.get('init_e_v'), ureg('V')),
        step_1_potential=_with_unit(d.get('high_e_v'), ureg('V')),
        step_2_potential=_with_unit(d.get('low_e_v'), ureg('V')),
        step_1_time=_with_unit(d.get('pulse_width_s'), ureg('s')),
        step_2_time=_with_unit(d.get('quiet_time_s'), ureg('s')),
    )
    if d['datetime']:
        entry.datetime = _try_convert_datetime(d['datetime'])


def set_chi_data_cp(entry, d):
    set_voltammetry_data(entry, d)
    entry.properties = CPProperties(
        step_1_current=_with_unit(d.get('cathodic_current_a'), ureg('A')),
        step_1_time=_with_unit(d.get('cathodic_time_s'), ureg('s')),
        step_2_current=_with_unit(d.get('anodic_current_a'), ureg('A')),
        step_2_time=_with_unit(d.get('anodic_time_s'), ureg('s')),
        lower_limit_potential=_with_unit(d.get('low_e_limit_v'), ureg('V')),
        upper_limit_potential=_with_unit(d.get('high_e_limit_v'), ureg('V')),
        sample_period=_with_unit(d.get('data_interval_s'), ureg('s')),
    )
    if d['datetime']:
        entry.datetime = _try_convert_datetime(d['datetime'])


def set_chi_data_lsv(entry, d):
    set_voltammetry_data(entry, d)
    entry.properties = LSVProperties(
        scan_rate=_with_unit(d.get('scan_rate_vs'), ureg('V/s')),
        step_size=_with_unit(d.get('sample_interval_v'), ureg('V')),
        initial_potential=_with_unit(d.get('init_e_v'), ureg('V')),
        final_potential=_with_unit(d.get('final_e_v'), ureg('V')),
    )
    if d['datetime']:
        entry.datetime = _try_convert_datetime(d['datetime'])


def set_chi_data_cv(entry, d):
    entry.station = d.get('station')
    if d['datetime']:
        entry.datetime = _try_convert_datetime(d['datetime'])
    diff = _with_unit(d.get('potential_v'), ureg('V')) - _with_unit(
        d.get('init_e_v'), ureg('V')
    )
    cycle_indices = (
        [0] + list(sc.signal.argrelextrema(np.abs(diff.magnitude), np.less)[0]) + [None]
    )
    cycles = []
    for i in range(len(cycle_indices) - 1):
        cycles.append(
            VoltammetryCycleWithPlot(
                name=f'Cycle {i}',
                current=_with_unit(
                    d.get('current_a')[cycle_indices[i] : cycle_indices[i + 1]],
                    ureg('A'),
                ),
                voltage=_with_unit(
                    d.get('potential_v')[cycle_indices[i] : cycle_indices[i + 1]],
                    ureg('V'),
                ),
            )
        )

    entry.cycles = cycles
    entry.properties = CVProperties(
        initial_potential=_with_unit(d.get('init_e_v'), ureg('V')),
        limit_potential_1=_with_unit(d.get('high_e_v'), ureg('V')),
        limit_potential_2=_with_unit(d.get('low_e_v'), ureg('V')),
        scan_rate=_with_unit(d.get('scan_rate_vs'), ureg('V/s')),
    )


def set_chi_data_eis(entry, d):
    entry.station = d.get('station')
    entry.measurements = [
        EISPropertiesWithData(
            data=EISCycle(
                frequency=_with_unit(d.get('freq_hz'), ureg('Hz')),
                z_real=_with_unit(d.get('z_real_ohm'), ureg('ohm')),
                z_imaginary=_with_unit(d.get('z_imag_ohm'), ureg('ohm')),
                z_modulus=_with_unit(d.get('z_mod_ohm'), ureg('ohm')),
                z_angle=_with_unit(d.get('phase_deg'), ureg('deg')),
            ),
            dc_voltage=_with_unit(d.get('init_e_v'), ureg('V')),
            initial_frequency=_with_unit(d.get('low_freq_hz'), ureg('Hz')),
            final_frequency=_with_unit(d.get('high_freq_hz'), ureg('Hz')),
            ac_voltage=_with_unit(d.get('amplitude_v'), ureg('V')),
        )
    ]
    if d['datetime']:
        entry.datetime = _try_convert_datetime(d['datetime'])
