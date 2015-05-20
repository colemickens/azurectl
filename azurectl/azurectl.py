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
import sys
import docopt

# project
import logger
from app import App
from azurectl_exceptions import *


def main():
    """
        azurectl - invoke the Application
    """
    logger.init()
    try:
        App()
    except AzureError as e:
        # known exception, log information and exit
        logger.log.error('%s: %s' % (type(e).__name__, format(e)))
        sys.exit(1)
    except docopt.DocoptExit:
        # exception caught by docopt, results in usage message
        raise
    except SystemExit:
        # user exception, program aborted by user
        sys.exit(1)
    except:
        # exception we did no expect, show python backtrace
        logger.log.error('Unexpected error:')
        raise