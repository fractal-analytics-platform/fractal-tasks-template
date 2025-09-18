from pathlib import Path

import pytest
from ngio import create_synthetic_ome_zarr

from fractal_tasks_template.gaussian_blur_task import (
    gaussian_blur_task,
)


@pytest.mark.parametrize(
    "shape, axes",
    [
        ((64, 64), "yx"),
        ((1, 64, 64), "cyx"),
        ((3, 64, 64), "cyx"),
        ((4, 64, 64), "tyx"),
        ((1, 64, 64), "zyx"),
        ((1, 1, 64, 64), "czyx"),
        ((1, 10, 64, 64), "czyx"),
        ((1, 1, 64, 64), "tzyx"),
        ((1, 3, 64, 64), "tcyx"),
        ((1, 1, 10, 64, 64), "tczyx"),
    ],
)
def test_gaussian_blur_task(tmp_path: Path, shape: tuple[int, ...], axes: str):
    test_data_path = tmp_path / "data.zarr"

    create_synthetic_ome_zarr(
        store=test_data_path,
        shape=shape,
        overwrite=False,
        axes_names=axes,
    )
    gaussian_blur_task(
        zarr_url=str(test_data_path), sigma_xy=1.0, sigma_z=None, overwrite=False
    )
