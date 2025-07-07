import io
import os
from typing import Tuple, Dict

import requests
from PIL import Image

from openadapt.adapters import prompt
from openadapt import vision, utils
import replicate


FASTSAM_MODEL_REF = "casia-iva-lab/fastsam"


def _segment_image_from_url(image_url: str) -> Image.Image:
    """Segment an image using the FastSAM model on Replicate."""
    os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN", "")
    segmented_image_url = replicate.run(
        FASTSAM_MODEL_REF,
        input={"image": image_url},
    )
    image_data = requests.get(segmented_image_url).content
    return Image.open(io.BytesIO(image_data))


def _calculate_iou(box1: Dict[str, float], box2: Dict[str, float]) -> float:
    """Calculate intersection over union for two boxes."""
    left = max(box1["left"], box2["left"])
    top = max(box1["top"], box2["top"])
    right = min(box1["left"] + box1["width"], box2["left"] + box2["width"])
    bottom = min(box1["top"] + box1["height"], box2["top"] + box2["height"])
    if right <= left or bottom <= top:
        return 0.0
    intersection = (right - left) * (bottom - top)
    area1 = box1["width"] * box1["height"]
    area2 = box2["width"] * box2["height"]
    return intersection / float(area1 + area2 - intersection)


def describe_element(
    screenshot_url: str, bbox: Tuple[int, int, int, int]
) -> Dict[str, str]:
    """Return element name and description for the given screenshot and box."""
    response = requests.get(screenshot_url)
    response.raise_for_status()
    screenshot = Image.open(io.BytesIO(response.content))

    segmented_image = _segment_image_from_url(screenshot_url)
    masks = vision.get_masks_from_segmented_image(segmented_image)
    refined_masks = vision.refine_masks(masks)
    bounding_boxes, _ = vision.calculate_bounding_boxes(refined_masks)

    target_box = {"left": bbox[0], "top": bbox[1], "width": bbox[2], "height": bbox[3]}
    ious = [
        _calculate_iou(target_box, box)
        for box in bounding_boxes
    ]
    if not ious:
        raise ValueError("No masks found for segmentation")
    best_idx = max(range(len(ious)), key=lambda i: ious[i])
    masked_image = vision.extract_masked_images(
        screenshot,
        [refined_masks[best_idx]],
    )[0]

    system_prompt = utils.render_template_from_file("prompts/system.j2")
    prompt_text = (
        "What user interface element is contained in the highlighted circle of"
        " the image?"
    )
    description = prompt.prompt(
        prompt_text,
        images=[masked_image],
        system_prompt=system_prompt,
    ).strip()
    return {"name": description, "description": description}
