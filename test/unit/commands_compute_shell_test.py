import sys
import mock
from collections import namedtuple
from mock import patch


from test_helper import *

import azurectl
from azurectl.account.service import AzureAccount
from azurectl.commands.compute_shell import ComputeShellTask
from azurectl.config.parser import Config


class TestComputeShellTask:
    def setup(self):
        sys.argv = [
            sys.argv[0], '--config', '../data/config',
            'compute', 'shell'
        ]

        account = AzureAccount(
            Config(
                region_name='East US 2', filename='../data/config'
            )
        )
        credentials = namedtuple(
            'credentials',
            ['private_key', 'certificate', 'subscription_id', 'management_url']
        )
        account.publishsettings = mock.Mock(
            return_value=credentials(
                private_key='abc',
                certificate='abc',
                subscription_id='4711',
                management_url='test.url'
            )
        )
        account.get_blob_service_host_base = mock.Mock(
            return_value='.blob.test.url'
        )
        account.storage_key = mock.Mock()

        azurectl.commands.compute_shell.AzureAccount = mock.Mock(
            return_value=account
        )

        self.task = ComputeShellTask()

    @patch('azurectl.commands.compute_shell.code.interact')
    def test_process_compute_shell(self, mock_interact):
        self.task.command_args = {}
        self.task.process()
        assert mock_interact.called
