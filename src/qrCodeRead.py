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

    if data == '':
        print('[ERROR]' + filePath + 'からQRコードが見つかりませんでした')
    else:
        print(data)
    return data

if __name__ == '__main__':
    args = sys.argv
    if 2 == len(args):
        if (os.path.isfile(args[1]) and args[1][len(args[1])-4:] == '.jpg'):
            qrCodeToStr(args[1])
        elif args[1][len(args[1])-4:] == '.jpg':
            print('[ERROR]' + args[1] + 'JPEGファイルを指定してください')
        else:
            print('[ERROR]' + args[1] + 'というファイルはありません')
    else:
        print('[ERROR]' + args + '引数は1つです')