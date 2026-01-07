# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import List

from agentbay.api import models as main_models
from darabonba.model import DaraModel

class ListVolumesResponseBody(DaraModel):
    def __init__(
        self,
        code: str = None,
        data: List[main_models.ListVolumesResponseBodyData] = None,
        http_status_code: int = None,
        max_results: int = None,
        message: str = None,
        next_token: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.code = code
        self.data = data
        self.http_status_code = http_status_code
        self.max_results = max_results
        self.message = message
        self.next_token = next_token
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.data:
            for v1 in self.data:
                if v1:
                    v1.validate()

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.code is not None:
            result['Code'] = self.code

        result['Data'] = []
        if self.data is not None:
            for k1 in self.data:
                result['Data'].append(k1.to_map() if k1 else None)

        if self.http_status_code is not None:
            result['HttpStatusCode'] = self.http_status_code

        if self.max_results is not None:
            result['MaxResults'] = self.max_results

        if self.message is not None:
            result['Message'] = self.message

        if self.next_token is not None:
            result['NextToken'] = self.next_token

        if self.request_id is not None:
            result['RequestId'] = self.request_id

        if self.success is not None:
            result['Success'] = self.success

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Code') is not None:
            self.code = m.get('Code')

        self.data = []
        if m.get('Data') is not None:
            for k1 in m.get('Data'):
                temp_model = main_models.ListVolumesResponseBodyData()
                self.data.append(temp_model.from_map(k1))

        if m.get('HttpStatusCode') is not None:
            self.http_status_code = m.get('HttpStatusCode')

        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')

        if m.get('Message') is not None:
            self.message = m.get('Message')

        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')

        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')

        if m.get('Success') is not None:
            self.success = m.get('Success')

        return self

class ListVolumesResponseBodyData(DaraModel):
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

