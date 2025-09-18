"""This is the Python module for my_task."""

import logging

import numpy as np
import pandas as pd
from ngio import Roi, open_ome_zarr_container
from ngio.experimental.iterators import FeatureExtractorIterator
from ngio.tables import FeatureTable
from pydantic import validate_call
from skimage import measure


def region_props_features_func(image: np.ndarray, label: np.ndarray, roi: Roi) -> dict:
    """Extract region properties features from a label image within a ROI."""
    assert image.ndim in (3, 4), "Image must be 4D yxzc or 3D yxz"
    assert image.ndim == label.ndim, (
        "Image and label must have the same number of dimensions"
    )
    assert label.shape[-1] == 1, "Label image must have a single channel"
    label = label[..., 0]  # Remove channel dimension
    props = measure.regionprops_table(
        label,
        intensity_image=image,
        properties=[
            "label",
            "area",
            "area_bbox",
            "axis_major_length",
            "axis_minor_length",
            "solidity",
            "mean_intensity",
            "max_intensity",
            "min_intensity",
            "std_intensity",
        ],
    )
    num_regions = len(props["label"])
    props["region"] = [roi.get_name()] * num_regions
    props["time"] = [roi.t] * num_regions
    return props


def join_tables(
    tables: list[dict[str, list]], index_key: str = "label"
) -> pd.DataFrame:
    """Join a list of tables (dictionaries) into a single DataFrame."""
    assert len(tables) >= 1, "At least one table is required"
    out_dict = {}
    for table in tables:
        for key, value in table.items():
            if key not in out_dict:
                out_dict[key] = []
            out_dict[key].extend(value)

    df = pd.DataFrame(out_dict)
    df = df.set_index(index_key)
    return df


@validate_call
def region_props_features_task(
    *,
    # Fractal managed parameters
    zarr_url: str,
    # Input parameters
    label_image_name: str,
    output_table_name: str = "region_props_features",
    overwrite: bool = True,
) -> None:
    """Extract region properties features from the input image.

    Args:
        zarr_url (str): URL to the OME-Zarr container
        label_image_name (str): Name of the label image to analyze.
        output_table_name (str): Name for the output feature table.
        overwrite (bool): Whether to overwrite an existing feature table.
            Defaults to True.
    """
    # Use the first of input_paths
    logging.info(f"{zarr_url=}")

    # Open the OME-Zarr container
    ome_zarr = open_ome_zarr_container(zarr_url)
    logging.info(f"{ome_zarr=}")

    # Get the label image at the highest resolution available
    label_image = ome_zarr.get_label(name=label_image_name)

    # This will raise an error if no image matches the pixel size of the label image
    image = ome_zarr.get_image(pixel_size=label_image.pixel_size, strict=True)
    logging.info(f"{image=}")
    logging.info(f"{label_image=}")

    if not overwrite and output_table_name in ome_zarr.list_tables():
        raise FileExistsError(
            f"Table {output_table_name} already exists. "
            "Set overwrite=True to overwrite it."
        )

    # Some of the features in regionprops fail if the image is has singleton on z
    axes_order = "yxc" if image.is_2d else "yxzc"
    # Create an iterator to process the image and extract features
    iterator = FeatureExtractorIterator(
        input_image=image,
        input_label=label_image,
        axes_order=axes_order,
    )
    iterator = iterator.by_zyx(strict=False)

    tables = []
    for input_data, label_data, roi in iterator.iter_as_numpy():
        _table_dict = region_props_features_func(
            image=input_data,
            label=label_data,
            roi=roi,
        )
        tables.append(_table_dict)

    # Convert the tables to a DataFrame
    # Save the DataFrame as a table in the OME-Zarr container
    feature_df = join_tables(tables, index_key="label")
    feature_table = FeatureTable(
        table_data=feature_df, reference_label=label_image_name
    )
    ome_zarr.add_table(name=output_table_name, table=feature_table, overwrite=overwrite)
    logging.info(f"Feature table {output_table_name} added to OME-Zarr container.")
    return None


if __name__ == "__main__":
    from fractal_task_tools.task_wrapper import run_fractal_task

    run_fractal_task(task_function=region_props_features_task)
