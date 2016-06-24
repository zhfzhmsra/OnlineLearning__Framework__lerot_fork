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

# KH, 2012/06/20

import numpy as np

from collections import defaultdict
from .AbstractEval import AbstractEval


class PAKEval(AbstractEval):
    """
    Precision at k evaluation. Relevant document in ranking up to index k
    """
    def evaluate_ranking(self, ranking, query, cutoff=-1):
        # If cutoff is out of range, make it length of ranking
        if cutoff == -1 or cutoff > len(ranking):
            cutoff = len(ranking)

        # return dict if value is not in stats_by_vert
        stats_by_vert = defaultdict(lambda: {'total': 0, 'rel': 0})
        for doc in ranking[:cutoff]:
            vert = doc.get_type()
            stats_by_vert[vert]['total'] += 1
            # If document is relevant, add one to counter
            if query.get_labels()[doc.get_id()] > 0:
                stats_by_vert[vert]['rel'] += 1
        # Calculate the precision for ranking
        precisions = [float(s['rel']) / s['total'] for s in stats_by_vert.itervalues()]
        if len(precisions) == 0:
            return 0.0
        return float(sum(precisions)) / len(precisions)
