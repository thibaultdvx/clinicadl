"""
Automatically reject images incorrectly preprocessed pet-linear (Unified Segmentation) with ? criterion


"""

from logging import getLogger
from pathlib import Path
from typing import Optional, Union

import nibabel as nib
import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from clinicadl.utils.clinica_utils import (
    RemoteFileStructure,
    clinicadl_file_reader,
    fetch_file,
    get_subject_session_list,
    pet_linear_nii,
)
from clinicadl.utils.enum import SUVRReferenceRegions, Tracer

from .utils import get_metric


def quality_check(
    caps_dir: Path,
    output_tsv: Path,
    tracer: Union[Tracer, str],
    ref_region: Union[SUVRReferenceRegions, str],
    use_uncropped_image: bool,
    participants_tsv: Optional[Path],
    threshold: float = 0.8,
    n_proc: int = 1,
):
    """
    Performs quality check on pet-linear pipeline.

    Parameters
    ----------

    caps_directory: str (Path)
        The CAPS folder where pet-linear outputs are stored.
    output_tsv: str (Path)
        The path to TSV output file.
    tracer: str
        The label given to the PET acquisition, specifying the tracer used (trc-<tracer>).
    ref_region: str
        The reference region used to perform intensity normalization {pons|cerebellumPons|pons2|cerebellumPons2}.
    use_uncropped_image: bool
        Use the uncropped image instead of the cropped image generated by t1-linear or pet-linear.
    participants_tsv: str (Path)
        Path to a TSV file including a list of participants/sessions on which the quality-check will be performed.
    threshold: float
        The threshold on the output probability to decide if the image passed or failed.
        Default is 0.8
    n_proc: int
        Number of cores used during the task.
    """
    logger = getLogger("clinicadl.quality_check")

    tracer = Tracer(tracer)
    ref_region = SUVRReferenceRegions(ref_region)

    if Path(output_tsv).is_file():
        raise NameError("this file already exists please chose another name")

    # load the contour mask
    home = Path.home()
    cache_clinicadl = home / ".cache" / "clinicadl" / "mask"
    if not cache_clinicadl.is_dir():
        cache_clinicadl.mkdir(parents=True)

    mask_contour_file = cache_clinicadl / "qc_pet_mask_contour.nii.gz"

    if not (mask_contour_file).is_file():
        try:
            url_aramis = "https://aramislab.paris.inria.fr/files/data/masks/"
            FILE1 = RemoteFileStructure(
                filename="qc_pet_mask_contour.nii.gz",
                url=url_aramis,
                checksum="0c561ce7de343219e42861b87a359420f9d485da37a8f64d1366ee9bb5460ee6",
            )
            mask_contour_file = fetch_file(FILE1, cache_clinicadl)
        except IOError as err:
            raise IOError("Unable to download required MNI file for QC: ", err)

    mask_contour_nii = nib.loadsave.load(mask_contour_file)
    mask_contour = mask_contour_nii.get_fdata()
    mask_contour.astype(int)

    nb_one_inside = np.sum(mask_contour)  # 1605780

    columns = [
        "participant_id",
        "session_id",
        "pass_probability",
        "pass",
    ]

    results_df = pd.DataFrame(columns=columns)
    subjects, sessions = get_subject_session_list(
        caps_dir, participants_tsv, False, False, None
    )
    file_type = pet_linear_nii(
        tracer,
        ref_region,
        use_uncropped_image,
    )
    input_files = clinicadl_file_reader(subjects, sessions, caps_dir, file_type)[0]

    def write_output_data(file):
        file = Path(file)

        if file.is_file():
            image_nii = nib.loadsave.load(file)
            image_np = image_nii.get_fdata()
        else:
            raise FileNotFoundError(f"Clinical data not found ({file})")

        sum_contour = get_metric(mask_contour, image_np, nb_one_inside)

        session = file.parent.parent
        subject = session.parent
        row = [
            [
                subject.name,
                session.name,
                sum_contour,
                sum_contour > threshold,
            ]
        ]
        row_df = pd.DataFrame(row, columns=columns)

        return row_df

    results_df = Parallel(n_jobs=n_proc)(
        delayed(write_output_data)(file) for file in input_files
    )

    all_df = pd.DataFrame(columns=columns)
    for subject_df in results_df:
        all_df = pd.concat([all_df, subject_df])
    all_df.sort_values("pass_probability", inplace=True)
    all_df.to_csv(output_tsv, sep="\t", index=False)

    logger.info(
        f"Quality check metrics extracted at {Path(output_tsv) / 'QC_metrics.tsv'}."
    )
