import sys
import os
import logging

handler = logging.FileHandler('result/err.txt', encoding='utf-8')
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(name)s %(message)s"))

logger = logging.getLogger()
logger.addHandler(handler)
logger = logging.getLogger(__name__)

def qrCodeToStr(filePath):
    """QRコードから文字列を読み取る
    Args:
        filePath (String): QRコードを含む画像ファイルのパス
    Returns:
        String: QRコードを読み取った結果(失敗したnullString)
    """
    import cv2
    try:
        img = cv2.imread(filePath, cv2.IMREAD_GRAYSCALE)
        # QRコードデコード
        qr = cv2.QRCodeDetector()
        data, points, straight_qrcode = qr.detectAndDecode(img)

        if points == '' :
            logger.warn('QRコードが見つかりません。,%s', filePath)
            return None
        elif data == '':
            logger.error('QRコードが解読できません。,%s', filePath)
            return None
        else:
            logger.info(data)
    except Exception as e:
        logger.error('QRコードが見つかりません。,%s,エラーコード：%s', filePath, str(e))
        return None
    return data

if __name__ == '__main__':
    args = sys.argv
    if 2 == len(args):
        if (os.path.isfile(args[1]) and args[1][len(args[1])-4:] == '.jpg'):
            qrCodeToStr(args[1])
        elif args[1][len(args[1])-4:] == '.jpg':
            logger.error('JPEGファイルを指定してください')
        else:
            logger.error(str(args[1]) + 'というファイルはありません')
    else:
        logger.error('引数は1つです')