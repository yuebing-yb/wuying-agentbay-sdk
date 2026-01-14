# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from darabonba.model import DaraModel

class GetVolumeRequest(DaraModel):
    def __init__(
        self,
        allow_create: bool = None,
        authorization: str = None,
        image_id: str = None,
        volume_name: str = None,
    ):
        self.allow_create = allow_create
        self.authorization = authorization
        self.image_id = image_id
        self.volume_name = volume_name

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.allow_create is not None:
            result['AllowCreate'] = self.allow_create

        if self.authorization is not None:
            result['Authorization'] = self.authorization

        if self.image_id is not None:
            result['ImageId'] = self.image_id

        if self.volume_name is not None:
            result['VolumeName'] = self.volume_name

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AllowCreate') is not None:
            self.allow_create = m.get('AllowCreate')

        if m.get('Authorization') is not None:
            self.authorization = m.get('Authorization')

        if m.get('ImageId') is not None:
            self.image_id = m.get('ImageId')

        if m.get('VolumeName') is not None:
            self.volume_name = m.get('VolumeName')

        return self

