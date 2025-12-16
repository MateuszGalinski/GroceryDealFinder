import cv2
import numpy as np
import pytesseract

def extract_text(image_path) -> str:
    img = cv2.imread(image_path)
    if img is None:
        print("Nie znaleziono pliku.")
        return ""

    # debug_img = img.copy()
    h_img, w_img, _ = img.shape

    tol = 30
    # target_yellow = np.array([9, 231, 255]) 
    
    lower_yellow = np.array([max(0, 9 - tol), max(0, 231 - tol), max(0, 100 - tol)])
    upper_yellow = np.array([min(255, 9 + tol), min(255, 231 + tol), min(255, 255)])

    mask = cv2.inRange(img, lower_yellow, upper_yellow)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    found_items = [""]

    for cnt in contours:
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        
        x, y, w, h = cv2.boundingRect(approx)
        area = w * h

        if area < 2000 or area > 150000:
            continue

        if not (4 <= len(approx) <= 6):
            continue

        aspect = w / float(h)
        if not (0.5 < aspect < 3.2):
            continue

        margin_top = 0
        if aspect > 2.5 or h < 80:
            margin_bottom = 250 - h + 400
        else:
            margin_bottom = int(h * 2.5)
        margin_right = 250 - w + 300
        margin_left = 0

        roi_y1 = max(0, y - margin_top)
        roi_y2 = min(h_img, y + h + margin_bottom)
        roi_x1 = max(0, x - margin_left)
        roi_x2 = min(w_img, x + w + margin_right)

        roi = img[roi_y1:roi_y2, roi_x1:roi_x2]

        # Rysowanie na obrazku wynikowym
        # Niebieski = wykryta żółta plama (kotwica)
        # cv2.rectangle(debug_img, (x, y), (x+w, y+h), (255, 0, 0), 3)
        # Zielony = obszar wysłany do OCR
        # cv2.rectangle(debug_img, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)

        # OCR Processing
        # Binaryzacja ROI przed OCR dla lepszego wyniku
        # roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # Wzmocnienie kontrastu
        # roi_processed = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        text = pytesseract.image_to_string(roi, lang='pol', config='--psm 6')
        clean_text = " ".join(t.strip() for t in text.split())

        if len(clean_text) > 3:
            found_items.append(clean_text)

    # for item in found_items:
    #     print(item)

    # cv2.imwrite("debug_img.jpg", debug_img)
    return "\n".join(found_items).strip()

from env import TESSERACT_DIR
pytesseract.pytesseract.tesseract_cmd = TESSERACT_DIR
    
if __name__ == "__main__":
    extract_text("scrapers/biedronka_pages/page_0.png")