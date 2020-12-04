import logging
import sys
import os

import numpy
import cv2

import settings
from changeMark.markerPosition import MarkerPosition
from changeMark.enquete_optimize import Enquete

handler = logging.FileHandler('result/err.txt', encoding='utf-8')
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(name)s %(message)s"))

logger = logging.getLogger()
logger.addHandler(handler)
logger = logging.getLogger(__name__)


def changeMarkToStr(scanFilePath, n_col, n_row, message):
    """マークシートの読み取り、結果をFalse,Trueの2次元配列で返す
    Args:
        scanFilePath (String): マークシート形式を含むJPEGファイルのパス
        n_col (int): 選択肢の数(列数)
        n_row (int): 設問の数(行数)
    Returns:
        list: マークシートの読み取った結果　False,Trueの2次元配列
    """
    marker_img = get_marker_image()
    enquete_img = cv2.imread(scanFilePath,0)
    margin_top = settings.margin_top
    margin_bottom = settings.margin_bottom

    enquete = Enquete(enquete_img, marker_img, n_row, n_col, margin_top, margin_bottom)
    img = enquete.optimization_for_mark()

    result_bool_list = get_marksheet_result_bool_list(img, n_row, n_col, margin_top, margin_bottom)
    return result_bool_list_to_result_message(message, scanFilePath, result_bool_list)

def get_marker_image() -> numpy.ndarray:
    """scan_dpi に合わせたmarkerを作成

    Returns:
        numpy.ndarray: markerの画像を配列化したもの
    """
    marker_dpi = settings.marker_dpi
    scan_dpi = settings.scan_dpi
    marker_file_path = settings.marker_file_path    
    marker = cv2.imread(marker_file_path,0) 
    w, h = marker.shape[::-1]
    return cv2.resize(marker, (int(h*scan_dpi/marker_dpi), int(w*scan_dpi/marker_dpi)))

def get_marksheet_result_bool_list(img, n_row, n_col, margin_top, margin_bottom) -> list:
    """img(マークシート画像)から判定結果をboolの2次元リストで取得

    Args:
        img (image): マーカー範囲で切り出したマークシートの画像
        n_row (int): マークシートの行数
        n_col (int): マークシートの列数
        margin_top (int): 上部の空白行の数
        margin_bottom (int): 下部の空白行の数

    Returns:
        list: img(マークシート画像)から判定結果をboolの2次元リスト
    """
    area_num = get_marksheet_count_black(img, n_row, n_col, margin_top, margin_bottom)
    result = []
    for row_num in area_num:
        row_result = [ num > numpy.max(area_num)*0.2 and num > numpy.average(row_num)*4 and num > 5000 for num in row_num ]
        result.append(row_result)

        logger.info(row_num)
        logger.info(row_result)
    return result

def get_marksheet_count_black(img, n_row, n_col, margin_top, margin_bottom) -> list:
    """マークシートの各セル内の黒く塗れたドット数を数えて、結果を2次元配列で返す

    Args:
        img (image): マーカー範囲で切り出したマークシートの画像
        n_row (int): マークシートの行数
        n_col (int): マークシートの列数
        margin_top (int): 上部の空白行の数
        margin_bottom (int): 下部の空白行の数

    Returns:
        list: マークシートの各セル内の黒く塗れたドット数を数えた結果を2次元配列
    """
    area_num = []
    for row in range(margin_top, n_row - margin_bottom):
        tmp_img = img [row*100:(row+1)*100,]
        area_sum = []
        for col in range(n_col):
            area_sum.append(numpy.sum(tmp_img[:,col*100:(col+1)*100]))
        area_num.append(area_sum)
    return area_num

def result_bool_list_to_result_message(message,scanFilePath, result_bool_list) -> str:
    """result_bool_list boolの2次元配列から、一次元のテキスト配列に変更
       ex:
        ['img\\enquete\\20201124131852703-015.jpg', 'TACC', '197', 'None', 'None']
        ['img\\enquete\\20201124131852703-016.jpg', 'TACC', '197', 3, 1]

    Returns:
        str: 一次元のテキスト配列
    """
    for raw in range(len(result_bool_list)):
        res = numpy.where(result_bool_list[raw])[0]+1
        if len(res)>1:
            message.append('multi answer:' + str(res))
        elif len(res)==1:
            message.append(res[0])
        else:
            message.append('None')
    message.insert(0,scanFilePath)
    return message

if __name__ == '__main__':

    args = sys.argv
    if 3 == len(args):
        if (os.path.isfile(args[1]) and args[1][len(args[1])-4:] == '.jpg'):
            if ( len(args[2].split('_')) == 6 and args[2].split('_')[4].isdigit() and args[2].split('_')[5].isdigit()):
                n_col = int(args[2].split('_')[4])
                n_row = int(args[2].split('_')[5])
                changeMarkToStr(args[1],n_col,n_row)
            else:
                logger.error('QRコードメッセージがおかしいです：' + args[2])

        elif args[1][len(args[1])-4:] == '.jpg':
            logger.error(args[1] + 'JPEGファイルを指定してください')
        else:
            logger.error(args[1] + 'というファイルはありません')