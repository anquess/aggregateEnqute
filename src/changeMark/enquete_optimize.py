import numpy
import cv2

import settings
from changeMark.markerPosition import MarkerPosition

class Enquete(object):
    def __init__(self, enquete_img, marker_img, n_row, n_col, margin_top, margin_bottom):
        self.enquete_img = enquete_img
        self.marker_img = marker_img
        self.n_row = n_row + margin_top + margin_bottom
        self.n_col = n_col
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom

    def get_marker_pos(self) -> list:
        """self.enquete_imgからmarkerの位置を探し、複数ある位置をリスト形式で返す

        Returns:
            list: [x, y]座標位置のリスト
        """
        res = cv2.matchTemplate(self.enquete_img, self.marker_img, cv2.TM_CCOEFF_NORMED)
        w, h = self.marker_img.shape[::-1]

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

    def cut_out_img(self) -> numpy.ndarray:
        """marker_positionsの範囲でimgを画像切り出す

        Returns:
            numpy.ndarray: 切り出した後の画像
        """
        marker_postions = self.get_marker_pos()
        marker_postions = numpy.sort(marker_postions, axis=0)
        mark_area={}
        mark_area['top_x'] = marker_postions[0][0]
        mark_area['top_y'] = marker_postions[0][1]
        mark_area['bottom_x'] = marker_postions[-1][0]
        mark_area['bottom_y'] = marker_postions[-1][1]

        return self.enquete_img[mark_area['top_y']:mark_area['bottom_y'],mark_area['top_x']:mark_area['bottom_x']]

    def optimization_for_mark(self) -> numpy.ndarray:
        """マーク範囲で切り出したimg画像をアンケートしやすい形
        縦横サイズ変更　(100 x n_col)    x   (100 x n_row)
        ぼかして、2値化、白黒反転

        Returns:
            numpy.ndarray: 最適化された画像
        """
        result_img = cv2.resize(self.cut_out_img(), (self.n_col * 100, self.n_row * 100))
        result_img = cv2.medianBlur(result_img,3)
        res, result_img = cv2.threshold(result_img, 0, 255, cv2.THRESH_OTSU)
        return 255 - result_img
