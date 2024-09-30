"""
Script for running inference for task 2: CoW detection/localization.
Inference.py serves as the entrypoint for the docker container.

NOTE: You don't need to change anything in this script!
All your code should be in your_algorithm.py.

If you use this template you can simply replace the `your_detection_algorithm` function
in your_algorithm.py with your own algorithm.

The relevant paths are as follows:
    input_path: contains the input images inside the folders
    /images/head-mr-angio or /images/head-ct-angio
        Docker: /input
        Local: ./test/input
    output_path: output predictions are stored as cow-roi.json
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

import json
from glob import glob
from pathlib import Path

import SimpleITK as sitk
from your_algorithm import your_detection_algorithm


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
    pred_dict = your_detection_algorithm(
        mr_input_array=input_head_mr_angiography,
        ct_input_array=input_head_ct_angiography,
    )

    # Save your output
    print("Saving output...")
    write_json_file(content=pred_dict, output_folder=output_path)
    print("Done!")

    return 0


def write_json_file(*, content, output_folder):
    # Make some sanity checks!
    assert type(content) is dict, "Content must be a dictionary!"
    assert content.keys() == {
        "size",
        "location",
    }, "Content must contain only 'size' and 'location' keys!"
    assert (
        type(content["size"]) is list and type(content["location"]) is list
    ), "Size and location must be lists!"
    assert (
        len(content["size"]) == 3 and len(content["location"]) == 3
    ), "Size and location must be lists of 3 integers!"
    assert all(
        [type(i) is int for i in content["size"] + content["location"]]
    ), "Size and location must be lists of integers!"

    # Writes a json file
    location = output_folder / "cow-roi.json"
    with open(location, "w") as f:
        f.write(json.dumps(content, indent=4))


def load_image_file_as_array(*, location):
    # Use SimpleITK to read a file
    input_file = (glob(str(location / "*.mha")) + glob(str(location / "*.nii.gz")))[
        0
    ]  # There is just one file in the input folder!
    img = sitk.ReadImage(input_file)

    # Convert it to a Numpy array

    # NOTE: SimpleITK npy axis ordering is (z,y,x)!
    img_array = sitk.GetArrayFromImage(img)

    # reorder from (z,y,x) to (x,y,z)
    img_array = img_array.transpose((2, 1, 0))

    return img_array


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
