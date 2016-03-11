# Copyright (c) 2016 SUSE.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
usage: azurectl compute shell

commands:
    shell
        start a python shell within the azure context

"""
import code
import os
from tempfile import NamedTemporaryFile
from textwrap import dedent
# project
from logger import log
from cli_task import CliTask
from azure_account import AzureAccount
from azure.servicemanagement import ServiceManagementService


class ComputeShellTask(CliTask):
    """
        Interactive shell
    """
    def process(self):

        account = AzureAccount(self.config)
        cert_file = NamedTemporaryFile()
        cert_file.write(account.publishsettings().private_key)
        cert_file.write(account.publishsettings().certificate)
        cert_file.flush()

        self.service = ServiceManagementService(
            account.publishsettings().subscription_id,
            cert_file.name,
            account.publishsettings().management_url
        )

        print dedent("""
            An instance of azure.servicemanagement.ServiceManagementService has
            been instantiated using the supplied credentials, as `service`.

            When you're finished, exit with `exit()`
        """)
        code.interact(local={'service': self.service})