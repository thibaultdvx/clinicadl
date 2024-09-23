from torch import Tensor
from torch.nn import BCEWithLogitsLoss, MultiMarginLoss

from clinicadl.losses import ImplementedLoss, create_loss_config, get_loss_function


def test_get_loss_function():
    for loss in ImplementedLoss:
        config = create_loss_config(loss=loss)()
        _ = get_loss_function(config)

    config = create_loss_config("MultiMarginLoss")(
        reduction="sum", weight=[1, 2, 3], p=2
    )
    loss, updated_config = get_loss_function(config)
    assert isinstance(loss, MultiMarginLoss)
    assert loss.reduction == "sum"
    assert loss.p == 2
    assert loss.margin == 1.0
    assert (loss.weight == Tensor([1, 2, 3])).all()

    assert updated_config.loss == "MultiMarginLoss"
    assert updated_config.reduction == "sum"
    assert updated_config.p == 2
    assert updated_config.margin == 1.0
    assert updated_config.weight == [1, 2, 3]

    config = create_loss_config("BCEWithLogitsLoss")(pos_weight=[1, 2, 3])
    loss, updated_config = get_loss_function(config)
    assert isinstance(loss, BCEWithLogitsLoss)
    assert (loss.pos_weight == Tensor([1, 2, 3])).all()
    assert updated_config.pos_weight == [1, 2, 3]
