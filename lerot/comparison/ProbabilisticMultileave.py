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

import argparse
from collections import defaultdict
from random import randint
import random

from AbstractInterleavedComparison import AbstractInterleavedComparison
import numpy as np

from ..utils import split_arg_str


class ProbabilisticMultileave(AbstractInterleavedComparison):
    """Probabilistic ..."""

    def __init__(self, arg_str=None):
        '''
        TODO: docstring

        ARGS:
        - aggregate: "expectation", "log-likelihood-ratio",
            "likelihood-ratio", "log-ratio", "binary"
        - det_interleave: If true, use deterministic interleaving, regardless
            of the ranker type used for comparison.
        - compare_td: if TRUE, compare rankers using observed assignment
            instead of marginalizing over possible assignments.
        '''
        if arg_str:
            parser = argparse.ArgumentParser(description="Parse arguments for "
                "interleaving method.", prog=self.__class__.__name__)
            parser.add_argument("-a", "--aggregate", choices=["expectation",
                "log-likelihood-ratio", "likelihood-ratio", "log-ratio",
                "binary"])
            parser.add_argument("-d", "--det_interleave", type=bool,
                help="If true, use deterministic interleaving, regardless "
                "of the ranker type used for comparison.")
            parser.add_argument("-t", "--compare_td", type=bool,
                help="If true, compare rankers using observed assignments "
                "instead of marginalizing over possible assignments.")
            parser.add_argument("-c", "--credits", type=bool,
                help="If true, return credits of rankers instead of ranks.")
            args = vars(parser.parse_known_args(split_arg_str(arg_str))[0])
            if "aggregate" in args and args["aggregate"]:
                self.aggregate = args["aggregate"]
            if "det_interleave" in args and args["det_interleave"]:
                self.det_interleave = True
            if "compare_td" in args and args["compare_td"]:
                self.compare_td = True
            if "credits" in args and args["credits"]:
                self.credits = True
        if not hasattr(self, "aggregate") or not self.aggregate:
            self.aggregate = "expectation"
        if not hasattr(self, "det_interleave"):
            self.det_interleave = False
        if not hasattr(self, "compare_td"):
            self.compare_td = False
        if not hasattr(self, "credits"):
            self.credits = False

    def multileave(self, rankers, query, length):
        '''
        TODO: DOCSTRING

        ARGS:
        - rankers: a list of ...
        - query: ...
        - length: the desired length of the lists

         RETURNS:
        - l: multileaved list of documents
        - a: list indicating which ranker is used at each row of l
        '''
        d = defaultdict(list)
        for i, r in enumerate(rankers):
            d[i] = r.init_ranking(query)

        length = min([length] + [r.document_count() for r in rankers])
        # start with empty document list
        l = []
        # random bits indicate which r to use at each rank
        #a = np.asarray([randint(0, len(rankers) - 1) for _ in range(length)])
        a = []
        pool = []
        while len(a) < length:
            if len(pool) == 0:
                pool = range(len(rankers))
                random.shuffle(pool)
            a.append(pool.pop())
        for next_a in a:
            # flip coin - which r contributes doc (pre-computed in a)
            select = rankers[next_a]
            others = [r for r in rankers if r is not select]
            # draw doc
            pick = select.next()
            l.append(pick)
            # let other ranker know that we removed this document
            for o in others:
                try:
                    o.rm_document(pick)
                    # TODO remove try / catch block
                except:
                    pass
        return (np.asarray(l), a)

    def infer_outcome(self, l, rankers, clicks, query):
        '''
        TODO: DOCSTRING

        ARGS:
        - l: the created list of documents, using multileaving
        - rankers: the rankers
        - clicks: the clicks
        - query: the query

        RETURNS
        - The Credits
        '''

        click_ids = np.where(np.asarray(clicks) == 1)[0]
        if not len(click_ids):  # no clicks, will be a tie
            # return [1/float(len(rankers))]*len(rankers)
            # the decision could be made to give each ranker equal credit in a
            # tie so all rankers get rank 1
            if (self.credits):
                return [1.0/float(len(rankers))] * len(rankers)
            return [1] * len(rankers)

        for r in rankers:
            r.init_ranking(query)
        p = self.probability_of_list(l, rankers, click_ids)

        creds = self.credits_of_list(p)

        if (self.credits):
            return creds
        return self.credits_to_outcome(creds)

    def get_rank(self, ranker, documents):
        '''
        Return the rank of given documents in given ranker.
        Note: rank is not index (rank is index+1)

        ARGS:
        - ranker
        - documents

        RETURN:
        - a list containing the rank in the ranker for each of the documents
        '''
        ranks = [None] * len(documents)
        docsInRanker = ranker.docids

        for i, d in enumerate(documents):
            if d in docsInRanker:
                ranks[i] = docsInRanker.index(d) + 1
        return ranks

    def probability_of_list(self, result_list, rankers, clickedDocs):
        '''
        ARGS:
        - result_list: the multileaved list
        - rankers: a list of rankers
        - clickedDocs: the docIds in the result_list which recieved a click

        RETURNS
        -sigmas: list with for each click the list containing the probability
         that the list comes from each ranker
        '''
        tau = 0.3
        n = len(rankers[0].docids)
        sigmoid_total = np.sum(float(n) / (np.arange(n) + 1) ** tau)
        sigmas = np.zeros([len(clickedDocs), len(rankers)])
        for i, r in enumerate(rankers):
            ranks = np.array(self.get_rank(r, result_list))
            for j in range(len(clickedDocs)):
                click = clickedDocs[j]
                sigmas[j, i] = ranks[click] / (sigmoid_total
                                               - np.sum(float(n) /
                                                        (ranks[: click]
                                                         ** tau)))
        for i in range(sigmas.shape[0]):
            sigmas[i, :] = sigmas[i, :] / np.sum(sigmas[i, :])
        return list(sigmas)

    def credits_of_list(self, p):
        '''
        ARGS:
        -p: list with for each click the list containing the probability that
            the list comes from each ranker

        RETURNS:
        - credits: list of credits for each ranker
        '''
        creds = [np.average(col) for col in zip(*p)]
        return creds

    def credits_to_outcome(self, creds):
        rankers_credits = sorted(zip(range(len(creds)), creds), reverse=True,
                                 key=lambda item: item[1])

        ranked_credits = len(rankers_credits)*[None]
        last_c = None
        last_rank = 0
        rank = 0
        for (r, c) in rankers_credits:
            rank += 1
            if not (c == last_c):
                ranked_credits[r] = rank
                last_rank = rank
            else:
                ranked_credits[r] = last_rank
            last_c = c

        return ranked_credits
