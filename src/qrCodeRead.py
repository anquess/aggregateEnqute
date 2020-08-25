import sys
import os
def qrCodeToStr(filePath):
    """QRコードから文字列を読み取る

    Args:
        filePath (String): QRコードを含む画像ファイルのパス

    Returns:
        String: QRコードを読み取った結果(失敗したnullString)
    """
    import cv2

    img = cv2.imread(filePath, cv2.IMREAD_GRAYSCALE)
    # QRコードデコード
    qr = cv2.QRCodeDetector()
    data,_,_ = qr.detectAndDecode(img)
    print(data)
    return data

if __name__ == '__main__':
    args = sys.argv
    if 2 == len(args):
        if os.path.isfile(args[1]):
            qrCodeToStr(args[1])
        else:
            print(args[1] + 'というファイルはありません')
    else:
        print(args + '引数は1つです')