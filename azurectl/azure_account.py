# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
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
from collections import namedtuple
from xml.dom import minidom
from OpenSSL.crypto import *
from tempfile import NamedTemporaryFile
from azure.servicemanagement import ServiceManagementService
import base64

# project
from azurectl_exceptions import (
    AzureServiceManagementError,
    AzureSubscriptionPrivateKeyDecodeError,
    AzureSubscriptionCertificateDecodeError,
    AzureSubscriptionIdNotFound,
    AzureSubscriptionParseError,
    AzureManagementCertificateNotFound,
    AzureSubscriptionPKCS12DecodeError
)
from config import Config


class AzureAccount:
    """
        Azure Service and Storage account handling
    """
    def __init__(self, account_name=None, filename=None):
        self.config = Config(account_name, filename)
        self.service = None

    def storage_name(self):
        return self.config.get_option('storage_account_name')

    def storage_container(self):
        return self.config.get_option('storage_container_name')

    def storage_key(self, name=None):
        self.__get_service()
        if not name:
            name = self.storage_name()
        account_keys = self.service.get_storage_account_keys(name)
        return account_keys.storage_service_keys.primary

    def instance_types(self):
        self.__get_service()
        result = []
        for rolesize in self.service.list_role_sizes():
            memory = rolesize.memory_in_mb
            cores = rolesize.cores
            disks = rolesize.max_data_disk_count
            size = rolesize.virtual_machine_resource_disk_size_in_mb
            instance_type = {
                rolesize.name: {
                    'memory': format(memory) + 'MB',
                    'cores': cores,
                    'max_disk_count': disks,
                    'disk_size': format(size) + 'MB'
                }
            }
            result.append(instance_type)
        return result

    def storage_names(self):
        self.__get_service()
        result = []
        for storage in self.service.list_storage_accounts():
            result.append(storage.service_name)
        return result

    def publishsettings(self):
        credentials = namedtuple(
            'credentials',
            ['private_key', 'certificate', 'subscription_id']
        )
        p12 = self.__read_p12()
        result = credentials(
            private_key=self.__get_private_key(),
            certificate=self.__get_certificate(),
            subscription_id=self.__get_subscription_id()
        )
        return result

    def __get_service(self):
        if self.service:
            return
        publishsettings = self.publishsettings()
        self.cert_file = NamedTemporaryFile()
        self.cert_file.write(publishsettings.private_key)
        self.cert_file.write(publishsettings.certificate)
        self.cert_file.flush()
        try:
            self.service = ServiceManagementService(
                publishsettings.subscription_id,
                self.cert_file.name
            )
        except Exception as e:
            raise AzureServiceManagementError(
                '%s: %s' % (type(e).__name__, format(e))
            )

    def __get_private_key(self):
        p12 = self.__read_p12()
        try:
            return dump_privatekey(
                FILETYPE_PEM, p12.get_privatekey()
            )
        except Exception as e:
            raise AzureSubscriptionPrivateKeyDecodeError(
                '%s: %s' % (type(e).__name__, format(e))
            )

    def __get_certificate(self):
        p12 = self.__read_p12()
        try:
            return dump_certificate(
                FILETYPE_PEM, p12.get_certificate()
            )
        except Exception as e:
            raise AzureSubscriptionCertificateDecodeError(
                '%s: %s' % (type(e).__name__, format(e))
            )

    def __get_subscription_id(self):
        xml = self.__read_xml()
        subscriptions = xml.getElementsByTagName('Subscription')
        try:
            return subscriptions[0].attributes['Id'].value
        except:
            raise AzureSubscriptionIdNotFound(
                'No Subscription.Id found in %s' % self.settings
            )

    def __read_xml(self):
        try:
            self.settings = self.config.get_option('publishsettings')
            return minidom.parse(self.settings)
        except Exception as e:
            raise AzureSubscriptionParseError(
                '%s: %s' % (type(e).__name__, format(e))
            )

    def __read_p12(self):
        xml = self.__read_xml()
        try:
            profile = xml.getElementsByTagName('Subscription')
            cert = profile[0].attributes['ManagementCertificate'].value
        except:
            raise AzureManagementCertificateNotFound(
                'No PublishProfile.ManagementCertificate found in %s' %
                self.settings
            )
        try:
            return load_pkcs12(base64.b64decode(cert), '')
        except Exception as e:
            raise AzureSubscriptionPKCS12DecodeError(
                '%s: %s' % (type(e).__name__, format(e))
            )
