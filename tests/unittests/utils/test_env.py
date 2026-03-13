import subprocess
from unittest import mock

import pytest

from clinicadl.utils.env import export_conda_environment


def test_export_conda_environment_in_non_conda_env(monkeypatch):
    monkeypatch.delenv("CONDA_DEFAULT_ENV", raising=False)
    monkeypatch.delenv("CONDA_PREFIX", raising=False)

    with pytest.raises(
        RuntimeError, match="Please run ClinicaDL inside a Conda environment"
    ):
        export_conda_environment("env.yml")


@mock.patch("subprocess.run")
def test_export_conda_environment_in_conda_env(mock_run, monkeypatch):
    monkeypatch.setenv("CONDA_PREFIX", "/fake/conda")
    export_conda_environment("env.yml")
    mock_run.assert_called_once_with(
        ["conda", "env", "export", "--no-builds", "--file", "env.yml"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
