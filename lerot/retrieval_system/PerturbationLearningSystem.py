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

"""
Retrieval system implementation for use in learning experiments.
"""

import argparse
import numpy

from .AbstractLearningSystem import AbstractLearningSystem
from ..utils import get_class, split_arg_str, create_ranking_vector


class PerturbationLearningSystem(AbstractLearningSystem):
    """A retrieval system that learns online from pairwise comparisons. The
    system keeps track of all necessary state variables (current query,
    weights, etc.) so that comparison and learning classes can be stateless
    (implement only static / class methods)."""

    def __init__(self, feature_count, arg_str):
        # parse arguments
        parser = argparse.ArgumentParser(
            description="Initialize retrieval "
            "system with the specified feedback and learning mechanism.",
            prog="PerturbationLearningSystem"
        )
        parser.add_argument("-w", "--init_weights", help="Initialization "
                            "method for weights (random, zero).",
                            required=True)

        # Perturbation arguments
        parser.add_argument("-p", "--perturbator", required=True)
        parser.add_argument("-b", "--swap_prob", default=0.25, type=float)
        # parser.add_argument("-f", "--perturbator_args", nargs="*")

        parser.add_argument("-r", "--ranker", required=True)
        parser.add_argument("-s", "--ranker_args", nargs="*", default=tuple())
        parser.add_argument("-t", "--ranker_tie", default="random")

        parser.add_argument("-l", "--max_results", default=float('Inf'))

        args = vars(parser.parse_known_args(split_arg_str(arg_str))[0])

        self.ranker_class = get_class(args["ranker"])
        self.ranker_args = args["ranker_args"]
        self.ranker_tie = args["ranker_tie"]
        self.init_weights = args["init_weights"]
        self.feature_count = feature_count
        self.ranker = self.ranker_class(
            self.ranker_args,
            self.ranker_tie,
            self.feature_count,
            sample=None,  # explicitly break sampling
            init=self.init_weights
        )

        self.max_results = args["max_results"]

        self.perturbator = get_class(args["perturbator"])(args["swap_prob"])

    def get_ranked_list(self, query):
        new_ranking, single_start = self.perturbator.perturb(
            self.ranker, query, self.max_results
        )
        self.current_ranking = new_ranking
        self.current_single_start = single_start
        self.current_query = query
        return new_ranking

    def update_solution_once(self, clicks):
        """
        Update the ranker weights without regard to multiple clicks
        on a single link
        """

        new_ranking = self._get_feedback(clicks)

        # Calculate ranking vectors
        current_vector = create_ranking_vector(
            self.current_query,
            self.current_ranking
        )

        new_vector = create_ranking_vector(
            self.current_query,
            new_ranking
        )

        self.perturbator.update(
            new_vector,
            current_vector,
            self.current_query,
            self.ranker
        )

        # Update the weights
        self.ranker.update_weights(new_vector - current_vector, 1)

        return self.get_solution()

    def update_solution(self, clicks):
        """
        Update the ranker weights

        while keeping in mind that documents with a relevance of > 1 are
        clicked more than once
        """

        # Loop through clicks until no clicks are left
        while numpy.count_nonzero(clicks) > 0:
            # Update
            self.update_solution_once(clicks)

            # Remove one click per click
            relevant_clicks = numpy.nonzero(clicks)
            for click_index in relevant_clicks:
                clicks[click_index] -= 1

        return self.get_solution()

    def get_solution(self):
        return self.ranker

    def _get_feedback(self, clicks):
        """
        Get a new ranking of documents, swapped according to user clicks
        """

        max_length = len(self.current_ranking)

        # Check whether new ranking should start with a single start
        if self.current_single_start:
            new_ranking = [self.current_ranking[0]]
        else:
            new_ranking = []
        # Loop for swapping pairs of documents according to clicks
        for i in xrange(self.current_single_start, max_length-1, 2):
            # Swap if there is a click on the lower item of a pair
            if clicks[i+1] and not clicks[i]:
                new_ranking.append(self.current_ranking[i+1])
                new_ranking.append(self.current_ranking[i])
            # Don't swap
            else:
                new_ranking.append(self.current_ranking[i])
                new_ranking.append(self.current_ranking[i+1])

        # Add last index if it hasn't been added yet
        if len(new_ranking) < max_length:
            new_ranking.append(self.current_ranking[max_length-1])

        return new_ranking
