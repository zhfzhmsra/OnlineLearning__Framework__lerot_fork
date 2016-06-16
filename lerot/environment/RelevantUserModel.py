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

# KH 07/10/2012

import argparse
import re

from numpy import zeros

from .AbstractUserModel import AbstractUserModel
from ..utils import split_arg_str


class RelevantUserModel(AbstractUserModel):
    """
    Defines a user model that clicks on all relevant documents in a list
    with an optional limit
    """

    def __init__(self, arg_str):
        parser = argparse.ArgumentParser(
            description="Defines a user model that clicks on all relevant "
            "documents in a list with an optional limit",
            prog="RelevantUserModel")
        parser.add_argument("-limit", "--result_click_limit", default=-1)
        args = vars(parser.parse_args(split_arg_str(arg_str)))
        self.result_limit = int(args["result_click_limit"])

    def get_clicks(self, result_list, labels, **kwargs):
        click_list = zeros(len(result_list), dtype='int')
        for result_index, d in enumerate(result_list):
            if self.result_limit == result_index:
                break
            # Sets the click amount to the relevance value of a document
            click_list[result_index] = labels[d.get_id()]
        return click_list
