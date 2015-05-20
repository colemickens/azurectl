import sys
from nose.tools import *

import nose_helper

from azurectl.help import Help
from azurectl.azurectl_exceptions import *


class TestHelp:
    def setup(self):
        self.help = Help()

    @raises(AzureHelpNoCommandGiven)
    def test_show(self):
        self.help.show(None)
