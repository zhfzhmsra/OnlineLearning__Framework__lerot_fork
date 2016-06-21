# This file is part of Lerot.
#
# Lerot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lerot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Lerot.  If not, see <http://www.gnu.org/licenses/>.

from collections import defaultdict

from .AbstractEval import AbstractEval

class ISEval(AbstractEval):
    """Simple vertical selection (IS) metric, a.k.a. mean-prec."""

    def __init__(self):
        pass

    def get_value(self, ranking, labels, orientations, cutoff=-1):
        if cutoff == -1:
            cutoff = len(labels)
        stats_by_vert = defaultdict(lambda: {'total': 0, 'rel': 0})
        for d in ranking[:cutoff]:
            vert = d.get_type()
            if vert == 'Web':
                continue
            stats_by_vert[vert]['total'] += 1
            if labels[d.get_id()] > 0:
                stats_by_vert[vert]['rel'] += 1
        precisions = [float(s['rel']) / s['total'] for s in stats_by_vert.itervalues()]
        if len(precisions) == 0:
            return 0.0
        return float(sum(precisions)) / len(precisions)
