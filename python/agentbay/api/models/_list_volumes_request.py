# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import List

from darabonba.model import DaraModel

class ListVolumesRequest(DaraModel):
    def __init__(
        self,
        authorization: str = None,
        image_id: str = None,
        max_results: int = None,
        next_token: str = None,
        volume_ids: List[str] = None,
        volume_name: str = None,
    ):
        self.authorization = authorization
        self.image_id = image_id
        self.max_results = max_results
        self.next_token = next_token
        self.volume_ids = volume_ids
        self.volume_name = volume_name

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.authorization is not None:
            result['Authorization'] = self.authorization

        if self.image_id is not None:
            result['ImageId'] = self.image_id

        if self.max_results is not None:
            result['MaxResults'] = self.max_results

        if self.next_token is not None:
            result['NextToken'] = self.next_token

        if self.volume_ids is not None:
            result['VolumeIds'] = self.volume_ids

        if self.volume_name is not None:
            result['VolumeName'] = self.volume_name

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Authorization') is not None:
            self.authorization = m.get('Authorization')

        if m.get('ImageId') is not None:
            self.image_id = m.get('ImageId')

        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')

        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')

        if m.get('VolumeIds') is not None:
            self.volume_ids = m.get('VolumeIds')

        if m.get('VolumeName') is not None:
            self.volume_name = m.get('VolumeName')

        return self

