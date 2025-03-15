# prompt: A cloud run function that runs in response to a file being uploaded to a google cloud storage bucket. It should download the file into cloud run local storage

import functions_framework
from google.cloud import storage
import os
import cv2
import numpy as np
from rembg import remove
from PIL import Image
import math
import imutils

def crop_and_fill(image_path, output_path):
    input = Image.open(image_path)
    output = remove(input)
    imageBox = output.getbbox()
    cropped = output.crop(imageBox)
    cropped.save(output_path)


def fill_inner_circle(filename, output_path, bg_colour):
    if bg_colour == 'white':
        bg_code = (255, 255, 255)
    elif bg_colour == 'black':
        bg_code = (0, 0, 0)
    # Loads an image
    src = cv2.imread(cv2.samples.findFile(filename), cv2.IMREAD_COLOR)
    # Check if image is loaded fine
    if src is None:
        print ('Error opening image!')
        print ('Usage: hough_circle.py [image_name -- default ' + default_file + '] \n')
        return -1

    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    rows = gray.shape[0]
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 0.5, rows / 8,
                               param1=100, param2=50,
                               minRadius=math.floor(rows/8), maxRadius=math.ceil(rows/3))

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle center
            cv2.circle(src, center, 1, (0, 100, 100), 3)
            # circle outline
            radius = i[2]
            cv2.circle(src, center, radius, bg_code, -1)

    cv2.imwrite(output_path, src)
    # cv2_imshow(src)
    # cv2.waitKey(0)

    return 0

def fill_outside_largest_circle(image_path, output_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    rows = gray.shape[0]

    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.5, math.floor(rows/3),
                               param1=100, param2=50,
                               minRadius=math.floor(rows/3), maxRadius=math.ceil(rows/2))  # Adjust minRadius as needed

    if circles is not None:
        circles = np.uint16(np.around(circles))
        largest_circle = max(circles[0,:], key=lambda x: x[2])

        # Fill outside the largest circle with white
        mask = np.zeros_like(gray)
        cv2.circle(mask, (largest_circle[0], largest_circle[1]), largest_circle[2], (255), -1)

        img[mask == 0] = (255,255,255)

        cv2.imwrite(output_path, img)
    else:
        print("No circles found.")

input = "/content/Angel - B.jpg"
output = "/content/Angel - B.png"
bg_colour = 'white'

def process_image(input, output, bg_colour):
    crop_and_fill(input, "/content/no_bg.png")
    fill_inner_circle('/content/no_bg.png', output, bg_colour)
    if bg_colour == 'white':
        fill_outside_largest_circle(output, output)


@functions_framework.cloud_event
def process_image_upload(cloud_event):
    """
    Cloud Function triggered by a file upload to a Cloud Storage bucket.
    """

    data = cloud_event.data

    if not data:
        print("No data received in Cloud Event")
        return

    file_bucket = data["bucket"]
    file_name = data["name"]

    # Download the file from Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(file_bucket)
    blob = bucket.blob(file_name)

    # Use a temporary file to store the downloaded image.
    temp_local_filename = "/tmp/" + os.path.basename(file_name) # Cloud Run local file path
    blob.download_to_filename(temp_local_filename)

    try:
        # Process the downloaded image
        output_filename = "/tmp/" + os.path.splitext(os.path.basename(file_name))[0] + "_processed.png" # Local output path
        bg_colour = "white"  # Example bg_color - Could be made configurable
        process_image(temp_local_filename, output_filename, bg_colour)

        # Upload the processed image back to Cloud Storage (optional).
        processed_blob = bucket.blob(os.path.splitext(file_name)[0] + "_processed.png")
        processed_blob.upload_from_filename(output_filename)
        print(f"Processed image uploaded to gs://{file_bucket}/{processed_blob.name}")
    except Exception as e:
        print(f"Error processing image: {e}")

    # Clean up the temporary files (essential)
    os.remove(temp_local_filename)
    os.remove(output_filename)
    os.remove("/tmp/no_bg.png")  # Assuming this is a temporary file created in process_image

