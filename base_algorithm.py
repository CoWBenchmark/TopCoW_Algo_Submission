import logging
import os
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Pattern

import numpy as np
import SimpleITK as sitk

# evalutils provides methods to wrap your algorithm in Docker containers
# and util functions like evalutils.validators for validators that you can use etc.
from evalutils import SegmentationAlgorithm
from evalutils.exceptions import FileLoaderError, ValidationError
from evalutils.io import ImageLoader
from evalutils.validators import DataFrameValidator
from pandas import DataFrame

logger = logging.getLogger(__name__)


class TRACK(Enum):
    MR = "mr"
    CT = "ct"


class TASK(Enum):
    BINARY_SEGMENTATION = "bin_seg"
    MULTICLASS_SEGMENTATION = "mul_seg"


class CoWSegNumImgsEqualValidator(DataFrameValidator):
    """
    inherits DataFrameValidator from evalutils

    Validates that the number of CT and MR images is equal
    """

    def validate(self, *, df: DataFrame):
        try:
            path_ct = df["path_ct"].tolist()
            path_mr = df["path_mr"].tolist()
        except KeyError:
            raise ValidationError(
                "Column `path_ct` or `path_mr` not found in DataFrame."
            )

        assert len(path_ct) == len(
            path_mr
        ), "The number of CT and MR images is not equal."


class BaseAlgorithm(SegmentationAlgorithm):
    """
    inherits SegmentationAlgorithm class from evalutils.
    NOTE: we overwrite the default input, saving path with:
            input_path=INPUT_PATH,
            output_path=OUTPUT_PATH,
            output_file=OUTPUT_FILE,
    NOTE these are modified according to your chosen track and task AUTOMATICALLY!

    We extend SegmentationAlgorithm by
        - providing custom input/output interface paths
        - having our own validators
        - modifying components called by process function

    class MyCoWSegAlgorithm(BaseAlgorithm) will need to read the following input:

        Head MR Angiography (Image) at /input/images/head-mr-angio/<uuid>.mha
        Head CT Angiography (Image) at /input/images/head-ct-angio/<uuid>.mha

    will also need to write the following output (binary or multi-class):

        Circle of Willis Binary Segmentation (Segmentation) to
            /output/images/cow-binary-segmentation/<uuid>.mha
        Circle of Willis Multiclass Segmentation (Segmentation) to
            /output/images/cow-multiclass-segmentation/<uuid>.mha
    """

    def __init__(self, *, track: Enum, task: Enum):
        self.track = track
        self.task = task
        self.input_image_mr = sitk.Image()
        self.input_image_ct = sitk.Image()
        self.input_image_file_path_ct = Path()
        self.input_image_file_path_mr = Path()
        self.segmentation_path = Path()
        self.segmentation_dict = {}

        assert self.track.value in set(
            item.value for item in TRACK
        ), f"{self.track.value} Invalid track! Must be either 'mr' or 'ct'."
        assert self.task.value in set(
            item.value for item in TASK
        ), f"{self.task.value} Invalid task! Must be either 'bin_seg' or 'mul_seg'"

        print("Track = ", self.track.value)
        print("Task = ", self.task.value)

        if self.task == TASK.MULTICLASS_SEGMENTATION:
            task_output = "multiclass"
        elif self.task == TASK.BINARY_SEGMENTATION:
            task_output = "binary"

        # default path initialization
        # will be updated with your self.track, self.trask
        base_input_path = Path(f"input/images/head-{self.track.value}-angio/")
        base_output_path = Path(f"output/images/cow-{task_output}-segmentation/")
        base_output_file = Path("output/results.json")

        if _is_docker():
            # replace the ./test/ with root / for docker env
            INPUT_PATH = Path("/").joinpath(base_input_path)
            OUTPUT_PATH = Path("/").joinpath(base_output_path)
            OUTPUT_FILE = Path("/").joinpath(base_output_file)
        else:
            INPUT_PATH = Path("./test/").joinpath(base_input_path)
            OUTPUT_PATH = Path("./test/").joinpath(base_output_path)
            OUTPUT_FILE = Path("./test/").joinpath(base_output_file)

        # print(f"INPUT_PATH={INPUT_PATH}")
        print(f"OUTPUT_PATH={OUTPUT_PATH}")
        # print(f"OUTPUT_FILE={OUTPUT_FILE}")

        super().__init__(
            validators=dict(
                input_image=(
                    # CoWSegUniqueImagesValidator(),
                    CoWSegNumImgsEqualValidator(),
                )
            ),
            input_path=INPUT_PATH,
            output_path=OUTPUT_PATH,
            output_file=OUTPUT_FILE,
        )

        # If output_path doesn't exist, create it
        if not os.path.exists(self._output_path):
            print(f"{self._output_path} does not exist, will create it.")
            os.makedirs(self._output_path)

        print("Path at terminal when executing this file")
        print(os.getcwd() + "\n")

        print("BaseAlgorithm __init__ complete!")

    def _load_input_image(self, *, case):
        """
        modified evalutils class Algorithm's
            private _load_input_image() method

        Loading ct and mr image for each case
        """
        print("\n-- call _load_input_image()")
        print(f"\tcase = \n{case}\n")
        input_image_file_path_ct = case["path_ct"]
        input_image_file_path_mr = case["path_mr"]
        print(f"\tinput_image_file_path_ct = \n{input_image_file_path_ct}")
        print(f"\tinput_image_file_path_mr = \n{input_image_file_path_mr}")

        input_image_file_loader = self._file_loaders["input_image"]
        if not isinstance(input_image_file_loader, ImageLoader):
            raise RuntimeError("The used FileLoader was not of subclass ImageLoader")

        # Load the images for this case. Both modalities are always loaded,
        # irrespective of whether they are both used for the prediction
        # NOTE: input_image_ct and input_image_mr are supposed to be SimpleITK.Image
        input_image_ct = input_image_file_loader.load_image(input_image_file_path_ct)
        input_image_mr = input_image_file_loader.load_image(input_image_file_path_mr)

        # Check that it is the expected images
        if input_image_file_loader.hash_image(input_image_ct) != case["hash_ct"]:
            raise RuntimeError("CT image hashes do not match")
        if input_image_file_loader.hash_image(input_image_mr) != case["hash_mr"]:
            raise RuntimeError("MR image hashes do not match")

        self.input_image_ct = input_image_ct
        print("\tinput_image_ct attributes:")
        _sitk_access_attr(input_image_ct)

        self.input_image_mr = input_image_mr
        print("\tinput_image_mr attributes:")
        _sitk_access_attr(input_image_mr)

        self.input_image_file_path_ct = input_image_file_path_ct
        self.input_image_file_path_mr = input_image_file_path_mr

    def _load_cases(
        self,
        *,
        folder: Path,
        file_loader: ImageLoader,
        file_filter: Optional[Pattern[str]] = None,
    ) -> DataFrame:
        """
        modified evalutils class Algorithm's
            private _load_cases() method

        Loading cases. Each case consists of a ct and a mr,
        loaded from the corresponding input directories
        """
        print("\n-- call _load_cases()")
        cases = None

        print(f"\tfolder = {folder}")
        if "mr" in str(folder):
            folder_mr = folder
            folder_ct = Path(str(folder).replace("mr", "ct"))
        elif "ct" in str(folder):
            folder_ct = folder
            folder_mr = Path(str(folder).replace("ct", "mr"))
        else:
            raise ValueError(
                "Incorrect input folder name. Name must either contain 'mr' or 'ct'!"
            )

        # pick the only .mha file in the folder
        path_mr = sorted(folder_mr.glob("*.mha"), key=self._file_sorter_key)
        path_ct = sorted(folder_ct.glob("*.mha"), key=self._file_sorter_key)
        print(f"path_mr = {path_mr}")
        print(f"path_ct = {path_ct}")

        assert (
            len(path_mr) == len(path_ct) == 1
        ), "Only 1 image can be contained in the ct and mr input folders."

        path_mr, path_ct = path_mr[0], path_ct[0]

        if file_filter is None or (
            file_filter.match(str(path_ct)) and file_filter.match(str(path_mr))
        ):
            try:
                case_ct = file_loader.load(fname=path_ct)[0]
                case_mr = file_loader.load(fname=path_mr)[0]
                cases = [
                    {
                        "hash_ct": case_ct["hash"],
                        "path_ct": case_ct["path"],
                        "hash_mr": case_mr["hash"],
                        "path_mr": case_mr["path"],
                    }
                ]
            except FileLoaderError:
                logger.warning(
                    f"Could not load {path_ct.name} or {path_mr.name} using {file_loader}."
                )
        else:
            logger.info(
                f"Skip loading {path_ct.name} and {path_mr.name} because it doesn't match {file_filter}."
            )

        if cases is None or len(cases) == 0:
            raise FileLoaderError(
                f"Could not load any files in {folder} with " f"{file_loader}."
            )

        return DataFrame(cases)

    def process_case(self, *, idx: int, case: DataFrame) -> Dict:
        """
        implements the process_case method of evalutils'
            class SegmentationAlgorithm(Algorithm)
            def process_case(self, *, idx: int, case: DataFrame) -> Dict:

        This function prepares the case, calls the subclass's prediction algorithm,
            which saves the prediction array,
            and returns a dict for self._case_results in self.process_cases()

        NOTE: calling order is self.process() ->
                               self.process_cases() ->
                               self.process_case()
        """
        print(f"\n-- call process_case(idx={idx})")

        # Initialize case
        # NOTE: Arrays have axis order (x,y,z)
        self.initialize_case(case=case)

        input_image_ct = self.input_image_ct
        input_image_mr = self.input_image_mr
        segmentation_dict = self.segmentation_dict

        # Predict segmentation, np.array in order (x,y,z)
        print("-- call self.predict()")
        print(">>> Your MyCoWSegAlgorithm will now have the required inputs:")
        print(">>>     input_image_ct: sitk.Image and input_image_mr: sitk.Image")
        print(">>> Please implement your algorithm here, and return us the")
        print(">>>     Output: Segmentation np.array in (x,y,z)\n")
        segmentation_prediction = self.predict(
            image_ct=input_image_ct, image_mr=input_image_mr
        )
        print("\n<<< Congratulations! We have finished processing your predict() func")
        print("<<< We will now save your prediction array as .mha image")
        print(f"<<< to {self.segmentation_path}\n")

        # Save prediction array as .mha image to correct output folder
        self.save_segmentation(
            pred_array=segmentation_prediction,
        )

        # Write segmentation dictionary to results.json for this case
        return segmentation_dict

    def initialize_case(self, *, case: DataFrame):
        """
        Initializing the case for prediction
        """
        track = self.track
        task = self.task
        print(f"\n-- call initialize_case(track={track.value}, task={task.value})")

        # Load and test the image for this case
        self._load_input_image(case=case)

        input_image_file_path_ct = self.input_image_file_path_ct
        input_image_file_path_mr = self.input_image_file_path_mr

        output_path = self._output_path

        if track == TRACK.MR:
            main_input_image_file = input_image_file_path_mr.name
            secondary_input_image_file = input_image_file_path_ct.name
        elif track == TRACK.CT:
            main_input_image_file = input_image_file_path_ct.name
            secondary_input_image_file = input_image_file_path_mr.name

        self.segmentation_path = output_path / main_input_image_file

        # Write segmentation file path to result.json for this case
        self.segmentation_dict = {
            "track": track.value,
            "task": task.value,
            "outputs": [
                dict(type="metaio_image", filename=self.segmentation_path.name)
            ],
            "main_input": [dict(type="metaio_image", filename=main_input_image_file)],
            "secondary_input": [
                dict(type="metaio_image", filename=secondary_input_image_file)
            ],
            "error_messages": [],
        }
        print(f"self.segmentation_dict = \n{self.segmentation_dict}")

        print("initialize_case() done\n")

    def save_segmentation(
        self,
        *,
        pred_array: np.array,
    ):
        """
        Save prediction array as .mha image with same metadata as main input image.
        Array must be in order (x,y,z)
        """
        track = self.track
        task = self.task
        segmentation_path = self.segmentation_path
        input_image_mr = self.input_image_mr
        input_image_ct = self.input_image_ct

        print("\n-- call save_segmentation() using:")
        print(f"\ttrack={track.value}, task={task.value}")
        print(f"\tsegmentation_path={segmentation_path}")

        # Input images are needed for the metadata
        if track == TRACK.MR:
            print("-> main_input is from TRACK.MR")
            main_input = input_image_mr
        else:
            print("-> main_input is from TRACK.CT")
            main_input = input_image_ct

        assert (
            main_input.GetSize() == pred_array.shape
        ), "Prediction output must have the same shape as the main input image"

        # Reorder array from (x,y,z) to (z,y,x) before using sitk.GetImageFromArray
        pred_array = pred_array.transpose((2, 1, 0)).astype(np.uint8)

        # Converting prediction array back to SimpleITK copying the metadata from the original image
        seg_mask = sitk.GetImageFromArray(pred_array.astype(np.uint8))
        # Copies the Origin, Spacing, and Direction from the source image
        seg_mask.CopyInformation(main_input)

        # write the image
        sitk.WriteImage(seg_mask, str(segmentation_path), useCompression=True)

        print(f">>> Seg saved at {segmentation_path}\n")

    def save(self):
        """overwrite the default .save() by NOT saving any results.json"""
        pass


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


def _sitk_access_attr(image: sitk.Image):
    """
    Accessing Attributes
    """
    print("##############################################")
    print(f"image.GetSize() = {image.GetSize()}")
    print(f"image.GetWidth() = {image.GetWidth()}")
    print(f"image.GetHeight() = {image.GetHeight()}")
    print(f"image.GetDepth() = {image.GetDepth()}")
    print(f"image.GetOrigin() = {image.GetOrigin()}")
    print(f"image.GetSpacing() = {image.GetSpacing()}")
    print(f"image.GetDirection() = {image.GetDirection()}")
    print("image.GetNumberOfComponentsPerPixel() =")
    print(image.GetNumberOfComponentsPerPixel())
    print(f"image.GetDimension() = {image.GetDimension()}")
    print(f"image.GetPixelIDValue() = {image.GetPixelIDValue()}")
    print(f"image.GetPixelIDTypeAsString() = {image.GetPixelIDTypeAsString()}")
    for key in image.GetMetaDataKeys():
        print('"{0}":"{1}"'.format(key, image.GetMetaData(key)))
    print("##############################################")
