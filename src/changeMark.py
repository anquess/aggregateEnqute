def changeMarkToStr(scanFilePath, n_col, n_row):
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

    threshold = 0.65
    loc = np.where( res >= threshold)

    mark_area={}

    try:
        mark_area['top_x']= min(loc[1])
        mark_area['top_y']= min(loc[0])
        mark_area['bottom_x']= max(loc[1])
        mark_area['bottom_y']= max(loc[0])
        img = img[mark_area['top_y']:mark_area['bottom_y'],mark_area['top_x']:mark_area['bottom_x']]
    except ValueError as identifier:
        print("値がおかしいです: {}".format(identifier))
        return 'error'
    except KeyError as identifier:
        print("キーが間違っています: {}".format(identifier))
        return 'error'
    
    # 次に，この後の処理をしやすくするため，切り出した画像をマークの
    # 列数・行数の整数倍のサイズになるようリサイズします。
    # ここでは，列数・行数の100倍にしています。
    # なお，行数をカウントする際には，マーク領域からマーカーまでの余白も考慮した行数にします。

    margin_top = 1 # 上余白行数
    margin_bottom = 0 # 下余白行数

    n_row = n_row + margin_top + margin_bottom

    img = cv2.resize(img, (n_col*100, n_row*100))

    ### ブラーをかける
    img = cv2.GaussianBlur(img,(5,5),0)

    ### 50を閾値として2値化
    res, img = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    ### 白黒反転
    img = 255 - img

    cv2.imwrite('img/res.png',img)

    # マークの認識

    ### 結果を入れる配列を用意
    result = []
    
    ### 行ごとの処理(余白行を除いて処理を行う)
    for row in range(margin_top, n_row - margin_bottom):
        
        ### 処理する行だけ切り出す
        tmp_img = img [row*100:(row+1)*100,]
        area_sum = [] # 合計値を入れる配列

        ### 各マークの処理
        for col in range(n_col):

            ### NumPyで各マーク領域の画像の合計値を求める
            area_sum.append(np.sum(tmp_img[:,col*100:(col+1)*100]))

        ### 画像領域の合計値が，中央値の3倍以上かどうかで判断
        result.append(area_sum > np.median(area_sum) * 3)

    return result

if __name__ == '__main__':
    import sys
    import os

    args = sys.argv
    if 3 == len(args):
        if (os.path.isfile(args[1]) and args[1][len(args[1])-4:] == '.jpg'):
            if ( len(args[2].split('_')) == 5 and args[2].split('_')[4].isdigit() and args[2].split('_')[5].isdigit()):
                n_col = int(args[2].split('_')[4])
                n_row = int(args[2].split('_')[5])
                changeMarkToStr(args[1],n_col,n_row)
            else:
                print('[ERROR]QRコードメッセージがおかしいです：' + args[2])

        elif args[1][len(args[1])-4:] == '.jpg':
            print('[ERROR]' + args[1] + 'JPEGファイルを指定してください')
        else:
            print('[ERROR]' + args[1] + 'というファイルはありません')