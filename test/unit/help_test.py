import sys
from nose.tools import *
from azure_cli.help import Help
from azure_cli.exceptions import *

class TestHelp:
    def setup(self):
        self.help = Help({'<command>': ''})

    @raises(AzureNoCommandGiven)
    def test_show(self):
        self.help.show()
