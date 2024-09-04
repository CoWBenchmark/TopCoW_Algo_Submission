"""
The following is a simple example algorithm for task 3: CoW edge graph classification.

It can be run locally (good for setting up and debugging your algorithm) 
or in a docker container (required for submission to grand-challenge.org).

If you use this template you can simply replace the `your_classification_algorithm` function with your own algorithm. 
The suggested inputs are np.arrays of the MR and CT images respectively, the output should be a dictionary containing 
the predicted presence(1)/absence(0) of the anterior and posterior CoW edges in the form
{ 
    "anterior": 
        { "L-A1": 1/0, "Acom": 1/0, "3rd-A2": 1/0, "R-A1": 1/0 }, 
    "posterior": 
        { "L-Pcom": 1/0, "L-P1": 1/0, "R-P1": 1/0, "R-Pcom": 1/0 } 
}

To run your algorithm, execute the `inference.py` script (inference.py is the entry point for the docker container). 
NOTE: You don't need to change anything in the inference.py script!

The relevant paths are as follows:
    input_path: contains the input images inside the folders /images/head-mr-angio or /images/head-ct-angio
        Docker: /input
        Local: ./test/input
    output_path: output predictions are stored as cow-ant-post-classification.json
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


def your_classification_algorithm(*, mr_input_array: np.array, ct_input_array: np.array) -> dict:
    """
    This is an example of a prediction algorithm.
    It is a dummy algorithm that returns the classification result of a complete and standard CoW.
    args:
        mr_input_array: np.array - input image for MR track
        ct_input_array: np.array - input image for CT track
    returns:
        dict - CoW edge classification in the form { "anterior": { "L-A1": 1/0, "Acom": 1/0, "3rd-A2": 1/0, "R-A1": 1/0 }, 
               "posterior": { "L-Pcom": 1/0, "L-P1": 1/0, "R-P1": 1/0, "R-Pcom": 1/0 } }
    """

    #######################################################################################
    # TODO: place your own prediction algorithm here.
    # You are free to remove everything! Just return to us a dictionary containing 
    # the CoW edge classification prediction in the form { "anterior": { "L-A1": 1/0, "Acom": 1/0, "3rd-A2": 1/0, "R-A1": 1/0 }, 
    # "posterior": { "L-Pcom": 1/0, "L-P1": 1/0, "R-P1": 1/0, "R-Pcom": 1/0 } }.
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

    # For now, let us set make bogus predictions
    pred_dict = {
        "anterior": {
            "L-A1": 1, "Acom": 1, "3rd-A2": 0, "R-A1": 1
        },
        "posterior": {
            "L-Pcom": 1, "L-P1": 1, "R-P1": 1, "R-Pcom": 1
        }
    }

    return pred_dict