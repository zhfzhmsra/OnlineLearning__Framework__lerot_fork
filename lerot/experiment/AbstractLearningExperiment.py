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

import random
from ..utils import get_class


class AbstractLearningExperiment:

    def __init__(
            self, training_queries, test_queries, feature_count, log_fh, args):
        """Initialize an experiment using the provided arguments."""
        self.log_fh = log_fh
        self.training_queries = training_queries
        self.test_queries = test_queries
        self.feature_count = feature_count
        # construct system according to provided arguments
        self.num_queries = args["num_queries"]
        self.query_sampling_method = args["query_sampling_method"]
        self.um_class = get_class(args["user_model"])
        self.um_args = args["user_model_args"]
        self.um = self.um_class(self.um_args)
        self.system_class = get_class(args["system"])
        self.system_args = args["system_args"]
        self.system = self.system_class(self.feature_count, self.system_args)
        # if isinstance(self.system, AbstractOracleSystem):
        #     self.system.set_test_queries(self.test_queries)
        self.evaluations = []
        for eval_args in args["evaluation"]:
            # Handle evaluation arguments
            split_args = eval_args.split()
            # First element in this list is the evaluation method
            kwargs = {}
            # read in additional arguments
            for i in xrange(1, len(split_args)-1, 2):
                kwargs[split_args[i]] = int(split_args[i+1])

            # Here go default values
            if 'cutoff' not in kwargs:
                kwargs['cutoff'] = -1

            # Put everything in dict
            eval_name = split_args[0]
            kwargs['eval_class'] = get_class(eval_name)()
            self.evaluations.append((eval_name, kwargs))
        self.queryid = None

    def _sample_qid(self, query_keys, query_count, query_length):
            if self.query_sampling_method == "random":
                return query_keys[random.randint(0, query_length - 1)]
            elif self.query_sampling_method == "fixed":
                return query_keys[query_count % query_length]
            elif self.query_sampling_method == "one":
                if self.queryid is None:
                    self.queryid = random.randrange(query_length)
                return query_keys[self.queryid]

    def run(self):
        raise NotImplementedError("Derived class needs to implement run.")
