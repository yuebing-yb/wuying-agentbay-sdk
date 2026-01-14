# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from agentbay.api import models as main_models
from darabonba.model import DaraModel

class GetVolumeResponseBody(DaraModel):
    def __init__(
        self,
        code: str = None,
        data: main_models.GetVolumeResponseBodyData = None,
        http_status_code: int = None,
        message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.code = code
        self.data = data
        self.http_status_code = http_status_code
        self.message = message
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.code is not None:
            result['Code'] = self.code

        if self.data is not None:
            result['Data'] = self.data.to_map()

        if self.http_status_code is not None:
            result['HttpStatusCode'] = self.http_status_code

        if self.message is not None:
            result['Message'] = self.message

        if self.request_id is not None:
            result['RequestId'] = self.request_id

        if self.success is not None:
            result['Success'] = self.success

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Code') is not None:
            self.code = m.get('Code')

        if m.get('Data') is not None:
            temp_model = main_models.GetVolumeResponseBodyData()
            self.data = temp_model.from_map(m.get('Data'))

        if m.get('HttpStatusCode') is not None:
            self.http_status_code = m.get('HttpStatusCode')

        if m.get('Message') is not None:
            self.message = m.get('Message')

        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')

        if m.get('Success') is not None:
            self.success = m.get('Success')

        return self

class GetVolumeResponseBodyData(DaraModel):
    def __init__(
        self,
        belonging_image_id: str = None,
        create_time: str = None,
        status: str = None,
        volume_id: str = None,
        volume_name: str = None,
    ):
        self.belonging_image_id = belonging_image_id
        self.create_time = create_time
        self.status = status
        self.volume_id = volume_id
        self.volume_name = volume_name

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.belonging_image_id is not None:
            result['BelongingImageId'] = self.belonging_image_id

        if self.create_time is not None:
            result['CreateTime'] = self.create_time

        if self.status is not None:
            result['Status'] = self.status

        if self.volume_id is not None:
            result['VolumeId'] = self.volume_id

        if self.volume_name is not None:
            result['VolumeName'] = self.volume_name

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('BelongingImageId') is not None:
            self.belonging_image_id = m.get('BelongingImageId')

        if m.get('CreateTime') is not None:
            self.create_time = m.get('CreateTime')

        if m.get('Status') is not None:
            self.status = m.get('Status')

        if m.get('VolumeId') is not None:
            self.volume_id = m.get('VolumeId')

        if m.get('VolumeName') is not None:
            self.volume_name = m.get('VolumeName')

        return self

