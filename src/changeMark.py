def changeMarkToStr(scanFilePath, n_col, n_row, message):
    """マークシートの読み取り、結果をFalse,Trueの2次元配列で返す
    Args:
        scanFilePath (String): マークシート形式を含むJPEGファイルのパス
        n_col (int): 選択肢の数(列数)
        n_row (int): 設問の数(行数)
    Returns:
        list: マークシートの読み取った結果　False,Trueの2次元配列
    """
    ### n_col = 6 # 1行あたりのマークの数
    ### n_row = 9 # マークの行数
    import numpy as np
    import cv2

    ### マーカーの設定
    marker_dpi = 120 # 画面解像度(マーカーサイズ)
    scan_dpi = 200 # スキャン画像の解像度

    # グレースケール (mode = 0)でファイルを読み込む
    marker=cv2.imread('img/setting/marker.jpg',0) 

    # マーカーのサイズを取得
    w, h = marker.shape[::-1]

    # マーカーのサイズを変更
    marker = cv2.resize(marker, (int(h*scan_dpi/marker_dpi), int(w*scan_dpi/marker_dpi)))

    ### スキャン画像を読み込む
    img = cv2.imread(scanFilePath,0)

    res = cv2.matchTemplate(img, marker, cv2.TM_CCOEFF_NORMED)

    ## makerの3点から抜き出すのを繰り返す 抜き出すときの条件は以下の通り
    margin_top = 1 # 上余白行数
    margin_bottom = 0 # 下余白行数
 
    for threshold in [0.8, 0.75, 0.7, 0.65, 0.6]:
    
        loc = np.where( res >= threshold)
        mark_area={}
        try:
            mark_area['top_x']= sorted(loc[1])[0]+10
            mark_area['top_y']= sorted(loc[0])[0]
            mark_area['bottom_x']= sorted(loc[1])[-1]-15
            mark_area['bottom_y']= sorted(loc[0])[-1]

            topX_error = sorted(loc[1])[1] - sorted(loc[1])[0]
            bottomX_error = sorted(loc[1])[-1] - sorted(loc[1])[-2]
            topY_error = sorted(loc[0])[1] - sorted(loc[0])[0]
            bottomY_error = sorted(loc[0])[-1] - sorted(loc[0])[-2]
            img = img[mark_area['top_y']:mark_area['bottom_y'],mark_area['top_x']:mark_area['bottom_x']]

            if (topX_error < 5 and bottomX_error < 5 and topY_error < 5 and bottomY_error < 5):    
                break
        except:
            continue
    
    height, width = img.shape[:2]
    cv2.imwrite('img/res2.png',img)

    # 次に，この後の処理をしやすくするため，切り出した画像をマークの
    # 列数・行数の整数倍のサイズになるようリサイズします。
    # ここでは，列数・行数の100倍にしています。
    # なお，行数をカウントする際には，マーク領域からマーカーまでの余白も考慮した行数にします。
    n_row = n_row + margin_top + margin_bottom
    img = cv2.resize(img, (n_col*100, n_row*100))
    
    imagearray = np.zeros((img.shape[0],img.shape[1]),np.uint8)
    for col in range(0,n_col+1):
        count = np.array([[max(col*100 - 30 ,0),100],[col*100 + 30 , 100],[max(col*100 - 30 ,0),n_row*100],[col*100 + 30 ,n_row*100]])
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
            area_sum.append(np.sum(tmp_img[:,col*100:(col+1)*100]))
        area_num.append(area_sum)

    ### 画像領域の合計値が，平均値の4倍以上かどうかで判断
    ### 実際にマークを縫っている場合、4.9倍から6倍　全く塗っていないので3倍があった
    ### 中央値の3倍だと、0が続いたときに使えない
    result = []
    for row_num in area_num:
        print(row_num)
        row_result = [ num > np.max(area_num)*0.2 and num > np.average(row_num)*4 and num > 20000 for num in row_num ]
        print(row_result)
        result.append(row_result)

    

    for x in range(len(result)):
        res = np.where(result[x])[0]+1
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