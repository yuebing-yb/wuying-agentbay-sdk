# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import Optional

from darabonba.model import DaraModel


class GetSkillMetaDataShrinkRequest(DaraModel):
    def __init__(
        self,
        authorization: Optional[str] = None,
        image_id: Optional[str] = None,
        skill_group_ids_shrink: Optional[str] = None,
    ):
        self.authorization = authorization
        self.image_id = image_id
        self.skill_group_ids_shrink = skill_group_ids_shrink

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

        if self.skill_group_ids_shrink is not None:
            result['SkillGroupIds'] = self.skill_group_ids_shrink

        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get('Authorization') is not None:
            self.authorization = m.get('Authorization')

        if m.get('ImageId') is not None:
            self.image_id = m.get('ImageId')

        if m.get('SkillGroupIds') is not None:
            self.skill_group_ids_shrink = m.get('SkillGroupIds')

        return self
