# Dockerfile for task 1: CoW multiclass segmentation.

# Edit the base image here, e.g. to use
# Tensorflow: https://hub.docker.com/r/tensorflow/tensorflow/ 
# Pytorch: https://hub.docker.com/r/pytorch/pytorch/
# For Pytorch e.g.: FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-runtime
# Or list your pip packages in requirements.txt and install them
FROM python:3.10-slim

# Ensures that Python output to stdout/stderr is not buffered: prevents missing information when terminating
ENV PYTHONUNBUFFERED=1

RUN groupadd -r user && useradd -m --no-log-init -r -g user user
USER user

WORKDIR /opt/app

COPY --chown=user:user requirements.txt /opt/app/
COPY --chown=user:user resources /opt/app/resources

# You can add any Python dependencies to requirements.txt
RUN python -m pip install \
    --user \
    --no-cache-dir \
    --no-color \
    --requirement /opt/app/requirements.txt

COPY --chown=user:user inference.py /opt/app/
COPY --chown=user:user your_algorithm.py /opt/app/
COPY --chown=user:user torch_utilities.py /opt/app/

ENTRYPOINT ["python", "inference.py"]
