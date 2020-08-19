def qrCodeToStr(filePath):
    import qrcode
    import numpy as np
    import cv2

    img = cv2.imread(filePath, cv2.IMREAD_GRAYSCALE)
    # QRコードデコード
    qr = cv2.QRCodeDetector()

    data, points, straight_qrcode = qr.detectAndDecode(img)
    return data