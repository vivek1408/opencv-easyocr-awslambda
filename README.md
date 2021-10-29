# nedo_ocr
Synopsis: initialize_ocr.py takes an image as input and depending on the size of the image calls the appropriate OCR module in easy_ocr.py

There are 2 types of documents to be OCR'd:
Type 1: Blood Test report form (5000x4850)
Type 2: Rapid Point results (1344x4392)

initialize_ocr.py calls appropriate function in easy_ocr.py when one dimension of the input image is lesser than 1500 pixels.



Aim of this project is to OCR 2 kinds of documents that are related to the blood test of an indiviudual.
The first one is the blood test report that looks like this:

![alt text](https://github.com/vivek1408/opencv-easyocr-awslambda/blob/main/Images/type1/sample2.jpg?raw=true)

From the above document the required fields for extraction include T-Bil, CRE and PLT and their respective results and units.

We also need the pO2 value from the 2nd document.

![alt text](https://github.com/vivek1408/opencv-easyocr-awslambda/blob/main/Images/RAPIDPoint/s2.jpg?raw=true)

In initialize_ocr.py we read in the image to be OCR'd using openCV and depending on the dimensions of the input image we call the appropriate OCR function from the easy_ocr.py module.


For documents of the Type 1 the function will use the first few rows of the image to first split the document into 4 columns of interest ie Item, Result, Result LorH and units. Once the document is split into the above columns, OCR can be done seperately on each column. This increases OCR accuracy and decreases time required for the OCR engine to work since the input image is very large and dividing into columns will reduce the pixels that the OCR engine needs to analyze.

Once that is done, we will run through the columns and find the required text (T-Bil, PLT and CRE) and find the corresponding results and units by matching the Y coordinates of the bounding boxes returned by the OCR engine.

These results are then stored in a MySQL database in AWS RDS for future. 

The intermediate individual column CSV files are stored in S3 for other purposes.

Essentially the results of OCR of form type 1 looks like this:

![alt text](https://github.com/vivek1408/opencv-easyocr-awslambda/blob/main/Images/type1/sample2_res.jpg?raw=true)



And the results of OCR of RAPIDPoint results looks like this:

![alt text](https://github.com/vivek1408/opencv-easyocr-awslambda/blob/main/Images/RAPIDPoint/s2res.JPG?raw=true)


Installation: 
Required packages: easyocr, opencv-python

install python3, then run the foollowing after updating pip package:
pip3 install opencv-python
pip3 install easyocr

confirm installations with:
import cv2
import easyocr
print(cv2.__version__)
print(easyocr.__version__)

Produced by Vivek-san
