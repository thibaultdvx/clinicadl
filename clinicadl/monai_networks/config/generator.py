from typing import Optional, Sequence, Union

from pydantic import PositiveInt, computed_field

from clinicadl.utils.factories import DefaultFromLibrary

from .base import ImplementedNetworks, NetworkConfig
from .conv_decoder import ConvDecoderOptions
from .mlp import MLPOptions


class GeneratorConfig(NetworkConfig):
    """Config class for Generator."""

    in_shape: Sequence[PositiveInt]
    num_outputs: PositiveInt
    conv_args: ConvDecoderOptions
    mlp_args: Union[Optional[MLPOptions], DefaultFromLibrary] = DefaultFromLibrary.YES

    @computed_field
    @property
    def network(self) -> ImplementedNetworks:
        """The name of the network."""
        return ImplementedNetworks.GENERATOR
