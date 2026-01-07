# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from darabonba.model import DaraModel

class DeleteVolumeRequest(DaraModel):
    def __init__(
        self,
        authorization: str = None,
        volume_id: str = None,
    ):
        self.authorization = authorization
        # This parameter is required.
        self.volume_id = volume_id

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.authorization is not None:
            result['Authorization'] = self.authorization

        if self.volume_id is not None:
            result['VolumeId'] = self.volume_id

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Authorization') is not None:
            self.authorization = m.get('Authorization')

        if m.get('VolumeId') is not None:
            self.volume_id = m.get('VolumeId')

        return self

