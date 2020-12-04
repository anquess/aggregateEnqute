import logging

import numpy
import cv2

import settings


handler = logging.FileHandler('result/err.txt', encoding='utf-8')
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(name)s %(message)s"))

logger = logging.getLogger()
logger.addHandler(handler)
logger = logging.getLogger(__name__)


class NotCutOutException(Exception):
    pass

def get_angle(res, w, h):
    loc = numpy.where( res >= 0.8 )
    square_pt = []
    temp_pt = []
    for pt in zip(*loc[::-1]):
        print('pt', pt)
        if len(temp_pt) == 0 or (abs(numpy.average(temp_pt[0], axis=0) - pt[0]) > w and abs(numpy.average(temp_pt[0], axis=1) - pt[1]) > h):
            temp_pt[0].append(pt)
        elif len(temp_pt) == 1 or (abs(numpy.average(temp_pt[1], axis=0) - pt[0]) > w and abs(numpy.average(temp_pt[1], axis=1) - pt[1]) > h):
            temp_pt[1].append(pt)
        elif len(temp_pt) == 2 or (abs(numpy.average(temp_pt[2], axis=0) - pt[0]) > w and abs(numpy.average(temp_pt[2], axis=1) - pt[1]) > h):
            temp_pt[2].append(pt)
        elif len(temp_pt) == 1 or (abs(numpy.average(temp_pt[3], axis=0) - pt[0]) > w and abs(numpy.average(temp_pt[3], axis=1) - pt[1]) > h):
            temp_pt[3].append(pt)
        else:
            print("erro")

def get_marker() -> numpy.ndarray:
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


def cut_out(img, loc) -> list:
    """markerに合わせて画像を切り出し

    Args:
        img (ndarry): 切り出したい画像
        loc (array): マーカーの位置情報

    Raises:
        NotCutOutException: 

    Returns:
        list: [description]
    """
    mark_area={}
    try:
        mark_area['top_x'] = sorted(loc[1])[0] + 10
        mark_area['top_y'] = sorted(loc[0])[0]
        mark_area['bottom_x'] = sorted(loc[1])[-1] - 15
        mark_area['bottom_y'] = sorted(loc[0])[-1]

        topX_error = sorted(loc[1])[1] - sorted(loc[1])[0]
        bottomX_error = sorted(loc[1])[-1] - sorted(loc[1])[-2]
        topY_error = sorted(loc[0])[1] - sorted(loc[0])[0]
        bottomY_error = sorted(loc[0])[-1] - sorted(loc[0])[-2]
        if (topX_error < 5 and bottomX_error < 5 and topY_error < 5 and bottomY_error < 5):
            return img[mark_area['top_y']:mark_area['bottom_y'],mark_area['top_x']:mark_area['bottom_x']]
        else:
            return img
    except:
        raise NotCutOutException('')
    return img

def changeMarkToStr(scanFilePath, n_col, n_row, message):
    """マークシートの読み取り、結果をFalse,Trueの2次元配列で返す
    Args:
        scanFilePath (String): マークシート形式を含むJPEGファイルのパス
        n_col (int): 選択肢の数(列数)
        n_row (int): 設問の数(行数)
    Returns:
        list: マークシートの読み取った結果　False,Trueの2次元配列
    """
    marker = get_marker()

    ### スキャン画像を読み込む
    img = cv2.imread(scanFilePath,0)
    res = cv2.matchTemplate(img, marker, cv2.TM_CCOEFF_NORMED)
    w, h = marker.shape[::-1]
    get_angle(res, w, h)
    ## makerの3点から抜き出すのを繰り返す 抜き出すときの条件は以下の通り
    for threshold_percent in range(settings.threshold_start,
     settings.threshold_stop, settings.threshold_step):
    
        loc = numpy.where( res >= threshold_percent / 100)
        try:
            img2 = cut_out(img, loc)
            if img2 == img:
                continue
            else:
                img = img2
                break
        except:
            continue
    
    height, width = img.shape[:2]
    cv2.imwrite('img/res2.png',img)

    # 次に，この後の処理をしやすくするため，切り出した画像をマークの
    # 列数・行数の整数倍のサイズになるようリサイズします。
    # ここでは，列数・行数の100倍にしています。
    # なお，行数をカウントする際には，マーク領域からマーカーまでの余白も考慮した行数にします。
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