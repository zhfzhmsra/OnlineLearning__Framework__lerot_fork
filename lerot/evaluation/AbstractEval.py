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

from random import sample
from numpy import mean


class AbstractEval:
    """
    Abstract base class for computing evaluation metrics for given relevance
    labels.
    """

    def __init__(self):
        self.prev_solution_w = None
        self.prev_score = None

    def evaluate_all(self, solution, queries, cutoff=-1, ties="random"):
        """
        Evaluate all queries given a certain solution
        """
        outcomes = []
        for query in queries:
            outcomes.append(self.evaluate_one(solution, query, cutoff, ties))
        score = mean(outcomes)

        self.prev_solution_w = solution.w
        self.prev_score = score

        return score

    def evaluate_one(self, solution, query, cutoff=-1, ties="random"):
        """
        Evaluate one query with a provided solution
        """

        scores = solution.score(query.get_feature_vectors())
        sorted_docs = self._sort_docids_by_score(query.get_docids(), scores,
                                                 ties=ties)
        return self.evaluate_ranking(sorted_docs, query, cutoff)

    def evaluate_ranking(self, ranking, query, cutoff=-1):
        raise NotImplementedError("Derived class needs to implement this.")

    def _sort_docids_by_score(self, docids, scores, ties="random"):
        n = len(docids)
        if ties == "first":
            scored_docids = zip(scores, reversed(range(n)), docids)
        elif ties == "last":
            scored_docids = zip(scores, range(n), docids)
        elif ties == "random":
            scored_docids = zip(scores, sample(range(n), n), docids)
        else:
            raise Exception("Unknown method for breaking ties: \"%s\"" % ties)
        scored_docids.sort(reverse=True)
        return [docid for _, _, docid in scored_docids]
