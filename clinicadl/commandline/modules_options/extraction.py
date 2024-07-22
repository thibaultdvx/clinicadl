import click

from clinicadl.caps_dataset.extraction.config import (
    ExtractionConfig,
    ExtractionImageConfig,
    ExtractionPatchConfig,
    ExtractionROIConfig,
    ExtractionSliceConfig,
)
from clinicadl.config.config_utils import get_default_from_config_class as get_default
from clinicadl.config.config_utils import get_type_from_config_class as get_type

extract_json = click.option(
    "-ej",
    "--extract_json",
    type=get_type("extract_json", ExtractionConfig),
    default=get_default("extract_json", ExtractionConfig),
    help="Name of the JSON file created to describe the tensor extraction. "
    "Default will use format extract_{time_stamp}.json",
)


save_features = click.option(
    "--save_features",
    is_flag=True,
    help="""Extract the selected mode to save the tensor. By default, the pipeline only save images and the mode extraction
            is done when images are loaded in the train.""",
)

patch_size = click.option(
    "-ps",
    "--patch_size",
    type=get_type("patch_size", ExtractionPatchConfig),
    default=get_default("patch_size", ExtractionPatchConfig),
    show_default=True,
    help="Patch size.",
)
stride_size = click.option(
    "-ss",
    "--stride_size",
    type=get_type("stride_size", ExtractionPatchConfig),
    default=get_default("stride_size", ExtractionPatchConfig),
    show_default=True,
    help="Stride size.",
)


slice_direction = click.option(
    "-sd",
    "--slice_direction",
    type=get_type("slice_direction", ExtractionSliceConfig),
    default=get_default("slice_direction", ExtractionSliceConfig),
    show_default=True,
    help="Slice direction. 0: Sagittal plane, 1: Coronal plane, 2: Axial plane.",
)
slice_mode = click.option(
    "-sm",
    "--slice_mode",
    type=get_type("slice_mode", ExtractionSliceConfig),
    default=get_default("slice_mode", ExtractionSliceConfig),
    show_default=True,
    help=(
        "rgb: Save the slice in three identical channels, "
        "single: Save the slice in a single channel."
    ),
)
discarded_slices = click.option(
    "-ds",
    "--discarded_slices",
    type=get_type("discarded_slices", ExtractionSliceConfig),
    default=get_default("discarded_slices", ExtractionSliceConfig),
    multiple=2,
    help="""Number of slices discarded from respectively the beginning and
        the end of the MRI volume.  If only one argument is given, it will be
        used for both sides.""",
)
roi_list = click.option(
    "--roi_list",
    type=get_type("roi_list", ExtractionROIConfig),
    default=get_default("roi_list", ExtractionROIConfig),
    required=True,
    multiple=True,
    help="List of regions to be extracted",
)
roi_uncrop_output = click.option(
    "--roi_uncrop_output",
    type=get_type("roi_uncrop_output", ExtractionROIConfig),
    default=get_default("roi_uncrop_output", ExtractionROIConfig),
    is_flag=True,
    help="Disable cropping option so the output tensors "
    "have the same size than the whole image.",
)
roi_custom_template = click.option(
    "--roi_custom_template",
    "-ct",
    type=get_type("roi_custom_template", ExtractionROIConfig),
    default=get_default("roi_custom_template", ExtractionROIConfig),
    help="""Template name if MODALITY is `custom`.
        Name of the template used for registration during the preprocessing procedure.""",
)
roi_custom_mask_pattern = click.option(
    "--roi_custom_mask_pattern",
    "-cmp",
    type=get_type("roi_custom_mask_pattern", ExtractionROIConfig),
    default=get_default("roi_custom_mask_pattern", ExtractionROIConfig),
    help="""Mask pattern if MODALITY is `custom`.
            If given will select only the masks containing the string given.
            The mask with the shortest name is taken.""",
)
