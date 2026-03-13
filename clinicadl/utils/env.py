import os
import subprocess
from pathlib import Path


def export_conda_environment(destination: str | Path) -> None:
    """
    Exports the current Conda environment to a YAML file.

    Parameters
    ----------
    destination : str | Path
        The path where the environment YAML file will be saved.
    """
    _check_conda_env()

    subprocess.run(
        ["conda", "env", "export", "--no-builds", "--file", str(destination)],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def compare_conda_environments(ref_env_file: Path) -> None:
    _check_conda_env()

    result = subprocess.run(
        ["conda", "compare", str(ref_env_file)],
        check=True,
        capture_output=True,
    )

    if "Success." not in result.stdout.decode():
        raise RuntimeError(
            f"Current Conda environment does not match reference environment in {ref_env_file}\n:{result.stdout.decode()}"
        )


def _check_conda_env() -> None:
    """
    Checks if the current environment is a Conda environment.
    """
    if not ("CONDA_DEFAULT_ENV" in os.environ or "CONDA_PREFIX" in os.environ):
        raise RuntimeError(
            "Please run ClinicaDL inside a Conda environment (see installation guide in https://clinicadl.readthedocs.io)"
        )
