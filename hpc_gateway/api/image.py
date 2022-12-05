"""Image APIs contains entrypoints to operate with the images,
It can pull the singularity images as cache or download specific
image and store `.sif` image file in the image storage.
"""

from flask import Blueprint

# For the container image operations
image_api_v1 = Blueprint("image_api_v1", "image_api_v1", url_prefix="/api/v1/image")


@image_api_v1.route("/", methods=["GET"])
def api_get_images():
    """get all images in the machine"""
    pass


@image_api_v1.route("/pull", methods=["POST"])
def api_pull_image():
    """cache pull the image,
    or pull to users storage that can only used by one user (NOT IMPLEMENTED YET)
    """
    pass
