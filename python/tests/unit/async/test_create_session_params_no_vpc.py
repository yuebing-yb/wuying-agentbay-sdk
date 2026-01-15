import pytest


def test_create_session_params_rejects_is_vpc_parameter():
    from agentbay import CreateSessionParams

    with pytest.raises(TypeError):
        CreateSessionParams(is_vpc=True)

