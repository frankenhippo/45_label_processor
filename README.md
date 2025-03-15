# 45_label_processor
A Google Cloud Run Function that formats pictures of 7" single labels to the preferred style for 45cat. The image guide is here: https://www.45cat.com/45_cont_image_help.php
The main points are below:

1. Get The Image 
You can use a scanner to scan the record (we recommend scanning at 300dpi), or take a photo using a smartphone or digital camera (we recommend using the "square" image option). 
If scanning a record which has a company sleeve or plain paper sleeve, then please remove it first. 
Please only submit images that you have created yourself, we can't accept images from eBay etc for copyright reasons.

The images are uploaded to a cloud storage bucket for processing

3. Crop The Image 
The 45cat style is to crop record labels to a circle, removing the black vinyl, leaving a white background. For white or pale labels, it's fine to leave a small frame of black vinyl. See "The Factory" scan to the right for an example.

This is what the function does in its current form

5. Rotate The Image 
Rotate the image so that the text is horizontal.

To be added later

7. Save The Image 
45cat accepts images in JPG format.

Saves as .png at the moment - to be changed
