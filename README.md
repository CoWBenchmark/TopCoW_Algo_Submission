# TopCoW Algorithm Submit Tempalte 🐮

 **Algorithm submission template** repo for the [**TopCoW2023 challenge**](https://topcow23.grand-challenge.org/) on grand-challnge (GC).
 The source code for the algorithm container was generated with `evalutils` version `0.4.2` using `Python 3.10`,
 and is specified to work with the GC algorithm submission system.

![overview-of-what-we-need](./docs/GC_TopCoWAlgorithm_4SubmissionPorts.png)
^Overview diagram in [PDF](./docs/GC_TopCoWAlgorithm_4SubmissionPorts-1.pdf)

## TLDR

* **If you want more flexibility (i.e. customize this repo beyond `process.py` file or not using this template repo and `evalutils` at all)**, then simply ensure that your docker container can:
  1. read from the input interface that supplies **two `.mha` images**:

        > Head MR Angiography (Image) at **`/input/images/head-mr-angio/<uuid>.mha`**
        >
        > Head CT Angiography (Image) at **`/input/images/head-ct-angio/<uuid>.mha`**

  2. write to the output interface **one `.mha` segmentation mask** depending on the task selected (binary or multi-class segmentation):

        > Circle of Willis Binary Segmentation (Segmentation) to **`/output/images/cow-binary-segmentation/<uuid>.mha`**
        >
        > Circle of Willis Multiclass Segmentation (Segmentation) to **`/output/images/cow-multiclass-segmentation/<uuid>.mha`**


* **If you are new to the GC submission system**, we recommend that you clone this repo locally and use it as a template, **which only requires a few simple steps to build a submission container!**
The steps are easily done, and you just follow the `TODO` in one or two files!

    1. Clone this repo locally
    2. Add your algorithm by editing the **`./process.py`** file
    3. Submit your algorithm by
        - (recommended) use `./export.sh` to create a `tar.gz` of your docker container and upload to GC
        - or link a _private_ repo let GC build the container in the cloud
        - GC documentation on the above two options: [how to deploy your container](https://grand-challenge.org/documentation/test-and-deploy-your-container/)


  For more information on **using this repo as a base, please refer to [Use This Repo as a Base](#use-this-repo-as-a-base)**


* **Submission portal links**. We have 8 submission portals in total. Four submission portals for the validation phase, and four for the final-test phase, one for each track and task:
    * Submit to [Validation MRA Binary](https://topcow23.grand-challenge.org/evaluation/validation-mra-binary/submissions/create/)
    * Submit to [Validation CTA Binary](https://topcow23.grand-challenge.org/evaluation/validation-cta-binary/submissions/create/)
    * Submit to [Validation MRA MultiClass](https://topcow23.grand-challenge.org/evaluation/validation-mra-multiclass/submissions/create/)
    * Submit to [Validation CTA MultiClass](https://topcow23.grand-challenge.org/evaluation/validation-cta-multiclass/submissions/create/)
    * Submit to [Final Test MRA Binary](https://topcow23.grand-challenge.org/evaluation/finaltest-mra-binary/submissions/create/)
    * Submit to [Final Test CTA Binary](https://topcow23.grand-challenge.org/evaluation/finaltest-cta-binary/submissions/create/)
    * Submit to [Final Test MRA MultiClass](https://topcow23.grand-challenge.org/evaluation/finaltest-mra-multiclass/submissions/create/)
    * Submit to [Final Test CTA MultiClass](https://topcow23.grand-challenge.org/evaluation/finaltest-cta-multiclass/submissions/create/)

    You are free to [**submit your algorithm containers**](https://grand-challenge.org/documentation/making-a-challenge-submission/#submitting-your-algorithm-container) to any of the phases.
    Please use the validation submission portals to make sure your docker containers work as intended.
    You can submit to validation phases with a daily limit until they close.
    But final test phases only allow for maximal one or two submissions.

---

## Use This Repo as a Base

### Clone this repo

If you want to use this repo as a base, first clone this repo locally.
(_Optionally, if you intend to submit your algorithm by linking a private GitHub repo, you can follow these [steps to clone and set up a private repo](https://grand-challenge.org/documentation/clone-a-repository-from-a-challenge-baseline-algorithm/)._)


### Edit `./process.py`

You can then adapt the `MyCoWSegAlgorithm` class in the `process.py` file. We have marked to most relevant parts you need to change with **`TODO`**.

**Only three parts need `TODO` actually**:

1. Specify the `track` and `trask`
2. Set up your model in `__init__`
3. Run your inference and return us numpy prediction mask in `predict()`

Simply specify `track` and `task` on top of the `process.py` file:

```python
# TODO: First, choose your track and task!
# track is either TRACK.CT or TRACK.MR
# task is either TASK.BINARY_SEGMENTATION or TASK.MULTICLASS_SEGMENTATION
track = TRACK.MR
task = TASK.BINARY_SEGMENTATION
```

Finally, in the `predict()` method, implement your inference algorithm there, and whatever you do,
**just return us an `numpy array`**. We will handle the rest of the file conversion and output saving etc from there onwards.

```python
def predict(self, *, image_ct: sitk.Image, image_mr: sitk.Image) -> np.array:
    """
    Inputs will be a pair of CT and MR .mha SimpleITK.Images
    Output is supposed to be an numpy array in (x,y,z)
    """

    # TODO: place your own prediction algorithm here
    model.predict(image_ct)
    ...
    # END OF TODO

    # return prediction array
    return pred_array
```

#### Requirement for `predict()` output array shape

For each test case the output of your algorithm must be a prediction array either for the CT or the MR image (depending on the track) and either binary or multi-class (depending on the task).

Your predictions are only evaluated within the ROI containing the CoW. In order for the ROIs of your predictions and the ground-truths to match, it's important that **your output mask array must have the same shape as the input image of the modality of the track you submit for**.

```python
# under the hood in our base_algorithm.py
# your pred_array needs to pass this test
assert (
    main_input.GetSize() == pred_array.shape
)
```

### Testing and deploying Docker container

Update your `requirements.txt` for your required python libraries.

Make the necessary changes to the `Dockerfile`:

* Choose a suitable base image if necessary to build your container (e.g., Tensorflow or Pytorch or even Ubuntu, or a different version of Python base image)
* Make sure that all required source files (such as model weights and python scripts) are copied to the Docker container with `COPY` in your `Dockerfile`

```docker
COPY --chown=user:user <somefile> /opt/app/
```

#### Build

Once your scripts are ready, you can build the container by `bash build.sh` to test if all dependencies are met.

#### **Test your container!**

**Highly recommended to test your container by `bash test.sh` locally**. This will mimic the GC docker running environment and input to your docker container any mha files you provide in the `input` folder. It will check the output predictions against what you provide in `./test/expected_output/`:

```bash
# TODO: Provide the expected output segmentation mask of your algorithm in ./test/expected_output/
# TODO: In the python code snippet below change the following if necessary:

TASK="binary"  # "binary" or "multiclass"
IMAGE_FILENAME="uuid_of_mr_whole_066.mha"
EXPECTED_SEG_MASK="topcow_mr_whole_066_testdocker_bin_seg.mha"
```

**Feel free to change the pair of test images in `test/input/images/head-ct-angio/` and `test/input/images/head-mr-angio/`, and the corresponding expected output in `test/expected_output` to validate your algorithm works as intended**.

**Note:** the scripts work on a case-by-case basis. So, there should only be 1 CT image and 1 MR image in the corresponding input folders.

Currently, you find `test/input/images/head-ct-angio/uuid_of_ct_whole_066.mha` and `test/input/images/head-mr-angio/uuid_of_mr_whole_066.mha` in the input folder and the corresponding outputs from our dummy algorithm in `test/expected_output/topcow_mr_whole_066_testdocker_bin_seg.mha`

### Export and Deploy

If you choose to upload your container to GC directly (instead of linking a private Github repo, see above TLDR), then run `export.sh` to package your docker container image. This will create a `.tar.gz` file ready for upload to one of our GC submission portals.

**NOTE: it is a good idea to rename the default generated file with a more informative name, since we have 2 tracks and 2 tasks:**

```bash
# e.g. for track MR, task multi-seg:
mv algo_docker_<date>.tar.gz <some_info>_<track><task>_<date>.tar.gz
```

### Making a Challenge Submission

Please refer to the GC documentation on ["Submitting your Algorithm container"](https://grand-challenge.org/documentation/making-a-challenge-submission/#submitting-your-algorithm-container), espeically the ["Submission tips"](https://grand-challenge.org/documentation/making-a-challenge-submission/#submission-tips).

_NOTE: It is recommended to use the GC to "Try Out Algorithm" first:_
> Once your container is active, please test it out before submitting it to the challenge, you can upload data using the "Try Out Algorithm" button. Please use a representative image and check that the outputs are what you expect. You can inspect the error messages on the Results page of your algorithm.

---

And that is it! 🤠
All the best for the submission process.
Please reach out to us by leaving an issue on this repo or on our challenge forum.

Here is a more detailed version of this readme for your reference: [detailed_readme](./docs/detailed_readme.md)

## References

We are very grateful for the following challenges that provide helpful tutorials and excellent example code!
Please have a look at these template repos if you want to deeply customize our repo or for more explanations.

* MIDOG Challenge Github with tutorial: [https://github.com/DeepMicroscopy/MIDOG_reference_docker](https://github.com/DeepMicroscopy/MIDOG_reference_docker)
* HanSeg Challenge Github with tutorial: [https://github.com/gasperpodobnik/HanSeg2023Algorithm/](https://github.com/gasperpodobnik/HanSeg2023Algorithm/)
* CL-Dection Challenge Github with tutorial: [https://github.com/szuboy/CL-Detection2023](https://github.com/szuboy/CL-Detection2023)
* SegRap Challenge Github with tutorial: [https://github.com/HiLab-git/SegRap2023](https://github.com/HiLab-git/SegRap2023)
