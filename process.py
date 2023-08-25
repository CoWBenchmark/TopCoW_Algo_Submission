"""
The most important file for Grand-Challenge Algorithm submission is this process.py.
This is the file where you will extend our base algorithm class,
and modify the subclass of MyCoWSegAlgorithm for your awesome algorithm :)
Simply update the TODO in this file.

NOTE: remember to COPY your required files in your Dockerfile
COPY --chown=user:user <somefile> /opt/app/
"""

import numpy as np
import SimpleITK as sitk

from base_algorithm import TASK, TRACK, BaseAlgorithm

#######################################################################################
# TODO: First, choose your track and task!
# track is either TRACK.CT or TRACK.MR
# task is either TASK.BINARY_SEGMENTATION or TASK.MULTICLASS_SEGMENTATION
track = TRACK.MR
task = TASK.BINARY_SEGMENTATION
# END OF TODO
#######################################################################################


class MyCoWSegAlgorithm(BaseAlgorithm):
    """
    Your algorithm goes here.
    Simply update the TODO in this file.
    """

    def __init__(self):
        super().__init__(
            track=track,
            task=task,
        )

        #######################################################################################
        # TODO: load and initialize your model here
        # self.model = ...
        # self.device = ...

        # END OF TODO
        #######################################################################################

    def predict(self, *, image_ct: sitk.Image, image_mr: sitk.Image) -> np.array:
        """
        Inputs will be a pair of CT and MR .mha SimpleITK.Images
        Output is supposed to be an numpy array in (x,y,z)
        """

        #######################################################################################
        # TODO: place your own prediction algorithm here
        # You are free to remove everything! Just return to us an npy in (x,y,z)
        # NOTE: If you extract the array from SimpleITK, note that
        #              SimpleITK npy array axis order is (z,y,x).
        #              Then you might have to transpose this to (x,y,z)
        #              (see below for an example).
        #######################################################################################

        # for example, if you use nnUnet
        # you can create a imagesTs folder with nii.gz files
        # check out SegRap challenge tutorial: https://github.com/HiLab-git/SegRap2023/blob/main/Docker_tutorial/SegRap2023_task1_OARs_nnUNet_Example/process.py
        import os

        imagesTs_path = os.path.join("./", "imagesTs")
        os.makedirs(imagesTs_path, exist_ok=True)
        main_nii_path = os.path.join(imagesTs_path, "inference_case1_0000.nii.gz")

        if track == TRACK.MR:
            print("-> main_input is from TRACK.MR")
            main_input = image_mr
            sec_input = image_ct
        else:
            print("-> main_input is from TRACK.CT")
            main_input = image_ct
            sec_input = image_mr
        sitk.WriteImage(main_input, main_nii_path, useCompression=True)
        # if using both modalities as channels, name the other modality with _0001
        # see https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format_inference.md
        sec_nii_path = os.path.join(imagesTs_path, "inference_case1_0001.nii.gz")
        sitk.WriteImage(sec_input, sec_nii_path, useCompression=True)

        # Check your imagesTs folder
        print("imagesTs_path = ", os.path.abspath(imagesTs_path))
        print(f"list imagesTs_path = {os.listdir(imagesTs_path)}")

        # e.g. this dummy example works for both binary and multi-class segmentation
        # because label 1 can be either CoW (in binary seg) or BA (in multi-class)
        stats = sitk.StatisticsImageFilter()
        stats.Execute(main_input)
        print("Main input max val: ", stats.GetMaximum())

        segmentation = sitk.BinaryThreshold(
            main_input,
            lowerThreshold=stats.GetMaximum() // 3,  # some arbitrary threshold
            upperThreshold=stats.GetMaximum(),
        )
        # NOTE: SimpleITK npy axis ordering is (z,y,x)!
        pred_array = sitk.GetArrayFromImage(segmentation)

        # reorder from (z,y,x) to (x,y,z)
        pred_array = pred_array.transpose((2, 1, 0)).astype(np.uint8)
        print("pred_array.shape = ", pred_array.shape)
        # The output np.array needs to have the same shape as track modality input
        print(f"main_input.GetSize() = {main_input.GetSize()}")

        # END OF TODO
        #######################################################################################

        # return prediction array
        return pred_array


if __name__ == "__main__":
    # NOTE: running locally ($ python3 process.py) has advantage of faster debugging
    # but please ensure the docker environment also works before submitting
    MyCoWSegAlgorithm().process()
    cowsay_msg = """\n
  ____________________________________
< MyCoWSegAlgorithm().process()  Done! >
  ------------------------------------
         \   ^__^ 
          \  (oo)\_______
             (__)\       )\/\\
                 ||----w |
                 ||     ||
    """
    print(cowsay_msg)
