#     Copyright 2017 Google, Inc.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
"""
.. module: security_monkey.watchers.gcp.gcs.bucket
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor:: Tom Melendez <supertom@google.com> @supertom

"""
from security_monkey.common.gcp.util import gcp_resource_id_builder, identifiers_from_account_names
from security_monkey.watcher import Watcher
from security_monkey.watcher import ChangeItem

from cloudaux.gcp.decorators import iter_project
from cloudaux.gcp.gcs import list_buckets
from cloudaux.orchestration.gcp.gcs.bucket import get_bucket


class GCSBucket(Watcher):
    index = 'gcsbucket'
    i_am_singular = 'GCSBucket'
    i_am_plural = 'GCSBuckets'
    account_type = 'GCP'

    def __init__(self, accounts=None, debug=False):
        super(GCSBucket, self).__init__(accounts=accounts, debug=debug)
        self.honor_ephemerals = True
        self.ephemeral_paths = [
            "Etag",
        ]

    def slurp(self):
        """
        :returns: item_list - list of GCSBuckets.
        :returns: exception _map - A dict where the keys are a tuple containing the
        location of the exception and the value is the actual exception
        """
        self.prep_for_slurp()
        account_identifiers = identifiers_from_account_names(self.accounts)

        @iter_project(projects=account_identifiers)
        def slurp_items(**kwargs):
            item_list = []
            buckets = list_buckets()

            for bucket in buckets:
                resource_id = gcp_resource_id_builder(
                    'storage.bucket.get', bucket['name'])
                b = get_bucket(
                    bucket_name=bucket['name'], **kwargs)
                item_list.append(
                    GCSBucketItem(
                        region=b['Location'],
                        account=kwargs['project'],
                        name=b['Id'],
                        arn=resource_id,
                        config=b))
            return item_list, kwargs.get('exception_map', {})

        return slurp_items()


class GCSBucketItem(ChangeItem):

    def __init__(self,
                 region=None,
                 account=None,
                 name=None,
                 arn=None,
                 config=None):
        if config is None:
            config = {}
        super(GCSBucketItem, self).__init__(
            index=GCSBucket.index,
            region=region,
            account=account,
            name=name,
            arn=arn,
            new_config=config)
