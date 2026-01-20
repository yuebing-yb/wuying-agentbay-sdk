import pytest


def test_create_session_params_accepts_beta_volume_parameter():
    from agentbay import CreateSessionParams

    params = CreateSessionParams(beta_volume="vol-test")
    assert getattr(params, "beta_volume") == "vol-test"
    assert not hasattr(params, "volume")


def test_create_session_params_rejects_volume_parameter():
    from agentbay import CreateSessionParams

    with pytest.raises(TypeError):
        CreateSessionParams(volume="vol-test")

