import logging

import numpy
import cv2

import settings
from changeMark.markerPosition import MarkerPosition


handler = logging.FileHandler('result/err.txt', encoding='utf-8')
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(name)s %(message)s"))

logger = logging.getLogger()
logger.addHandler(handler)
logger = logging.getLogger(__name__)


class NotCutOutException(Exception):
    pass

def get_marker_pos(img, marker) -> list:
    """imgからmarkerの位置を探し、複数ある位置をリスト形式で返す

    Args:
        img ([image]):markerを探し先の画像 
        marker ([image]): 探す画像

    Returns:
        list: [x, y]座標位置のリスト
    """
    res = cv2.matchTemplate(img, marker, cv2.TM_CCOEFF_NORMED)
    w, h = marker.shape[::-1]

    loc = numpy.where( res >= settings.threshold / 100)
    square_pt = []
    for pt in zip(*loc[::-1]):
        if len(square_pt) == 0:
            square_pt.append(MarkerPosition(w, h, pt[0], pt[1]))
        else:
            flg = False
            for pos in square_pt:
                if pos.is_near_pos(pt[0], pt[1]):
                    pos.append(pt[0], pt[1])
                    flg = True
                    break
            if not flg:
                square_pt.append(MarkerPosition(w, h, pt[0], pt[1]))
    center_postions = []
    for center in square_pt:
        center_postions.append(center.get_center())
    return center_postions

def get_marker_image() -> numpy.ndarray:
    """scan_dpi に合わせたmarkerを作成

    Returns:
        numpy.ndarray: markerの画像を配列化したもの
    """
    marker_dpi = settings.marker_dpi
    scan_dpi = settings.scan_dpi
    marker_file_path = settings.marker_file_path
    
    marker = cv2.imread(marker_file_path,0) 

    # マーカーのサイズを変更
    w, h = marker.shape[::-1]
    return cv2.resize(marker, (int(h*scan_dpi/marker_dpi), int(w*scan_dpi/marker_dpi)))

def cut_out_img(img, marker_postions) -> numpy.ndarray:
    """marker_positionsの範囲でimgを画像切り出す

    Args:
        img (image): 切り出す前の画像
        marker_postions (list): 切り出す位置(4点)

    Returns:
        numpy.ndarray: 切り出した後の画像
    """
    marker_postions = numpy.sort(marker_postions, axis=0)
    mark_area={}
    mark_area['top_x'] = marker_postions[0][0]
    mark_area['top_y'] = marker_postions[0][1]
    mark_area['bottom_x'] = marker_postions[-1][0]
    mark_area['bottom_y'] = marker_postions[-1][1]

    return img[mark_area['top_y']:mark_area['bottom_y'],mark_area['top_x']:mark_area['bottom_x']]
    

def changeMarkToStr(scanFilePath, n_col, n_row, message):
    """マークシートの読み取り、結果をFalse,Trueの2次元配列で返す
    Args:
        scanFilePath (String): マークシート形式を含むJPEGファイルのパス
        n_col (int): 選択肢の数(列数)
        n_row (int): 設問の数(行数)
    Returns:
        list: マークシートの読み取った結果　False,Trueの2次元配列
    """
    marker = get_marker_image()
    img = cv2.imread(scanFilePath,0)

    marker_postions = get_marker_pos(img, marker)

    img = cut_out_img(img, marker_postions)

    cv2.imwrite('img/res2.png',img)

    # 次に，この後の処理をしやすくするため，切り出した画像をマークの
    # 列数・行数の整数倍のサイズになるようリサイズします。
    # ここでは，列数・行数の100倍にしています。
    # なお，行数をカウントする際には，マーク領域からマーカーまでの余白も考慮した行数にします。
    height, width = img.shape[:2]
    margin_top = settings.margin_top
    margin_bottom = settings.margin_bottom

    n_row = n_row + margin_top + margin_bottom
    img = cv2.resize(img, (n_col*100, n_row*100))
    
    imagearray = numpy.zeros((img.shape[0],img.shape[1]),numpy.uint8)
    for col in range(0,n_col+1):
        count = numpy.array([[max(col*100 - 30 ,0),100],[col*100 + 30 , 100],[max(col*100 - 30 ,0),n_row*100],[col*100 + 30 ,n_row*100]])
        cv2.fillPoly(img, pts=[count], color=(255,255))

    ### ブラーをかける
    
#    img = cv2.GaussianBlur(img,(1,1),0)
    img = cv2.medianBlur(img,3)
    cv2.imwrite('img/res3.png',img)
    ### 50を閾値として2値化
#    res, img = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    res, img = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)

    ### 白黒反転
    img = 255 - img
    cv2.imwrite('img/res.png',img)

    # マークの認識

    ### 結果を入れる配列を用意
    area_num = []
    ### 行ごとの処理(余白行を除いて処理を行う)
    for row in range(margin_top, n_row - margin_bottom):
        
        ### 処理する行だけ切り出す
        tmp_img = img [row*100:(row+1)*100,]
        area_sum = [] # 合計値を入れる配列

        ### 各マークの処理
        for col in range(n_col):

            ### NumPyで各マーク領域の画像の合計値を求める
            area_sum.append(numpy.sum(tmp_img[:,col*100:(col+1)*100]))
        area_num.append(area_sum)

    ### 画像領域の合計値が，平均値の4倍以上かどうかで判断
    ### 実際にマークを縫っている場合、4.9倍から6倍　全く塗っていないので3倍があった
    ### 中央値の3倍だと、0が続いたときに使えない
    result = []
    for row_num in area_num:
        print(row_num)
        row_result = [ num > numpy.max(area_num)*0.2 and num > numpy.average(row_num)*4 and num > 20000 for num in row_num ]
        print(row_result)
        result.append(row_result)

    

    for x in range(len(result)):
        res = numpy.where(result[x])[0]+1
        if len(res)>1:
            message.append('multi answer:' + str(res))
        elif len(res)==1:
            message.append(res[0])
        else:
            message.append('None')
    message.insert(0,scanFilePath)
    return message

if __name__ == '__main__':
    import sys
    import os

    args = sys.argv
    if 3 == len(args):
        if (os.path.isfile(args[1]) and args[1][len(args[1])-4:] == '.jpg'):
            if ( len(args[2].split('_')) == 6 and args[2].split('_')[4].isdigit() and args[2].split('_')[5].isdigit()):
                n_col = int(args[2].split('_')[4])
                n_row = int(args[2].split('_')[5])
                changeMarkToStr(args[1],n_col,n_row)
            else:
                print('[ERROR]QRコードメッセージがおかしいです：' + args[2])

        elif args[1][len(args[1])-4:] == '.jpg':
            print('[ERROR]' + args[1] + 'JPEGファイルを指定してください')
        else:
            print('[ERROR]' + args[1] + 'というファイルはありません')