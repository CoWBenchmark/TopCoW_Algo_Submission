# TopCoW Algorithm Submit Template for Task 2: CoW Detection 🐮

## TLDR

* **If you want more flexibility (i.e. customize this repo beyond `your_algorithm.py` file or not using this template repo at all)**, then simply ensure that your docker container can:
  1. read from the input interface that supplies **two `.mha` images**:

        > Head MR Angiography (Image) at **`/input/images/head-mr-angio/<uuid>.mha`**
        >
        > Head CT Angiography (Image) at **`/input/images/head-ct-angio/<uuid>.mha`**

  2. write to the output interface **one `.json` bounding box**:

        > Circle of Willis Bounding Box (Json) to **`/output/cow-roi.json`**


* **If you are new to the GC submission system**, we recommend that you use this repo as a template, **which only requires a few simple steps to build a submission container!**
The steps are easily done, and you just follow the `TODO` in one file!

    1. Add your algorithm by editing the **`./your_algorithm.py`** file
    3. Submit your algorithm by
        - either linking a **private** repo let GC build the container in the cloud
        - or use `./export.sh` to create a `tar.gz` of your docker container and upload to GC
        - GC documentation on the above two options: [how to deploy your container](https://grand-challenge.org/documentation/test-and-deploy-your-container/)


  For more information on **using this repo as a template, please refer to [Use This Repo as a Template](#use-this-repo-as-a-template)**


* **Submission portal links**. We have 4 submission portals for task 2. Two submission portals for the validation phase, and two for the final-test phase, one for each track:
    * Submit to [Validation CTA Task 2 Box](https://topcow24.grand-challenge.org/evaluation/validation-cta-task-2-box/submissions/create/)
    * Submit to [Validation MRA Task 2 Box](https://topcow24.grand-challenge.org/evaluation/validation-mra-task-2-box/submissions/create/)
    * Submit to [Final Test CTA Task 2 Box](https://topcow24.grand-challenge.org/evaluation/finaltest-cta-task-2-box/submissions/create/)
    * Submit to [Final Test MRA Task 2 Box](https://topcow24.grand-challenge.org/evaluation/finaltest-mra-task-2-box/submissions/create/)

    Please use the validation submission portals to make sure your docker containers work as intended.
    You can submit to validation phases with a daily limit until they close.
    But final test phases only allow for maximal one or two submissions.

---

## Use This Repo as a Template

### Edit `./your_algorithm.py`

You can then adapt the `your_algorithm.py` file. We have marked the most relevant parts you need to change with **`TODO`**.

In the `your_detection_algorithm()` function, implement your inference algorithm there, and whatever you do,
**just return us a `dictionary`** containing your predicted bounding box in the form
```python
{
    "size": [x, y, z],
    "location": [x, y, z]
}
```
We will handle the rest of the file conversion and output saving etc from there onwards.

```python
def your_detection_algorithm(*, mr_input_array: np.array, ct_input_array: np.array) -> dict:
    """
    args:
        mr_input_array: np.array - input image for MR track
        ct_input_array: np.array - input image for CT track
    returns:
        dict - bounding box prediction in the form {"size": [x, y, z], "location": [x, y, z]}
    """

    # TODO: place your own prediction algorithm here
    model = ...
    device = ...
    ...
    model.predict(ct_input_array)
    ...
    # END OF TODO

    # return prediction dictionary
    return pred_dict
```

#### Requirement for `your_detection_algorithm()` output dictionary

For each test case the output of your algorithm must be a prediction dictionary with a "location" and "size" key. The "location" is a list for the lower coordinates of x-min, y-min, z-min (0-indexed) of the 3D volume. The "size" is a list of number of voxels of the volume along the x, y, and z axis.
```python
{
    "size": [x, y, z],
    "location": [x, y, z]
}
```
Under the hood in our `inference.py` your pred_dict needs to pass some tests
```python
assert type(content) == dict
assert content.keys() == {"size", "location"}
assert type(content["size"]) == list and type(content["location"]) == list
assert len(content["size"]) == 3 and len(content["location"]) == 3
assert all([type(i) == int for i in content["size"] + content["location"]])
```

#### Running inference

You can run inference locally by executing the script `inference.py`. The `inference.py` also serves as the entrypoint for the Docker container. 

**NOTE: You don't need to change anything in the `inference.py` script.**

### Testing and deploying Docker container

Update your `requirements.txt` for your required python libraries.

Make the necessary changes to the `Dockerfile`:

* Choose a suitable base image if necessary to build your container (e.g., Tensorflow or Pytorch or even Ubuntu, or a different version of Python base image)
* Make sure that all required source files (such as model weights and python scripts) are copied to the Docker container with `COPY` in your `Dockerfile`

```docker
COPY --chown=user:user <somefile> /opt/app/
```

#### **Test your container!**

**Highly recommended to test your container by `bash test_run.sh` locally**. This will mimic the GC docker running environment and input to your docker container any mha files you provide in the `./test/input` folder. It will check the predicted output `cow-roi.json` against what you provide in `./test/expected_output/cow-roi.json`.

**Feel free to change the pair of test images in `test/input/images/head-ct-angio/` and `test/input/images/head-mr-angio/`, and the corresponding expected output in `test/expected_output` to validate your algorithm works as intended**.

**Note:** the scripts work on a case-by-case basis. So, there should only be 1 CT image and 1 MR image in the corresponding input folders.

Currently, you find `test/input/images/head-ct-angio/example_input_dummy_cta.mha` and `test/input/images/head-mr-angio/example_input_dummy_mra.mha` in the input folder.

### Export and Deploy

If you choose to upload your container to GC directly (instead of linking a private Github repo, see above TLDR), then run `save.sh` to package your docker container image. This will create a `.tar.gz` file ready for upload to one of our GC submission portals.

**NOTE: it is a good idea to rename the default generated file with a more informative name, since we have 2 tracks:**

```bash
mv algo_docker_task-2_box_<timestamp>.tar.gz <some_info>_<track>_task-2_box_<timestamp>.tar.gz
```

### Making a Challenge Submission

Please refer to the GC documentation on ["Submitting your Algorithm container"](https://grand-challenge.org/documentation/making-a-challenge-submission/#submitting-your-algorithm-container), espeically the ["Submission tips"](https://grand-challenge.org/documentation/making-a-challenge-submission/#submission-tips).

_NOTE: It is recommended to use the GC to "Try Out Algorithm" first:_
> Once your container is active, please test it out before submitting it to the challenge, you can upload data using the "Try Out Algorithm" button. Please use a representative image and check that the outputs are what you expect. You can inspect the error messages on the Results page of your algorithm.

---

And that is it! 🤠
All the best for the submission process.
Please reach out to us by leaving an issue on this repo or on our challenge forum.