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

import scipy
import scipy.stats

from .AbstractEval import AbstractEval

class RPEval(AbstractEval):
    """Simple vertical selection (RP) metric, a.k.a. corr."""

    def __init__(self):
        pass

    def get_value(self, ranking, labels, orientations, cutoff=-1, ideal_ranking=None):
        assert ideal_ranking is not None
        if cutoff == -1:
            cutoff = len(ranking)
        cutoff = min([cutoff, len(ranking), len(ideal_ranking)])
        this_page_rels = [labels[d.get_id()] for d in ranking[:cutoff]]
        ideal_page_rels = [labels[d.get_id()] for d in ideal_ranking[:cutoff]]
        return scipy.stats.spearmanr(this_page_rels, ideal_page_rels)[0]
