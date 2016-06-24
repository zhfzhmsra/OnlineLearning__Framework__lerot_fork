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

from numpy import *
from numpy.random import shuffle
import logging
import argparse

from AbstractSampler import AbstractSampler

import numpy
numpy.set_printoptions(threshold=10000)


class BaselineSampler(AbstractSampler):
    def __init__(self, arms=[], arg_str=""):
        parser = argparse.ArgumentParser(prog=self.__class__.__name__)
        parser.add_argument("--NM_champion", type=int, default=-1)
        args = vars(parser.parse_known_args(arg_str.split())[0])
        self.nArms = len(arms)  # Number of arms
        self.lArms = arms       # Arms as a list of arms
        self.iArms = range(self.nArms)   # The indices of the arms
        self.dictArms = dict(zip(self.lArms, self.iArms))  # A dictionary
                                                #taking arms to their indices.
        self.RealWins = ones([self.nArms, self.nArms])
        self.plays = {}
        self.champ = args["NM_champion"]
        if self.champ in self.iArms:
            Arms = [self.champ]
        else:
            Arms = self.iArms
        for arm1 in self.iArms:
            self.plays[arm1] = {}
            for arm2 in Arms:
                if arm1 == arm2:
                    continue
                self.plays[arm1][arm2] = 0
        logging.info("Number of arms = %d" % self.nArms)
#        logging.info("Set of arms: %s" % arms)
        self.chatty = False
        self.t = 1

    def get_arms(self):
        # This returns two arms to compare.
        minplays = None
        mina1 = None
        mina2 = None
        for a1 in self.plays:
            for a2 in self.plays[a1]:
                if minplays is None or self.plays[a1][a2] <= minplays:
                    minplays = self.plays[a1][a2]
                    mina1 = a1
                    mina2 = a2
        self.plays[mina1][mina2] += 1
        if self.chatty:
            logging.info("Selected arm %d and arm %d" % (mina1,
                                                         mina2))
        return self.lArms[mina1], self.lArms[mina2], mina1, mina2

    def update_scores(self, winner, loser, score=1):
        winner = self.dictArms[winner]
        loser = self.dictArms[loser]
        self.RealWins[winner, loser] += score
        self.t += 1
        if self.t % 1000 == 0 and self.nArms <= 20:
            logging.info("Time: %d\n Score sheet: \n%s \n Preference Matrix: \n%s"
                         % (self.t,self.RealWins,
                            self.RealWins/(self.RealWins+self.RealWins.T)))
        return winner

    def get_winner(self):
        rWins = self.RealWins
        scores = rWins.sum(axis=1)
        topScore = sort(scores)[-1]
        Inds = nonzero(scores == topScore)[0]
        shuffle(Inds)
        firstPlace = Inds[0]
        return self.lArms[firstPlace]
