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

import numpy as np
from .ProbabilisticPerturbator import ProbabilisticPerturbator
from ..utils import create_ranking_vector


class DynamicProbabilisticPerturbator(ProbabilisticPerturbator):
    """
    Application system for dynamic probabilistic perturbation on ranker
    """

    def __init__(self, swap_prob):
        # delta = 0 because of paper
        self.delta = 0

        # First swap probability
        self.first_swap_prob = swap_prob

        # Initialise affirmativeness and iteration
        self.cum_affirm = 0
        self.t = 0

    def update(self, feedback_vec, perturbed_vec, query, ranker):
        """
        Update the cumulative affirmativeness with the affirmativeness of
        the last iteration
        """
        weights = np.transpose(ranker.w)
        new_affirm = np.dot(weights, feedback_vec) \
            - np.dot(weights, perturbed_vec)
        # print "New affirmativeness", new_affirm
        self.cum_affirm += new_affirm
        self.t += 1

    def _calc_max_affirm(self, ranker, query, max_length):
        """
        Calculate the maximum perturbation for the original ranking of this
        iteration
        """
        # Calculate feature vector for original ranking
        ranker.init_ranking(query)
        ranking = self.ranker_to_list(ranker, max_length)
        org_feature_vec = create_ranking_vector(query, ranking)

        # Calculate feature vector for maximum swap ranking
        max_ranking, single_start = self._perturb(1, ranker, query, max_length)
        max_feature_vec = create_ranking_vector(query, max_ranking)

        weights = np.transpose(ranker.w)
        return np.dot(weights, org_feature_vec) \
            - np.dot(weights, max_feature_vec)

    def perturb(self, ranker, query, max_length):
        """
        Calculate perturbed ranking with swap probability based on maximum
        perturbation and the average affirmativeness
        """
        swap_prob = self.get_swap_prob(ranker, query, max_length)

        # Create ranking
        return self._perturb(swap_prob, ranker, query, max_length)

    def get_swap_prob(self, ranker, query, max_length):
        """
        Get the swap probability according to the average affirmativeness
        """
        if self.t:
            # Calculate the maximum perturbation
            max_affirm = self._calc_max_affirm(ranker, query, max_length)

            # Calculate swap probability
            predicted_affirm = self.delta - self.cum_affirm / self.t
            swap_prob = predicted_affirm / max_affirm if max_affirm \
                else predicted_affirm
        else:
            # This is the first iteration
            swap_prob = self.first_swap_prob
        return swap_prob

    def ranker_to_list(self, ranker, max_length):
        """
        Extract the ranking from a ranker,
        put it in a list
        """
        new_ranked = []

        if max_length is None:
            max_length = ranker.document_count()
        else:
            max_length = min(ranker.document_count(), max_length)

        for i in range(max_length):
            new_ranked.append(ranker.next())
        return new_ranked
