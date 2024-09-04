"""
The following is a simple example algorithm for task 2: CoW detection/localization.

It can be run locally (good for setting up and debugging your algorithm) 
or in a docker container (required for submission to grand-challenge.org).

If you use this template you can simply replace the `your_detection_algorithm` function with your own algorithm. 
The suggested inputs are np.arrays of the MR and CT images respectively, the output should be a dictionary containing 
the predicted bounding box in the form
    {
    "size": [x, y, z],
    "location": [x, y, z]
    }

To run your algorithm, execute the `inference.py` script (inference.py is the entry point for the docker container). 
NOTE: You don't need to change anything in the inference.py script!

The relevant paths are as follows:
    input_path: contains the input images inside the folders /images/head-mr-angio or /images/head-ct-angio
        Docker: /input
        Local: ./test/input
    output_path: output predictions are stored as cow-roi.json
        Docker: /output
        Local: ./test/output
    resource_path: any additional resources needed for the algorithm during inference can be stored here (optional)
        Docker: resources
        Local: ./resources

Before submitting to grand-challenge.org, you must ensure that your algorithm runs in the docker container. To do this, run 
  ./test_run.sh
This will start the inference and reads from ./test/input and outputs to ./test/output

To save the container and prep it for upload to Grand-Challenge.org you can call:
  ./save.sh
"""
import numpy as np

def your_detection_algorithm(*, mr_input_array: np.array, ct_input_array: np.array) -> dict:
    """
    This is an example of a prediction algorithm.
    It is a dummy algorithm that returns a bounding box in the center of the image
    args:
        mr_input_array: np.array - input image for MR track
        ct_input_array: np.array - input image for CT track
    returns:
        dict - bounding box prediction in the form {"size": [x, y, z], "location": [x, y, z]}
    """

    #######################################################################################
    # TODO: place your own prediction algorithm here.
    # You are free to remove everything! Just return to us a dictionary containing 
    # the bounding box prediction in the form {"size": [x, y, z], "location": [x, y, z]}.
    # You can use the input_head_mr_angiography and/or input_head_ct_angiography
    # to make your prediction.

    # NOTE: If you extract the array from SimpleITK, note that
    #              SimpleITK npy array axis order is (z,y,x).
    #              Then you might have to transpose this to (x,y,z)

    #######################################################################################

    # load and initialize your model here
    # model = ...
    # device = ...

    # You can also place and load additional files in the resources folder
    # with open(resources / "some_resource.txt", "r") as f:
    #     print(f.read())

    # For now, let us set make bogus predictions for the MR image
    output_shape = mr_input_array.shape
    
    pred_dict = {
        "size": [l // 2 for l in output_shape],
        "location": [p // 4 for p in output_shape]
    }

    return pred_dict