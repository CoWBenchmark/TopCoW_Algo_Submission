import os

import SimpleITK as sitk


def convert_mha_nii(img_path, file_ending, save_path="."):
    """
    convert between .mha metaImage to .nii.gz nifti compressed
    file_ending='.nii.gz' | '.mha'
    """
    img = sitk.ReadImage(img_path)
    source_fname = os.path.basename(img_path)
    target_fname = source_fname.split(".")[0] + file_ending
    sitk.WriteImage(img, os.path.join(save_path, target_fname), useCompression=True)


if __name__ == "__main__":
    img_path = "test/topcow_ct_whole_002_0000.nii.gz"
    convert_mha_nii(img_path, ".mha", save_path="test/input/images/head-ct-angio/")

    img_path = "test/topcow_mr_whole_002_0000.nii.gz"
    convert_mha_nii(img_path, ".mha", save_path="test/input/images/head-mr-angio/")

    print("Done")
