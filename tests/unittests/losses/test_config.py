import pytest
from pydantic import ValidationError


def test_LossConfig():
    from clinicadl.losses import LossConfig

    LossConfig(reduction="none", p=2, weight=[0.1, 0.1, 0.8])
    LossConfig(
        loss="SmoothL1Loss", margin=10.0, delta=2.0, beta=3.0, label_smoothing=0.5
    )
    with pytest.raises(ValueError):
        LossConfig(loss="abc")
    with pytest.raises(ValueError):
        LossConfig(weight=[0.1, -0.1, 0.8])
    with pytest.raises(ValidationError):
        LossConfig(label_smoothing=1.1)
