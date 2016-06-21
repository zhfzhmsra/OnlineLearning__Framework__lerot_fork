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

class LivingLabsEval:

    __wins_list__ = None


    def __init__(self):
        self.__wins_list__ = []



    def update_score(self, wins):
        self.__wins_list__.append(wins)


    def get_win(self):
        return self.__wins_list__[len(self.__wins_list__)-1]


    def get_performance(self):
        total_wins = 0
        total_losses = 0
        for i in self.__wins_list__:
            if i[0]>i[1]:
                total_wins += 1
            if i[0]<i[1]:
                total_losses += 1
        if total_wins > 0:
            return (float(total_wins) / (total_losses + total_wins) )
