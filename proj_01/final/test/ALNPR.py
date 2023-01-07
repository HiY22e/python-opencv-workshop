import numpy as np
import cv2
from PIL import Image
import pytesseract as tess


# Now we will define three functions,
# to find the unnecessary contours that openCV may identify,
# but it does not have probability of being a number plate.

# The first function to check the area range and width-height ratio
def ratioCheck(area, width, height):
    ratio = float(width) / float(height)
    if ratio < 1:
        ratio = 1 / ratio
    if (area < 1063.62 or area > 73862.5) or (ratio < 3 or ratio > 6):
        return False
    return True


# The second function to check average of image matrix
def isMaxWhite(plate):
    avg = np.mean(plate)
    if (avg >= 115):
        return True
    else:
        return False


# The third function to check the rotation of contours
def ratio_and_rotation(rect):
    (x, y), (width, height), rect_angle = rect
    if (width > height):
        angle = -rect_angle
    else:
        angle = 90 + rect_angle

    if angle > 15:
        return False

    if height == 0 or width == 0:
        return False

    area = height * width
    if not ratioCheck(area, width, height):
        return False
    else:
        return True


# Now we will write a function to clean the identified number plate
# for preprocessing before feeding to pytesseract
def clean2_plate(plate):
    gray_img = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray_img, 110, 255, cv2.THRESH_BINARY)
    if cv2.waitKey(0) & 0xff == ord('q'):
        pass
    num_contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if num_contours:
        contour_area = [cv2.contourArea(c) for c in num_contours]
        max_cntr_index = np.argmax(contour_area)

        max_cnt = num_contours[max_cntr_index]
        max_cntArea = contour_area[max_cntr_index]
        x, y, w, h = cv2.boundingRect(max_cnt)

        if not ratioCheck(max_cntArea, w, h):
            return plate, None

        final_img = thresh[y:y+h, x:x+w]
        return final_img, [x, y, w, h]

    else:
        return plate, None


# In this step, we will take an image input.
# We will perform Gaussian Blur, Sobel and morphological operations.
# After we find contours in the image and loop through each contour to identify the number plate.
# We will then clean the image contour and feed it to pytesseract to recognize the number and characters.
img = cv2.imread("chepai03.jpg")
print("Number  input image...",)
cv2.imshow("input", img)

if cv2.waitKey(0) & 0xff == ord('q'):
    pass
img2 = cv2.GaussianBlur(img, (3, 3), 0)
img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

img2 = cv2.Sobel(img2, cv2.CV_8U, 1, 0, ksize=3)
_, img2 = cv2.threshold(img2, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

element = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(17, 3))
morph_img_threshold = img2.copy()
cv2.morphologyEx(src=img2, op=cv2.MORPH_CLOSE, kernel=element, dst=morph_img_threshold)
num_contours, hierarchy = cv2.findContours(morph_img_threshold, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
cv2.drawContours(img2, num_contours, -1, (0, 255, 0), 1)


for i, cnt in enumerate(num_contours):

    min_rect = cv2.minAreaRect(cnt)

    if ratio_and_rotation(min_rect):

        x, y, w, h = cv2.boundingRect(cnt)
        plate_img = img[y:y+h, x:x+w]
        print("Number  identified number plate...")
        cv2.imshow("num plate image", plate_img)
        if cv2.waitKey(0) & 0xff == ord('q'):
            pass

        if(isMaxWhite(plate_img)):
            clean_plate, rect = clean2_plate(plate_img)
            if rect:
                fg = 0
                x1, y1, w1, h1 = rect
                x, y, w, h = x+x1, y+y1, w1, h1
                # cv2.imwrite("clena.png",clean_plate)
                plate_im = Image.fromarray(clean_plate)
                text = tess.image_to_string(plate_im, lang='chi_sim')
                print("Number  Detected Plate Text : ", text)
