"""This is the Python module for my_task."""

import logging
import os
import pathlib
import shutil
from typing import Optional

from dask import array as da
from ngio import open_ome_zarr_container
from ngio.experimental.iterators import ImageProcessingIterator
from pydantic import validate_call
from scipy.ndimage import gaussian_filter


def compute_gaussian_blur(image: da.Array, sigma: tuple[float, ...]) -> da.Array:
    """Apply Gaussian blur to a Dask array image.

    Args:
        image (da.Array): Input image as a Dask array.
        sigma (tuple[float, ...]): Standard deviation for Gaussian kernel.

    Returns:
        da.Array: Blurred image as a Dask array.
    """

    # Apply Gaussian filter to each chunk
    def apply_gaussian(chunk):
        return gaussian_filter(chunk, sigma=sigma)

    assert image.ndim in (3, 4), "Image must be 2D or 3D (+channel)"
    assert len(sigma) == image.ndim, "Sigma must match image dimensions"
    # This will itroduce some edge artifacts at chunk boundaries
    # In a real application, consider using map_overlap to mitigate this
    # With appropriate depth based on sigma
    blurred_image = image.map_blocks(apply_gaussian, dtype=image.dtype)
    return blurred_image


@validate_call
def gaussian_blur_task(
    *,
    # Fractal managed parameters
    zarr_url: str,
    # Input parameters
    output_image_suffix: str = "gaussian_blur",
    sigma_xy: float = 1.0,
    sigma_z: Optional[float] = None,
    overwrite: bool = True,
    overwrite_input: bool = False,
) -> dict | None:
    """Apply a Gaussian blur to the input image and save the result as a OME-Zarr image.

    Args:
        zarr_url (str): URL to the OME-Zarr container.
        output_image_suffix (str): Suffix for the output image name.
        sigma_xy (float): Standard deviation for Gaussian kernel in the XY plane.
            Defaults to 1.0.
        sigma_z (Optional[float]): Standard deviation for Gaussian kernel
            in the Z direction. If None, the smoothing will be applied only in XY.
        overwrite (bool): Whether to overwrite an existing output image.
            Defaults to True.
        overwrite_input (bool): If True, the task will first create a new
            OME-Zarr image with the Gaussian blur applied, and then overwrite
            the original image with the new one. Defaults to False.
    """
    logging.info(f"{zarr_url=}")

    # Open the OME-Zarr container
    ome_zarr = open_ome_zarr_container(zarr_url)
    logging.info(f"{ome_zarr=}")

    zarr_path = pathlib.Path(zarr_url)
    zarr_dir, image_name = zarr_path.parent, zarr_path.stem
    logging.info(f"Input image name: {image_name}")

    output_image_suffix = (
        output_image_suffix.strip().lstrip().rstrip().replace(" ", "_")
    )
    output_image_name = f"{image_name}_{output_image_suffix}{zarr_path.suffix}"
    logging.info(f"New image name: {output_image_name}")

    output_zarr_path = zarr_dir / output_image_name
    output_ome_zarr = ome_zarr.derive_image(
        store=output_zarr_path,
        name=output_image_name,
        overwrite=overwrite,
    )
    logging.info(f"New OME-Zarr created at {output_zarr_path=}")
    input_image = ome_zarr.get_image()
    output_image = output_ome_zarr.get_image()

    if sigma_z is None:
        # If sigma_z is not provided, apply 2D Gaussian blur
        axes_order = "cyx"
        sigma = (0, sigma_xy, sigma_xy)
    else:
        # If sigma_z is provided, apply 3D Gaussian blur
        axes_order = "czyx"
        sigma = (0, sigma_z, sigma_xy, sigma_xy)

    logging.info(f"Running Gaussian blur with sigma={sigma} on axes {axes_order}")
    iterator = ImageProcessingIterator(
        input_image=input_image, output_image=output_image, axes_order=axes_order
    )

    if sigma_z is None:
        iterator = iterator.by_yx()
        logging.info("Iterator set to by_yx() for 2D Gaussian blur")
    else:
        # Set iterator to process by ZYX volumes for 3D Gaussian blur
        # all other axes are broadcasted
        # Strict=False means that if there no z axis or z is size 1, it will still work
        # If your processing needs requires a volume, use strict=True
        iterator = iterator.by_zyx(strict=False)
        logging.info("Iterator set to by_zyx() for 3D Gaussian blur")

    # If you would like to iterate over arbitrary region of interests (ROIs),
    # you can uncomment the following line and provide the ROIs
    # table = ome_zarr.get_generic_roi_table(name="my_roi_table")
    # iterator = iterator.product(table)
    #
    # Core processing loop
    #
    for input_data, writer in iterator.iter_as_dask():
        blurred_data = compute_gaussian_blur(input_data, sigma=sigma)
        writer(blurred_data)

    # No need to call output_image.consolidate()
    # ImageProcessingIterator handles this
    logging.info("Gaussian blur processing complete.")

    if overwrite_input:
        logging.info("Replace original zarr image with the newly created Zarr image")
        backup_path = zarr_path.parent / f"{zarr_path.stem}_backup{zarr_path.suffix}"
        os.rename(zarr_path, backup_path)
        os.rename(output_zarr_path, zarr_path)
        shutil.rmtree(f"{backup_path}", ignore_errors=False)
        # If we are overwriting the input, there is no need to update the image list
        return None

    image_list_update_dict = {
        "image_list_updates": [{"zarr_url": str(output_zarr_path), "origin": zarr_url}]
    }
    return image_list_update_dict


if __name__ == "__main__":
    from fractal_task_tools.task_wrapper import run_fractal_task

    run_fractal_task(task_function=gaussian_blur_task)
