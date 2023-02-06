# -*- coding: utf-8 -*-
'''
Head-Tail Utilities

Copyright (c) CERN 2016

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Authors:
    Tom Levens <tom.levens@cern.ch>
    Kacper Lasocha <kacper.lasocha@cern.ch>
'''

import configparser
import glob
import h5py
import logging
import numpy as np
import platform
import os
import socket

from functools import wraps
from scipy import stats
from scipy.interpolate import interp1d

__version__ = '2017-08-09'


class BQHT(object):
    def __init__(self, cfg_file=None, system=None, user=None, archive=False):
        '''Class to process Head-Tail data files

        Args:
            cfg_file:   path to configuration file
            system:     system (defaults to first one in configuration file)
            user        user (defaults to ALL)
        '''
        # Read configuration file
        if cfg_file is None:
            cfg_file = os.path.join(os.path.dirname(__file__), os.pardir, 'config', 'bqht.cfg')
        self._cp = configparser.ConfigParser()
        self._cp.read_file(open(cfg_file))

        overrides = [
            platform.system().lower(),
            socket.gethostname().split('.')[0].lower()
        ]

        for o in overrides:
            self._cp.read('{0[0]}.{1}{0[1]}'.format(os.path.splitext(cfg_file), o))

        self.cfg_file = cfg_file

        self._log = logging.getLogger(__name__)

        self.systems = self._cp.sections()

        self.archive = archive

        self._user = 'ALL'
        self.system = self.systems[0] if system is None else system

        if user is not None:
            self.user = user

    def __repr__(self):
        return '<BQHT: system={0}>'.format(self.system, self.user)

    def open_file(self, path):
        '''Open a HDF5 file

        Args:
            path:   HDF5 file to open

        Returns:
            A BQHTFile instance for the file
        '''
        htf = BQHTFile(path)

        for attr in ('offset', 'max_offset', 'harmonic', 'frev'):
            setattr(htf, attr, getattr(self, attr))

        if self.invert_sigma:
            for p in htf.planes:
                dataset = htf.data[p]['sigma']
                if dataset is not None:
                    dataset.invert = True

        return htf

    def file(self, name):
        '''Get a file path by (partial) name'''
        files = list(filter(lambda x: name in x, self.files))
        if files:
            return files[0]
        else:
            raise ValueError('could not find file "{0}"'.format(name))

    @property
    def system(self):
        return self._system

    @system.setter
    def system(self, val):
        if val not in self.systems:
            raise ValueError('{0} is not a valid system'.format(val))

        self.cfg = self._cp[val]
        self._system = val

        self.title = self.cfg.get('title', '')
        self.device = self.cfg.get('device', '')
        self.acc = self.cfg.get('acc', '')
        self.dir = self.cfg.get('dir', '') if not self.archive else self.cfg.get('archive', '')
        self.offset = float(self.cfg.get('offset', 0.0))
        self.max_offset = float(self.cfg.get('maxoffset', 25e-9))
        self.frev = float(self.cfg.get('frev', 0.0))
        self.harmonic = int(self.cfg.get('harmonic', 0))
        self.color = self.cfg.get('color', '#000')
        self.thresh = float(self.cfg.get('thresh', 0))
        self.limit = float(self.cfg.get('limit', 0))
        self.cable_comp = bool(self.cfg.get('cable_comp', 'False').lower() == 'true')
        self.invert_sigma = bool(self.cfg.get('inv_sigma', 'True').lower() == 'true')

        if 'users' in self.cfg.keys():
            self.users = ['ALL'] + list(map(lambda x: x.strip(), self.cfg['users'].split(',')))
        else:
            self.users = ['ALL']

        if self.user not in self.users:
            self.user = 'ALL'

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, val):
        if val in self.users:
            self._user = val
        else:
            raise ValueError('{0} is not a valid user'.format(val))

    @property
    def files(self):
        if not os.path.isdir(self.dir):
            return []
        else:
            # Format the filename
            user = '' if self.user == 'ALL' else '_{0}'.format(self.user)
            filename = '{0}{1}_*.h5'.format(self.device, user)

            # Glob a list of the files
            files = glob.glob(os.path.join(self.dir, '*', filename))

            # Return a sorted list of the files. This assumes the filename has
            # the format "SYSTEM_YYYYMMDD_HHMMSS.h5" so that the slice [-18:-3]
            # selects just the YYYYMMDD_HHMMSS part. This is ugly but is
            # significantly faster than doing it in a cleaner way.
            return sorted(files, key=lambda x: x[-18:-3])


class BQHTGroup(object):
    '''A group of Head-Tail datasets

    Args:
        init:    A dictionary to initialise this object's __dict__
        aliases: A dictionary of aliases
    '''
    def __init__(self, init={}, aliases={}):
        self.__dict__ = init
        self._aliases = aliases

    def __repr__(self):
        return '<BQHTGroup: [{0}]>'.format(
            ', '.join([x for x in self.__dict__.keys() if not x.startswith('_')]),
        )

    def __getitem__(self, key):
        if key in self._aliases.keys():
            key = self._aliases[key]
        return getattr(self, key)

    def __setitem__(self, key, val):
        if key in self._aliases.keys():
            key = self._aliases[key]
        return setattr(self, key, val)


class BQHTFile(object):
    def __init__(self, path):
        '''A Head-Tail file

        Args:
            path:   path of HDF5 file
        '''
        self._log = logging.getLogger(__name__)

        self.h5file = h5py.File(path, 'r')

        self.planes = ('horizontal', 'vertical')
        self.signals = ('delta', 'sigma')
        self.planes_signals = [(p, s) for p in self.planes for s in self.signals]

        # Initialise the groups
        aliases = {'sum': 'sigma'}
        self.data = BQHTGroup({p: BQHTGroup({s: None for s in self.signals}, aliases) for p in self.planes})

        # Make shortcuts of self.<plane> -> self.data.<plane>
        for p in self.planes:
            setattr(self, p, self.data[p])

        self.filename = path
        self.filesize = os.path.getsize(path)
        self.bunches = []
        self.bunch_stability = {}
        self.instability_mode = {}
        self.turn_adjust = None
        self.align = False

        # Create dataset for each plane/signal
        for i, (p, s) in enumerate(self.planes_signals):
            for k, v in [(s, s)] + list(aliases.items()):
                if v == s:
                    data_name = '{0}/{1}'.format(p, k)
                    dataset = self.h5file.get(data_name)
                    if dataset is not None:
                        break
            else:
                self.data[p][s] = None
                continue

            self.data[p][s] = BQHTDataset(dataset)
            self.data[p][s].remove_baseline = True if s == 'delta' else False
            self.data[p][s].plane = p
            self.data[p][s].signal = s

        self.acq_stamp = self.h5file.attrs.get('acq_stamp', 0)
        self.cycle_stamp = self.h5file.attrs.get('cycle_stamp', 0)
        self.cycle_name = self.h5file.attrs.get('cycle_name', b'').decode('ASCII')
        self.device = self.h5file.attrs.get('device', b'').decode('ASCII')
        self.version = self.h5file.attrs.get('version', 0)

        self.closed = False

    def __repr__(self):
        return '<BQHTFile: {0}>'.format(self.filename)

    def __getitem__(self, key):
        return self.data[key]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        '''Close the file'''
        if not self.closed:
            self.h5file.close()
            self.data = {p: {s: None for s in self.signals} for p in self.planes}
            self.closed = True

    def _check_closed(func):
        '''Decorator to check if the file has already been closed'''
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.closed:
                raise ValueError('cannot operate on a closed file')
            return func(self, *args, **kwargs)
        return wrapper

    # The following properties automatically set the equivalent property in each
    # child dataset
    offset = property(lambda s: s._offset, lambda s, v: s._set_data_attr('offset', v))
    max_offset = property(lambda s: s._max_offset, lambda s, v: s._set_data_attr('max_offset', v))
    harmonic = property(lambda s: s._harmonic, lambda s, v: s._set_data_attr('harmonic', v))
    frev = property(lambda s: s._frev, lambda s, v: s._set_data_attr('frev', v))
    turn_adjust = property(lambda s: s._turn_adjust, lambda s, v: s._set_data_attr('turn_adjust', v))
    populated_turns = property(lambda s: s._populated_turns, lambda s, v: s._set_data_attr('populated_turns', v))
    align = property(lambda s: s._align, lambda s, v: s._set_data_attr('align', v))

    def _set_data_attr(self, name, value):
        '''Sets an attribute in all datasets'''
        for p, s in self.planes_signals:
            if self.data[p][s] is not None:
                setattr(self.data[p][s], name, value)
        setattr(self, '_' + name, value)

    @_check_closed
    def locate_bunches(self, plane='horizontal', signal='sigma', threshold=5, parts=5):
        '''Locate bunches in data

        Splits each bunch into nb_parts and calculates the amplitude of each
        part. If the part with the maximum amplitude is greater than threshold
        multipled by the part with the lowest amplitude, consider this bunch
        to be present.

        Args:
            plane:      plane to use for detection
            signal:     signal to use for detection
            threshold:  threshold for detection
            parts:      number of parts for each bunch
        '''
        dataset = self.data[plane][signal]

        max_turn = dataset.number_of_turns - 1
        max_bunch = dataset.number_of_bunches - 1

        # Check for bunches in first turn
        self.bunches = self._locate_bunches(0, 0, max_bunch, dataset, threshold, parts)
        turn_range = range(0, dataset.number_of_turns)
        reverse = False

        # If no bunches in first turn, check last turn
        if not self.bunches:
            self.bunches = self._locate_bunches(max_turn, 0, max_bunch, dataset, threshold, parts)
            turn_range = reversed(turn_range)
            reverse = True

        # Check first bunch of each turn
        if self.bunches:
            bunch = self.bunches[0]
            populated_turns = []

            for turn in turn_range:
                # Compare also slots on each side of the bunch to account for
                # slippage due to incorrect frev value (search +10 slots as frev
                # is quite far off for ions)
                first_bunch = bunch - 1
                last_bunch = bunch + 10

                # Handle case where we have full turns, in this case if we reach
                # the first or last bunch, wrap around at the harmonic
                if dataset.number_of_bunches == dataset.harmonic:
                    if first_bunch < 0:
                        first_bunch = dataset.harmonic + first_bunch
                        bunches = []
                        if turn > 0:
                            bunches.extend(self._locate_bunches(turn - 1, first_bunch, dataset.harmonic - 1,
                                                                dataset, threshold, parts))
                        bunches.extend(self._locate_bunches(turn, 0, last_bunch, dataset, threshold, parts))
                    elif last_bunch >= dataset.harmonic:
                        last_bunch = last_bunch - dataset.harmonic
                        bunches = self._locate_bunches(turn, first_bunch, dataset.harmonic - 1,
                                                       dataset, threshold, parts)
                        if turn < dataset.number_of_turns - 1:
                            bunches.extend(self._locate_bunches(turn + 1, 0, last_bunch, dataset, threshold, parts))
                    else:
                        bunches = self._locate_bunches(turn, first_bunch, last_bunch, dataset, threshold, parts)

                # Handle the case where we do not have full turns, in this case
                # limit to the min/max.
                else:
                    if first_bunch < 0:
                        first_bunch = 0
                    elif last_bunch >= dataset.number_of_bunches:
                        last_bunch = dataset.number_of_bunches - 1

                    bunches = self._locate_bunches(turn, first_bunch, last_bunch, dataset, threshold, parts)

                # We found bunches in this turn, for the next turn use the first
                # found bunch to follow the slippage
                if bunches:
                    populated_turns.append(turn)
                    bunch = bunches[0]

            # Correct the bunch numbers for the slippage
            if reverse:
                diff = self.bunches[0] - bunch
                self.bunches = list(map(lambda x: x - diff, self.bunches))

            # Sort the list
            self.populated_turns = range(min(populated_turns), max(populated_turns) + 1)
        else:
            self.populated_turns = []

    @_check_closed
    def _locate_bunches(self, turn, first_bunch, last_bunch, dataset, threshold, parts):
        '''Locate bunches for a specific turn within a specific bunch range'''
        bunches = []

        # Extract data for whole range as this is faster than extracting it
        # bunch by bunch. We need to get the data without padding, otherwise
        # some parts may contain all/mostly zeros which breaks the amplitude
        # calculation.
        _, turn_data = dataset.get(turn, first_bunch, last_bunch, baseline=False, pad=False, align=False)

        for bunch in range(0, last_bunch - first_bunch + 1):
            # Slice bunch data
            bunch_start = int(bunch * dataset.samples_per_bunch)
            bunch_end = int(bunch_start + dataset.samples_per_bunch)
            bunch_data = turn_data[bunch_start:bunch_end]
            bunch_len = int(bunch_data.size - (bunch_data.size % parts))

            # Reshape into parts
            part_data = bunch_data[0:bunch_len].reshape(parts, bunch_len // parts)

            if part_data.size == 0:
                continue

            # Calculate amplitude of each part
            part_amp = np.max(part_data, axis=1) - np.min(part_data, axis=1)

            # Check if any part amplitude is above threshold
            if max(part_amp) > threshold * min(part_amp):
                bunches.append(first_bunch + bunch)

        return bunches

    @_check_closed
    def optimise_overlap(self, plane='horizontal', signal='sigma', **kwargs):
        '''Opitimizes overlap values for single/multi-segment cases

        Args:
            plane:      plane to use for detection
            signal:     signal to use for detection
        '''
        dataset = self.data[plane][signal]

        if len(self.bunches) == 0:
            self.turn_adjust = None
        elif dataset.segments == 1:
            self.frev, self.turn_adjust = self._optimise_overlap_single_segment(dataset, **kwargs)
        elif dataset.turn_adjust is None:
            self.frev, self.turn_adjust = self._optimise_overlap_multi_segment(dataset, **kwargs)

    @_check_closed
    def _calculate_fitness(self, bunch0, bunch1_interp, distance, best_fit, points):
        '''Calculate fitness'''
        square_diffs = 0.0
        for p in points:
            square_diffs = square_diffs + (bunch0[p] - bunch1_interp(p + distance))**2
            if square_diffs > best_fit:
                break
        return square_diffs

    @_check_closed
    def _generate_points(self, data, rand):
        '''Generate points for fitting'''
        if rand:
            values = range(0, len(data))
            data_sq = data**2
            density = data_sq / np.sum(data_sq)
            r_var = stats.rv_discrete(name='r_var', values=(values, density))
            points = sorted(list(set(r_var.rvs(size=60))))
        else:
            points = list(range(0, len(data), 3))

        self._log.info('Using points: {0}'.format(', '.join(map(str, points))))

        return points

    @_check_closed
    def _optimise_overlap_single_segment(self, dataset, rand=True, magnitude=10, iterations=5):
        '''Optimise overlap for a single segment

        Args:
            dataset:        dataset on which to operate
            rand:           use random samples in the bunch
            magnitude:      initial magnitude
            iterations:     number of iterations
        '''
        self._log.info('Using single segment optimiser')

        nb_turns = len(dataset.populated_turns)

        if nb_turns < 2:
            return (self.frev, None)
        else:
            first_bunch = self.bunches[0]
            repeat_approx = dataset.t_to_samples(dataset.frev)
            bunch_inc = dataset.samples_per_bunch
            offset = (dataset.populated_turns[0] * dataset.samples_per_turn +
                      dataset.t_to_samples(dataset.offset) +
                      dataset.t_to_samples(dataset.deskew) +
                      dataset.trigger_offset)

            # Extract samples for first bunch
            first_bunch_start = int(offset + first_bunch * bunch_inc)
            first_bunch_end = int(first_bunch_start + bunch_inc)

            first_bunch_data = np.array(
                dataset.convert_data(dataset._dataset[first_bunch_start:first_bunch_end])
            )

            # Calculate sample points
            points = self._generate_points(first_bunch_data, rand)

            mag = magnitude

            # Perform fitting
            # Precision up to 0.001 at default
            for j in range(1, iterations + 1):
                fitness = []
                distance = 0
                best_fit = float('inf')

                # Turn for comparison
                comp_turn = int(min(10**(j - 1) + 1, nb_turns) - 1)

                # Bunch position for comparison
                comp_bunch_start = int(repeat_approx * comp_turn - 10 * mag * comp_turn)
                comp_bunch_end = int(comp_bunch_start + bunch_inc + 20 * mag * comp_turn + 1)

                # Extract comparison bunch data
                comp_bunch_data = np.array(dataset.convert_data(
                    dataset._dataset[first_bunch_start + comp_bunch_start:first_bunch_start + comp_bunch_end]
                ))

                # Samples for interpolation
                comp_bunch_samp = np.arange(comp_bunch_start, comp_bunch_end)
                comp_bunch_interp = interp1d(comp_bunch_samp, comp_bunch_data, assume_sorted=True,
                                             bounds_error=False)

                # Fitting
                for i in range(-10, 11):
                    repeat = repeat_approx + (i * mag)
                    new_distance = comp_turn * repeat
                    if new_distance != distance:
                        distance = new_distance
                        fit = self._calculate_fitness(first_bunch_data, comp_bunch_interp, distance,
                                                      best_fit, points)
                        fitness.append(fit)
                        best_fit = min(fit, best_fit)
                    else:
                        fitness.append(fitness[-1])

                best_index = fitness.index(min(fitness))
                repeat_approx += (best_index - 10) * mag
                mag /= 10

            return (repeat_approx * dataset.period, None)

    @_check_closed
    def _optimise_overlap_multi_segment(self, dataset, rand=True, magnitude=1, iterations=1, limit=None):
        '''Optimise overlap for a multiple segments

        Args:
            dataset:        dataset on which to operate
            rand:           use random samples in the bunch
            magnitude:      initial magnitude
            iterations:     number of iterations
            limit:          limit to N segments (for testing)
        '''
        self._log.info('Using multi segment optimiser ({0} segments)'.format(dataset.segments))

        first_bunch = self.bunches[0]
        samples_per_segment = dataset.samples_per_turn
        bunch_inc = dataset.samples_per_bunch
        offset = (dataset.populated_turns[0] * dataset.samples_per_turn +
                  dataset.t_to_samples(dataset.offset) +
                  dataset.t_to_samples(dataset.deskew) +
                  dataset.trigger_offset)

        if limit is None:
            limit = dataset.segments

        # Extract samples for first bunch
        first_bunch_start = int(offset + first_bunch * bunch_inc)
        first_bunch_end = int(first_bunch_start + bunch_inc)

        first_bunch_data = np.array(
            dataset.convert_data(dataset._dataset[first_bunch_start:first_bunch_end])
        )

        offset_array = [0 for _ in range(0, dataset.populated_turns[0] + 1)]

        # Calculate sample points
        points = self._generate_points(first_bunch_data, rand)

        for segment in range(1, len(dataset.populated_turns)):
            if segment < limit:
                segment_start = int(samples_per_segment * segment)
                distance_approx = segment_start
                mag = magnitude
                for j in range(1, iterations + 1):
                    best_fit = float('inf')
                    fitness = []

                    # Bunch position for comparison
                    comp_bunch_start = int(segment_start - 10 * mag)
                    comp_bunch_end = int(comp_bunch_start + bunch_inc + 20 * mag + 1)

                    # Extract comparison bunch data
                    comp_bunch_data = np.array(dataset.convert_data(
                        dataset._dataset[first_bunch_start + comp_bunch_start:first_bunch_start + comp_bunch_end]
                    ))

                    # Samples for interpolation
                    if mag >= 1:
                        comp_bunch_interp = lambda x: comp_bunch_data[x - segment_start + (10 * mag)]
                    else:
                        comp_bunch_samp = np.arange(comp_bunch_start, comp_bunch_end)
                        comp_bunch_interp = interp1d(comp_bunch_samp, comp_bunch_data, assume_sorted=True,
                                                     bounds_error=False)

                    for i in range(-10, 11):
                        distance = distance_approx + (i * mag)
                        fit = self._calculate_fitness(first_bunch_data, comp_bunch_interp, distance,
                                                      best_fit, points)
                        fitness.append(fit)
                        best_fit = min(fit, best_fit)

                    best_index = fitness.index(min(fitness))
                    distance_approx += (best_index - 10) * mag
                    mag /= 10

                offset_array.append(distance_approx - segment_start)
            else:
                offset_array.append(0)

        offset_array.extend([0 for _ in range(dataset.populated_turns[-1], dataset.segments - 1)])

        return (self.frev, offset_array)

    @_check_closed
    def calculate_bunch_stability(self):
        '''Calculate bunch stability, algorithm V2

        Populates self.bunch_stability with the mean amplitude squared
        outside and inside the bunch area.
        '''
        self._log.info('Finding unstable bunches')

        if len(self.bunches) == 0:
            raise ValueError('no bunches, cannot calculate stability')

        for plane in self.planes:
            self.bunch_stability[plane] = {}

            delta_dataset = self.data[plane]['delta']
            sigma_dataset = self.data[plane]['sigma']

            nb_turns = sigma_dataset.number_of_turns

            _, sigma_data_t0_b0 = sigma_dataset[0, self.bunches[0]]

            inside_pts = np.where(sigma_data_t0_b0**2 >= 0.01 * max(sigma_data_t0_b0**2))[0]
            outside_pts = np.array(list(set(range(int(sigma_dataset.samples_per_bunch))) - set(inside_pts)))

            for bunch in self.bunches:
                mean_inside = 0
                mean_outside = 0

                for turn in range(nb_turns):
                    bunch_data = delta_dataset[turn, bunch][1]
                    mean_inside += np.mean(bunch_data[inside_pts]**2) / nb_turns
                    mean_outside += np.mean(bunch_data[outside_pts]**2) / nb_turns

                self.bunch_stability[plane][bunch] = (mean_outside, mean_inside)

    @_check_closed
    def calculate_mode(self, threshold=2.35):
        '''Calculate mode in instable bunches

        Looks for the local minima.
        '''
        self._log.info("Calculating instabilities' modes")

        if len(self.bunches) == 0:
            raise ValueError('no bunches, cannot calculate stability')

        for plane in self.planes:
            self.instability_mode[plane] = {}

            delta_dataset = self.data[plane]['delta']
            sigma_dataset = self.data[plane]['sigma']

            nb_turns = sigma_dataset.number_of_turns

            _, sigma_data_t0_b0 = sigma_dataset[0, self.bunches[0]]

            mode_points = np.where(sigma_data_t0_b0**2 >= 0.1 * max(sigma_data_t0_b0**2))[0]

            for bunch in self.bunches:
                if self.bunch_stability[plane][bunch][1]/self.bunch_stability[plane][bunch][0] >= threshold:
                    mode_amplitudes = np.zeros(len(mode_points))

                    for turn in range(nb_turns):
                        bunch_data = delta_dataset[turn, bunch][1]
                        for i, point in enumerate(mode_points):
                            mode_amplitudes[i] += bunch_data[point]**2

                    max_amplitude = np.max(mode_amplitudes)

                    local_mins = 0
                    local_mins_high_mode = -1
                    for i in range(len(mode_amplitudes)-4):
                        if mode_amplitudes[i+1] > mode_amplitudes[i+2] and mode_amplitudes[i+2] < mode_amplitudes[i+3]:
                            local_mins_high_mode += 1
                            if mode_amplitudes[i] > mode_amplitudes[i+2] and mode_amplitudes[i+2] < mode_amplitudes[i+4]:
                                if max_amplitude > 2.5*mode_amplitudes[i+2] and mode_points[i+4] - mode_points[i] < 6:
                                    local_mins += 1

                    if local_mins_high_mode > 5:
                        local_mins = local_mins_high_mode

                    self.instability_mode[plane][bunch] = local_mins / 2


class BQHTDataset(object):
    def __init__(self, dataset):
        '''A Head-Tail dataset

        Args:
            dataset:    HDF5 dataset
        '''
        self._dataset = dataset
        self.size = dataset.size
        self.shape = dataset.shape
        self.segments = int(dataset.attrs.get('segment_count', 1))
        self.data_resolution = float(dataset.attrs.get('ampl_resolution', 1.0))
        self.data_offset = float(dataset.attrs.get('data_offset', 0.0))
        self.period = float(dataset.attrs.get('sampling_period', 1.0e-10))
        self.trigger_delay = float(dataset.attrs.get('trigger_delay', 0.0))
        self.deskew = (float(dataset.attrs.get('deskew', 0)) + float(dataset.attrs.get('delay', 0))) * self.period
        self.mean = None
        self.remove_baseline = False
        self.offset = 0
        self.harmonic = 0
        self.max_offset = 0
        self._frev = 0
        self.turn_adjust = dataset.attrs.get('trigger_offset', None)
        self.remove_jitter = True
        self.invert = False
        self.cable_comp = False
        self.populated_turns = []
        self.plane = None
        self.signal = None
        self.align = False

        # Turn adjust as implemented by Acquiris
        if self.turn_adjust is not None:
            turn_adjust_0 = self.turn_adjust[0]
            self.turn_adjust = -(self.turn_adjust - turn_adjust_0) / self.period

    def __repr__(self):
        return '<BQHTDataset: {0}.{1}>'.format(self.plane, self.signal)

    def get(self, turn, first_bunch, last_bunch, **kwargs):
        '''Get bunch data

        Args:
            turn (int):         turn number
            first_bunch (int):  first bunch number
            last_bunch (int):   last bunch number

        Optional args:
            skip (int):         skip N samples at beginning of data
            extra (int):        return M extra samples at end of data
            baseline (bool):    perform baseline removal
            pad (bool):         pad data
            invert (bool):      invert the signal
            align (bool):       align the signal to the same samples
        '''
        skip = kwargs.get('skip', self.t_to_samples(self.offset))
        extra = kwargs.get('extra', 0)
        baseline = kwargs.get('baseline', self.remove_baseline)
        pad = kwargs.get('pad', True)
        invert = kwargs.get('invert', self.invert)
        align = kwargs.get('align', self.align)

        bunch_inc = self.samples_per_bunch
        deskew = self.t_to_samples(self.deskew)

        x_offset = skip + int(bunch_inc * first_bunch) + 1
        x_length = int(bunch_inc * (last_bunch - first_bunch + 1)) + extra

        xaxis = np.arange((x_offset - 1), (x_offset + x_length), dtype=np.float32)

        if self.remove_jitter and self.turn_adjust is not None and turn < len(self.turn_adjust):
            turn_adjust = self.turn_adjust[turn]
        else:
            turn_adjust = 0

        turn_inc = turn * self.samples_per_turn + turn_adjust
        turn_cor = turn_inc % 1

        bunch_sta = int(turn_inc) + x_offset + deskew + self.trigger_offset
        bunch_end = bunch_sta + x_length

        if align:
            y = self.convert_data(self._dataset[bunch_sta:bunch_end+1])

            x_interp = np.arange((x_offset - turn_cor), (x_offset + x_length - turn_cor + 1), dtype=np.float32)
            x_interp = x_interp[0:y.size]
            x = xaxis[1:]

            if y.size > 1:
                y_interp = interp1d(x_interp, y, assume_sorted=True, bounds_error=False)
                y = y_interp(x[0:y.size-1])
        else:
            x = xaxis[1:] - turn_cor
            y = self.convert_data(self._dataset[bunch_sta:bunch_end])

        if pad and y.size < x.size:
            y = np.pad(y, (0, x.size - y.size), 'constant')

        if baseline and turn in self.populated_turns:
            if self.mean is None:
                self.calc_mean()

            if not align and turn > 0:
                y_interp = interp1d(xaxis, self.mean[(x_offset - 1):(x_offset + x_length)], assume_sorted=True,
                                    bounds_error=False)
                x_interp = np.arange((x_offset - turn_cor), (x_offset + x_length - turn_cor), dtype=np.float32)

                y = y - y_interp(x_interp)
            else:
                y = y - self.mean[x_offset:(x_offset + x_length)]

        if invert:
            y = -y

        return (x * self.period, y)

    def convert_data(self, data):
        '''Returns data converted from raw samples to volts'''
        return (np.float32(data) - self.data_offset) * self.data_resolution

    def __getitem__(self, slicer):
        '''Get bunch data with slicing interface.

        Slicing:
            [t]         Returns data for turn=t, bunch=0..N-1
            [t, b]      Returns data for turn=t, bunch=b
            [t, b0:b1]  Returns data for turn=t, bunch=b0..b1
        '''
        if isinstance(slicer, tuple):
            turn = slicer[0]
            bunches = slicer[1]
        else:
            turn = slicer
            bunches = slice(0, self.number_of_bunches)

        if not isinstance(turn, int):
            raise IndexError('turn must be an integer')

        if isinstance(bunches, slice):
            firstbunch = bunches.start
            lastbunch = bunches.stop
        elif isinstance(bunches, int):
            firstbunch = bunches
            lastbunch = bunches
        else:
            raise IndexError('bunch must be an integer or a slice')

        return self.get(turn, firstbunch, lastbunch)

    def t_to_samples(self, t):
        '''Convert a time to samples'''
        return int(np.round(t / self.period))

    def calc_mean(self):
        '''Calculate the mean for baseline subtraction'''
        xx = np.arange(0, int(self.samples_per_bunch * self.number_of_bunches +
                              self.t_to_samples(self.max_offset)), dtype=np.float32) * self.period
        yy = np.zeros_like(xx)

        for i in self.populated_turns:
            x, y = self.get(i, 0, self.number_of_bunches - 1, skip=-1, extra=self.t_to_samples(self.max_offset) + 1,
                            baseline=False, align=False, invert=False)
            if i == 0:
                xx = x[:-1]
                yy = y[:-1]
            else:
                y_interp = interp1d(x, y, assume_sorted=True)
                yy += y_interp(xx)

        self.mean = yy / len(self.populated_turns)

    @property
    def number_of_bunches(self):
        if self.segments == 1:
            return self.harmonic
        else:
            segment_size = self.size / self.segments
            segment_bunches = segment_size / self.samples_per_bunch
            if segment_bunches > self.harmonic:
                return self.harmonic
            else:
                return int(segment_bunches)

    @property
    def trigger_offset(self):
        return int(self.t_to_samples(self.trigger_delay) % self.samples_per_turn)

    @property
    def number_of_turns(self):
        if self.segments == 1:
            samp_before_trig = self.t_to_samples(self.trigger_delay)
            samp_after_trig = self.size - samp_before_trig
            turns_before_trig = int(samp_before_trig / self.samples_per_turn)
            turns_after_trig = int(samp_after_trig / self.samples_per_turn)
            return turns_before_trig + turns_after_trig
        else:
            return self.segments

    @property
    def samples_per_bunch(self):
        return self.frev / self.period / self.harmonic

    @property
    def samples_per_turn(self):
        if self.segments == 1:
            return self.frev / self.period
        else:
            return self.size / self.segments

    @property
    def frev(self):
        return self._frev

    @frev.setter
    def frev(self, val):
        if val != self._frev:
            self._frev = val
            self.mean = None

# EOF
