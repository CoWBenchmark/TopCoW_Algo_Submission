# TopCoW24 Algorithm Submission Template 🐮

This repo is the **algorithm submission template** for the [**TopCoW2024 challenge**](https://topcow24.grand-challenge.org/) on grand-challnge (GC).

There are three sub-folders, `task-{1,2,3}-X`, for the three tasks of the challenge.
Each sub-folder generates its own algorithm container, and is specified to work with the GC algorithm submission system.

Please read the instructions below and in the respective task sub-folder, and modify the relevant parts of the code to submit your algorithm.

## Important Notes

* **If you want more flexibility (i.e. customize this repo beyond `your_algorithm.py` files or not using this template repo at all)**, then simply ensure that your docker container can:
  1. read from the input interface that supplies **two `.mha` images**:

        > Head MR Angiography (Image) at **`/input/images/head-mr-angio/<uuid>.mha`**
        >
        > Head CT Angiography (Image) at **`/input/images/head-ct-angio/<uuid>.mha`**

  2. write to the output interface **one `.mha` segmentation mask, one `.json` bounding box or one `.json` edge classification** depending on the task selected:

        > Task 1: Circle of Willis Multi-class Segmentation (Segmentation) to **`/output/images/cow-multiclass-segmentation/<uuid>.mha`**
        >
        > Task 2: Circle of Willis Bounding Box (Json) to **`/output/cow-roi.json`**
        >
        > Task 3: Circle of Willis Edge Classification (Json) to **`/output/cow-ant-post-classification.json`**


* **If you are new to the GC submission system**, we recommend that you clone this repo locally and use it as a template, **which only requires a few simple steps to build a submission container for each task separately!**
The steps are easily done, and you just follow the `TODO` in one file!

    1. Clone this repo locally
    2. Choose your task and navigate to the corresponding subfolder 
    3. Add your algorithm by editing the **`./<chosen_task_subfolder>/your_algorithm.py`** file
    4. Submit your algorithm by
        - either linking a **private** repo and let GC build the container in the cloud
        - or use `./<chosen_task_subfolder>/save.sh` to create a `tar.gz` of your docker container and upload to GC
        - GC documentation on the above two options: [how to deploy your container](https://grand-challenge.org/documentation/test-and-deploy-your-container/)


  For more information on **using this repo as a base, please refer to [Use This Repo as a Base](#use-this-repo-as-a-base)**


* **Submission portal links**. We have 12 submission portals in total. Six submission portals for the validation phase, and six for the final-test phase, one for each track and task:
    * Submit to [Validation CTA Task 1 Seg](https://topcow24.grand-challenge.org/evaluation/validation-cta-task-1-seg/submissions/create/)
    * Submit to [Validation MRA Task 1 Seg](https://topcow24.grand-challenge.org/evaluation/validation-mra-task-1-seg/submissions/create/)
    * Submit to [Validation CTA Task 2 Box](https://topcow24.grand-challenge.org/evaluation/validation-cta-task-2-box/submissions/create/)
    * Submit to [Validation MRA Task 2 Box](https://topcow24.grand-challenge.org/evaluation/validation-mra-task-2-box/submissions/create/)
    * Submit to [Validation CTA Task 3 Edg](https://topcow24.grand-challenge.org/evaluation/validation-cta-task-3-edg/submissions/create/)
    * Submit to [Validation MRA Task 3 Edg](https://topcow24.grand-challenge.org/evaluation/validation-mra-task-3-edg/submissions/create/)
    * Submit to [Final Test CTA Task 1 Seg](https://topcow24.grand-challenge.org/evaluation/finaltest-cta-task-1-seg/submissions/create/)
    * Submit to [Final Test MRA Task 1 Seg](https://topcow24.grand-challenge.org/evaluation/finaltest-mra-task-1-seg/submissions/create/)
    * Submit to [Final Test CTA Task 2 Box](https://topcow24.grand-challenge.org/evaluation/finaltest-cta-task-2-box/submissions/create/)
    * Submit to [Final Test MRA Task 2 Box](https://topcow24.grand-challenge.org/evaluation/finaltest-mra-task-2-box/submissions/create/)
    * Submit to [Final Test CTA Task 3 Edg](https://topcow24.grand-challenge.org/evaluation/finaltest-cta-task-3-edg/submissions/create/)
    * Submit to [Final Test MRA Task 3 Edg](https://topcow24.grand-challenge.org/evaluation/finaltest-mra-task-3-edg/submissions/create/)

    You are free to [**submit your algorithm containers**](https://grand-challenge.org/documentation/making-a-challenge-submission/#submitting-your-algorithm-container) to any of the phases.
    Please use the validation submission portals to make sure your docker containers work as intended.
    You can submit to validation phases with a daily limit until they close.
    But final test phases only allow for maximal one or two submissions.

---

## Use This Repo as a Base

### Clone this repo

If you want to use this repo as a base, first clone this repo locally.
Optionally, if you intend to submit your algorithm by [linking a private GitHub repo](https://grand-challenge.org/documentation/linking-a-github-repository-to-your-algorithm/), you can follow these [steps](https://grand-challenge.org/documentation/clone-a-repository-from-a-challenge-baseline-algorithm/) to set up a private repo.

### Choose your task 

Each task has its own submission portals and needs its own separate Docker containers for submission. Of course we encourage participants to take part in several or all tasks, but keep in mind that you need to **build and submit separate Docker containers for each task**. For a submission for a specific task, **navigate to the corresponding subfolder and follow the steps that are specified there**. The steps are all roughly the same for the different tasks and are outlined below.

### Edit `your_algorithm.py`

For the chosen task you can then adapt the `your_algorithm.py` file. We have marked to most relevant parts you need to change with **`TODO`**.

### Testing and deploying Docker container

Update your `requirements.txt` for your required python libraries.

Make the necessary changes to the `Dockerfile`:

* Choose a suitable base image if necessary to build your container (e.g., Tensorflow or Pytorch or even Ubuntu, or a different version of Python base image)
* Make sure that all required source files (such as model weights and python scripts) are copied to the Docker container with `COPY` in your `Dockerfile`

```docker
COPY --chown=user:user <somefile> /opt/app/
```

#### **Test your container!**

**Highly recommended to test your container by `bash test_run.sh` locally**. This will mimic the GC docker running environment and input to your docker container any mha files you provide in the `./<chosen_task_subfolder/test/input` folder. 

**Feel free to change the pair of test images in `./<chosen_task_subfolder/test/input/images/head-ct-angio/` and `./<chosen_task_subfolder/test/input/images/head-mr-angio/`.**

**Note:** the scripts work on a case-by-case basis. So, there should only be 1 CT image and 1 MR image in the corresponding input folders.

Currently, you find `example_input_dummy_cta.mha` and `example_input_dummy_mra.mha` in the input folder. 

### Export and Deploy

If you choose to upload your container to GC directly (instead of linking a private Github repo, see above TLDR), then run `save.sh` to package your docker container image. This will create a `.tar.gz` file ready for upload to one of our GC submission portals.

**NOTE: it is a good idea to rename the default generated file with a more informative name, since we have 2 tracks and 3 tasks:**

```bash
# e.g. for task 2:
mv algo_docker_task-2_box_<timestamp>.tar.gz <some_info>_<track>_<task>_<timestamp>.tar.gz
```

### Making a Challenge Submission

Please refer to the GC documentation on ["Submitting your Algorithm container"](https://grand-challenge.org/documentation/making-a-challenge-submission/#submitting-your-algorithm-container), espeically the ["Submission tips"](https://grand-challenge.org/documentation/making-a-challenge-submission/#submission-tips).

_NOTE: It is recommended to use the GC to "Try Out Algorithm" first:_
> Once your container is active, please test it out before submitting it to the challenge, you can upload data using the "Try Out Algorithm" button. Please use a representative image and check that the outputs are what you expect. You can inspect the error messages on the Results page of your algorithm.

---

And that is it! 🤠
All the best for the submission process.
Please reach out to us by leaving an issue on this repo or on our challenge forum.
