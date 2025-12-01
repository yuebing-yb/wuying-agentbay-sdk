# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from darabonba.model import DaraModel


class ListContextsRequest(DaraModel):
    def __init__(
        self,
        authorization: str = None,
        max_results: int = None,
        next_token: str = None,
        login_region_id: str = None,
    ):
        self.authorization = authorization
        self.max_results = max_results
        self.next_token = next_token
        self.login_region_id = login_region_id

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.authorization is not None:
            result["Authorization"] = self.authorization

        if self.max_results is not None:
            result["MaxResults"] = self.max_results

        if self.next_token is not None:
            result["NextToken"] = self.next_token

        if self.login_region_id is not None:
            result["LoginRegionId"] = self.login_region_id

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get("Authorization") is not None:
            self.authorization = m.get("Authorization")

        if m.get("MaxResults") is not None:
            self.max_results = m.get("MaxResults")

        if m.get("NextToken") is not None:
            self.next_token = m.get("NextToken")

        if m.get("LoginRegionId") is not None:
            self.login_region_id = m.get("LoginRegionId")

        return self
