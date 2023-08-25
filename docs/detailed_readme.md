
### 2 tracks, 2 tasks

The TopCoW challenge has 2 tracks (MR and CT) and 2 tasks (binary and multi-class segmentation). For each track and task you can submit a separate Docker image containing your algorithm. In total there will thus be 4 different submission paths with 4 different leaderboards for validation and test phases. You can participate in any (or all) that you like.

(*If you submit a multi-class segmentation algorithm, it is automatically considered for binary segmentation task by merging all classes into binary classes.*)

For any track and task you can use the same template class (`MyCoWSegAlgorithm`).


The modality of the given track is then considered to be the main modality, the other one the secondary modality.
For each test case the input to your algorithm will be both the CT image and the MR image, irrespective of whether your algorithm uses both images or not. In case you only need one of them, simply ignore the second input.

### Execution

If you execute the scripts locally (`python3 process.py`), local input and output folders are used. You can populate the input folder with example images of a patient for local testing of your algorithm.  

### Input and output paths

Keep the input and output paths in the `base_algorithm.py` as they are, otherwise the scripts might not work properly. This is especially important for execution in Docker since grand-challenge provides the input/output interfaces.



### Case by case

The algorithm evaluation works on a case-by-case basis, where each case is a patient with 1 CT image and 1 MR image. For each case your submitted algorithm should produce 1 segmentation prediction, which is later on compared to the ground-truth.  
The processing pipeline of the template class (*MyCoWSegAlgorithm*) is as follows for each case:
* *initialize_case()*: Initializing the case for prediction. Returns the loaded images (*SimpleITK.Image*) of both modalities, the output path for saving the segmentation
*  *predict()*: Predicting the segmentation for the main modality. This is the method that you should provide. 
* *save_segmentation()*: Saving the predicted segmentation mask as an .mha image with the same metadata as the input image of the main modality. 

This pipeline is called within the *process_case()* function and does not need to be changed unless you want to specify your own pipeline. 

### Prediction algorithm
The *predict()* method must contain your prediction algorithm, i.e. the algorithm that returns the segmentation predictions. The function has *SimpleITK.Images* as input and should return a numpy array as output. **Note:** We expect the output array to have axis order *(x,y,z)*. If you work with a different order, e.g. when using with *SimpleITK.GetImageFromArray*, then don't forget to reorder the axis before returning the array (as we do in our example).       
For each test case the input to your algorithm will be both the CT image and the MR image, irrespective of whether your algorithm uses both images or not. In case you only need one of them, simply ignore the second input.    
For each test case the output of your algorithm must be a prediction array either for the CT or the MR image (depending on the track) and either binary or multi-class (depending on the task). The output mask array must have the same shape as the input image of the modality that you want to segment (i.e. the main modality of the track you submit for). This is important for the correct evaluation of your segmentation result (see below).  
 
Depending on how your algorithm works, you can load and initialize your model(s) in the constructor (*\__init\__*) and add custom methods as required. E.g., add methods like *load_model()*, *process_image()*, *postprocessing()* or similar if required. Your algorithm can be as complex as you want.

### Evaluation
Your predictions are fed into another Docker container for evaluation. This Docker container contains the ground-truth labels and ROI coordinates for cropping. Your predictions are only evaluated within this ROI containing the CoW. In order for the ROIs of your predictions and the ground-truths to match, it's important that your predictions have the correct shape (the same shape as the input image of the modality you want to segment)! 

## Example overview
We provide an example for the 'mr' track and the 'bin_seg' task. Our dummy algorithm takes the MR image as input (ignoring the presented CT image) and segments it based on a simple thresholding. The output is a binary segmentation mask of the MR stored as an .mha image.

If run locally (`python3 process.py`), the input images are loaded from *./input/head-ct-angio/* and *./input/head-mr-angio/* respectively, the output image is saved to *./output/images/cow-binary-segmentation/*.

## Base algorithm
Under the hood, *base_algorithm.py* does much of the relevant work:
* Loading the images an presenting them to the *predict()* function. It always loads a paired CT and MR from the folders *head-ct-angio* and *head-mr-angio* respectively. For each run, these folders can only contain 1 image each.
* Saving the returned prediction array as an .mha in the correct output folder (either *cow-binary-segmentation* or *cow-multiclass-segmentation*). Thereby it copies the metadata from the original main input image. 

There should be no need to change `class BaseAlgorithm` unless you know what you are doing :)  
