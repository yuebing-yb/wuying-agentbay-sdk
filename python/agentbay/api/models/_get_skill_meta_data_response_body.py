# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import List, Optional

from agentbay.api import models as main_models
from darabonba.model import DaraModel


class GetSkillMetaDataResponseBody(DaraModel):
    def __init__(
        self,
        code: Optional[str] = None,
        data: Optional["GetSkillMetaDataResponseBodyData"] = None,
        http_status_code: Optional[int] = None,
        message: Optional[str] = None,
        request_id: Optional[str] = None,
        success: Optional[bool] = None,
        total_count: Optional[int] = None,
    ):
        self.code = code
        self.data = data
        self.http_status_code = http_status_code
        self.message = message
        self.request_id = request_id
        self.success = success
        self.total_count = total_count

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

        if self.total_count is not None:
            result['TotalCount'] = self.total_count

        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get('Code') is not None:
            self.code = m.get('Code')

        if m.get('Data') is not None:
            temp_model = main_models.GetSkillMetaDataResponseBodyData()
            self.data = temp_model.from_map(m.get('Data'))

        if m.get('HttpStatusCode') is not None:
            self.http_status_code = m.get('HttpStatusCode')

        if m.get('Message') is not None:
            self.message = m.get('Message')

        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')

        if m.get('Success') is not None:
            self.success = m.get('Success')

        if m.get('TotalCount') is not None:
            self.total_count = m.get('TotalCount')

        return self


class GetSkillMetaDataResponseBodyData(DaraModel):
    def __init__(
        self,
        meta_data_list: Optional[List["GetSkillMetaDataResponseBodyDataMetaDataList"]] = None,
        skill_path: Optional[str] = None,
    ):
        self.meta_data_list = meta_data_list
        self.skill_path = skill_path

    def validate(self):
        if self.meta_data_list:
            for v1 in self.meta_data_list:
                if v1:
                    v1.validate()

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        result['MetaDataList'] = []
        if self.meta_data_list is not None:
            for k1 in self.meta_data_list:
                result['MetaDataList'].append(k1.to_map() if k1 else None)

        if self.skill_path is not None:
            result['SkillPath'] = self.skill_path

        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        self.meta_data_list = []
        if m.get('MetaDataList') is not None:
            for k1 in m.get('MetaDataList'):
                temp_model = main_models.GetSkillMetaDataResponseBodyDataMetaDataList()
                self.meta_data_list.append(temp_model.from_map(k1))

        if m.get('SkillPath') is not None:
            self.skill_path = m.get('SkillPath')

        return self


class GetSkillMetaDataResponseBodyDataMetaDataList(DaraModel):
    def __init__(
        self,
        description: Optional[str] = None,
        name: Optional[str] = None,
    ):
        self.description = description
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.description is not None:
            result['Description'] = self.description

        if self.name is not None:
            result['Name'] = self.name

        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get('Description') is not None:
            self.description = m.get('Description')

        if m.get('Name') is not None:
            self.name = m.get('Name')

        return self
