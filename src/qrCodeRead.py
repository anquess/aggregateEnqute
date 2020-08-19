def qrCodeToStr(filePath):
    """QRコードから文字列を読み取る

    Args:
        filePath (String): QRコードを含む画像ファイルのパス

    Returns:
        String: QRコードを読み取った結果(失敗したnullString)
    """
    import qrcode
    import numpy as np
    import cv2

    img = cv2.imread(filePath, cv2.IMREAD_GRAYSCALE)
    # QRコードデコード
    qr = cv2.QRCodeDetector()

    data, points, straight_qrcode = qr.detectAndDecode(img)
    return data