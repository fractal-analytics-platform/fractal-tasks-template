from pathlib import Path

import pytest
from ngio import create_synthetic_ome_zarr, open_ome_zarr_container

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

    result = gaussian_blur_task(
        zarr_url=str(test_data_path), sigma_xy=1.0, sigma_z=None, overwrite=False
    )
    assert result is not None
    output_image_url = result["image_list_updates"][0]["zarr_url"]
    assert Path(output_image_url).exists()
    ome_zarr = open_ome_zarr_container(test_data_path)
    image = ome_zarr.get_image()
    assert image.shape == shape
    # DISCLAIMER: This is only a very basic test.
    # More comprehensive tests should be implemented based on the expected
    # results not only the presence of a blurred image.


def test_gaussian_blur_task_overwrite(tmp_path: Path):
    test_data_path = tmp_path / "data.zarr"

    create_synthetic_ome_zarr(
        store=test_data_path,
        shape=(64, 64),
        overwrite=False,
        axes_names="yx",
    )

    # First run to create the blurred image
    result1 = gaussian_blur_task(
        zarr_url=str(test_data_path), sigma_xy=1.0, sigma_z=None, overwrite=False
    )
    assert result1 is not None
    output_image_url1 = result1["image_list_updates"][0]["zarr_url"]
    assert Path(output_image_url1).exists()

    # Second run with overwrite=True should succeed
    result2 = gaussian_blur_task(
        zarr_url=str(test_data_path), sigma_xy=2.0, sigma_z=None, overwrite=True
    )
    assert result2 is not None
    output_image_url2 = result2["image_list_updates"][0]["zarr_url"]
    assert Path(output_image_url2).exists()
    assert output_image_url1 == output_image_url2

    # Third run with overwrite=False should raise an error
    with pytest.raises(FileExistsError):
        gaussian_blur_task(
            zarr_url=str(test_data_path), sigma_xy=3.0, sigma_z=None, overwrite=False
        )

    # Forth run with overwrite_input=True should overwrite the original image
    result_none = gaussian_blur_task(
        zarr_url=str(test_data_path), sigma_xy=1.0, sigma_z=None, overwrite_input=True
    )
    assert result_none is None
