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

from .DcgEval import DcgEval

class NdcgEval(DcgEval):
    """Compute NDCG (with gain = 2**rel-1 and log2 discount)."""
    def get_value(self, ranking, labels, orientations, cutoff=-1):
        sorted_labels = sorted(labels if isinstance(labels, list) else labels.itervalues(),
                              reverse=True)
        ideal_dcg = self.get_dcg(sorted_labels, cutoff)
        return self.get_dcg([labels[doc.get_id()] for doc in ranking], cutoff) / (
            1.0 if ideal_dcg == 0 else ideal_dcg)

    def evaluate_ranking(self, ranking, query, cutoff=-1):
        """
        Compute NDCG for the provided ranking. The ranking is expected
        to contain document ids in rank order.
        """
        if cutoff == -1 or cutoff > len(ranking):
            cutoff = len(ranking)
        if query.has_ideal():
            ideal_dcg = query.get_ideal()
        else:
            ideal_labels = list(reversed(sorted(query.get_labels())))[:cutoff]
            ideal_dcg = self.get_dcg(ideal_labels, cutoff)
            query.set_ideal(ideal_dcg)

        if ideal_dcg == .0:
            # return 0 when there are no relevant documents. This is consistent
            # with letor evaluation tools; an alternative would be to return
            # 0.5 (e.g., used by the yahoo learning to rank challenge tools)
            return 0.0

        # get labels for the sorted docids
        sorted_labels = [0] * cutoff
        for i in range(cutoff):
            sorted_labels[i] = query.get_label(ranking[i])
        dcg = self.get_dcg(sorted_labels, cutoff)
        return dcg / ideal_dcg
