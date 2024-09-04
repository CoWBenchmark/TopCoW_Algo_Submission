import torch

def _show_torch_cuda_info():
    """
    Function to show information about the availability of Torch CUDA.
    Might be useful for testing availability inside the docker container.
    Torch must be installed in the docker environment for this to work.
    """

    print("=+=" * 10)
    print("Collecting Torch CUDA information")
    print(f"Torch CUDA is available: {(available := torch.cuda.is_available())}")
    if available:
        print(f"\tnumber of devices: {torch.cuda.device_count()}")
        print(f"\tcurrent device: { (current_device := torch.cuda.current_device())}")
        print(f"\tproperties: {torch.cuda.get_device_properties(current_device)}")
    print("=+=" * 10)