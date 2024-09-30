"""
Script for running inference for task 1: CoW multiclass segmentation.
Inference.py serves as the entrypoint for the docker container.

NOTE: You don't need to change anything in this script!
All your code should be in your_algorithm.py.

If you use this template you can simply replace the `your_segmentation_algorithm` function
in your_algorithm.py with your own algorithm.

The relevant paths are as follows:
    input_path: contains the input images inside the folders
    /images/head-mr-angio or /images/head-ct-angio
        Docker: /input
        Local: ./test/input
    output_path: output predictions are stored inside the folder
    /images/cow-multiclass-segmentation
        Docker: /output
        Local: ./test/output
    resource_path: any additional resources needed for the algorithm during
    inference can be stored here (optional)
        Docker: ./resources
        Local: ./resources

Before submitting to grand-challenge.org, you must ensure that your algorithm
runs in the docker container. To do this, run
  ./test_run.sh
This will start the inference and reads from ./test/input and outputs to ./test/output

To save the container and prep it for upload to Grand-Challenge.org you can call:
  ./save.sh
"""

from glob import glob
from pathlib import Path

import numpy as np
import SimpleITK as sitk
from your_algorithm import TRACK, your_segmentation_algorithm

# NOTE: uncomment the next line if you use pytorch
# from torch_utilities import _show_torch_cuda_info


def run():
    # Setting correct paths for input, output and resources
    # depending on whether the algorithm is run in a docker container or locally
    if _is_docker():
        input_path = Path("/input")
        output_path = Path("/output")
    else:
        input_path = Path("./test/input")
        output_path = Path("./test/output")

    # Read the input
    # Gives a npy array with shape (x,y,z)
    input_head_mr_angiography = load_image_file_as_array(
        location=input_path / "images/head-mr-angio",
    )
    input_head_ct_angiography = load_image_file_as_array(
        location=input_path / "images/head-ct-angio",
    )

    # Check whether torch CUDA is available

    # NOTE: This relies on torch being installed in the environment
    # _show_torch_cuda_info()

    # Run your prediction algorithm
    print("Running prediction algorithm...")
    pred_array = your_segmentation_algorithm(
        mr_input_array=input_head_mr_angiography,
        ct_input_array=input_head_ct_angiography,
    )

    # Save your output
    print("Saving output...")
    write_array_as_image_file(
        array=pred_array, input_folder=input_path, output_folder=output_path
    )
    print("Done!")
    return 0


def load_image_file(*, input_path):
    # Use SimpleITK to read a file
    input_file = (glob(str(input_path / "*.mha")) + glob(str(input_path / "*.nii.gz")))[
        0
    ]  # There is just one file in the input folder!
    return sitk.ReadImage(input_file)


def load_image_file_as_array(*, location):
    img = load_image_file(input_path=location)

    # Convert it to a Numpy array

    # NOTE: SimpleITK npy axis ordering is (z,y,x)!
    img_array = sitk.GetArrayFromImage(img)

    # reorder from (z,y,x) to (x,y,z)
    img_array = img_array.transpose((2, 1, 0))

    return img_array


def write_array_as_image_file(*, array, input_folder, output_folder):
    # Checking for correct shape of prediction array.

    # NOTE: Your output prediction must have the same shape
    # as the input image of the chosen track!
    required_output_shape = tuple()
    input_img = sitk.Image
    if TRACK == "MR":
        input_img = load_image_file(input_path=input_folder / "images/head-mr-angio")
    elif TRACK == "CT":
        input_img = load_image_file(input_path=input_folder / "images/head-ct-angio")

    required_output_shape = input_img.GetSize()
    assert (
        array.shape == required_output_shape
    ), "Prediction output must have the same shape as the input image!"

    # Create the output folder
    output_location = output_folder / "images/cow-multiclass-segmentation"
    output_location.mkdir(parents=True, exist_ok=True)

    suffix = ".mha"

    # Reorder array from (x,y,z) to (z,y,x) before using sitk.GetImageFromArray
    array = array.transpose((2, 1, 0)).astype(np.uint8)

    # Converting prediction array back to SimpleITK
    # copying the metadata from the original image
    seg_mask = sitk.GetImageFromArray(array.astype(np.uint8))

    # Copies the Origin, Spacing, and Direction from the source image
    seg_mask.CopyInformation(input_img)

    sitk.WriteImage(
        seg_mask,
        output_location / f"output{suffix}",
        useCompression=True,
    )


def _is_docker():
    """
    check if process.py is run in a docker env
        bash test.sh vs python3 process.py

    from https://stackoverflow.com/questions/43878953/how-does-one-detect-if-one-is-running-within-a-docker-container-within-python
    """
    cgroup = Path("/proc/self/cgroup")
    exec_in_docker = (
        Path("/.dockerenv").is_file()
        or cgroup.is_file()
        and "docker" in cgroup.read_text()
    )
    print(f"exec_in_docker? {exec_in_docker}")
    return exec_in_docker


if __name__ == "__main__":
    raise SystemExit(run())
