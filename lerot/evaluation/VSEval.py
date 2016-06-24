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

from .AbstractEval import AbstractEval

class VSEval(AbstractEval):
    """Simple vertical selection (VS) metric, a.k.a. prec_v."""

    def __init__(self):
        pass

    def get_value(self, ranking, labels, orientations, cutoff=-1):
        if cutoff == -1:
            cutoff = len(ranking)
        verts_retrieved = set(d.get_type() for d in ranking[:cutoff] if d.get_type() != 'Web')
        if len(verts_retrieved) == 0:
            return 0.0
        verts_retrieved_relevant = sum(1 for v in verts_retrieved if orientations[v] > 0.5)
        return float(verts_retrieved_relevant) / len(verts_retrieved)
