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

import unittest
import cStringIO
import numpy as np

import lerot.query as query
import lerot.utils as utils


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def testSplitArgStr(self):
        split = utils.split_arg_str("--a 10 --b foo --c \"--d bar --e 42\"")
        self.assertEqual(split, ["--a", "10", "--b", "foo", "--c",
            "--d bar --e 42"], "wrong split (1): %s" % ", ".join(split))
        split = utils.split_arg_str("\"--a\" 10 --b foo --c --d bar --e 42")
        self.assertEqual(split, ["--a", "10", "--b", "foo", "--c", "--d",
            "bar", "--e", "42"], "wrong split (2): %s" % ", ".join(split))
        split = utils.split_arg_str("\"--a\"\" 10\"--b foo --c --d bar --e 42")
        self.assertEqual(split, ["--a", " 10", "--b", "foo", "--c", "--d",
            "bar", "--e", "42"], "wrong split (2): %s" % ", ".join(split))

    def testRank(self):
        scores = [2.1, 2.9, 2.3, 2.3, 5.5]
        self.assertIn(utils.rank(scores, ties="random"),
                      [[0, 3, 1, 2, 4], [0, 3, 2, 1, 4]])
        self.assertIn(utils.rank(scores, reverse=True, ties="random"),
                      [[4, 1, 3, 2, 0], [4, 1, 2, 3, 0]])
        self.assertEqual(utils.rank(scores, reverse=True, ties="first"),
                         [4, 1, 2, 3, 0])
        self.assertEqual(utils.rank(scores, reverse=True, ties="last"),
                         [4, 1, 3, 2, 0])

        scores = [2.1, 2.9, 2.3, 2.3, 5.5, 2.9]
        self.assertIn(utils.rank(scores, ties="random"),
                      [[0, 4, 2, 1, 5, 3],
                       [0, 3, 2, 1, 5, 4],
                       [0, 4, 1, 2, 5, 3],
                       [0, 3, 1, 2, 5, 4]])
        self.assertIn(utils.rank(scores, reverse=True, ties="random"),
                      [[5, 1, 3, 4, 0, 2],
                       [5, 2, 3, 4, 0, 1],
                       [5, 1, 4, 3, 0, 2],
                       [5, 2, 4, 3, 0, 1]])
        self.assertEqual(utils.rank(scores, reverse=True, ties="first"),
                         [5, 1, 3, 4, 0, 2])
        self.assertEqual(utils.rank(scores, reverse=True, ties="last"),
                         [5, 2, 4, 3, 0, 1])

    def test_create_ranking_vector(self):
        feature_count = 5
        # Create queries to test with
        test_queries = """
            1 qid:373 1:0.080000 2:0.500000 3:0.500000 4:0.500000 5:0.160000
            0 qid:373 1:0.070000 2:0.180000 3:0.000000 4:0.250000 5:0.080000
            0 qid:373 1:0.150000 2:0.016000 3:0.250000 4:0.250000 5:0.150000
            0 qid:373 1:0.100000 2:0.250000 3:0.500000 4:0.750000 5:0.130000
            0 qid:373 1:0.050000 2:0.080000 3:0.250000 4:0.250000 5:0.060000
            0 qid:373 1:0.050000 2:1.000000 3:0.250000 4:0.250000 5:0.160000
        """
        hard_gamma = [1, 0.63092975357, 0.5, 0.43067655807, 0.38685280723,
                      0.3562071871]
        hard_ranking_vector = [0.27938574, 1.11639191, 1.02610328, 1.29150486,
                               0.42166665]
        query_fh = cStringIO.StringIO(test_queries)
        this_query = query.Queries(query_fh, feature_count)['373']
        query_fh.close()
        fake_ranking = sorted(this_query.get_docids())
        # gamma, ranking_vector = utils.create_ranking_vector(
        ranking_vector = utils.create_ranking_vector(
            this_query, fake_ranking)
        # self.assertEqual(len(gamma), len(hard_gamma))
        self.assertEqual(feature_count, len(ranking_vector))
        # for i in xrange(0, len(gamma)):
        #     self.assertAlmostEqual(gamma[i], hard_gamma[i])

        for j in xrange(0, feature_count):
            self.assertAlmostEqual(ranking_vector[j], hard_ranking_vector[j])


if __name__ == '__main__':
    unittest.main()
