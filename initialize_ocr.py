import cv2
import easy_ocr

im = cv2.imread("sample3.jpg", 1)

#イメージのシェープからイメージの種類を決める。RapidPointの画像の幅は1500ピクセルを超えない。
x, y = im.shape[:2]
if (x<1500)|(y<1500):
    #OCRをパケージ化した関数を呼ぶ、RapidPointのために定義した関数です。
    a = easy_ocr.ocr_rapidpoint(im)
    print("pO2 = ", a)

else:
    # OCRをパケージ化した関数を呼ぶ、採決結果フォームのOCRは違う関数を使用する
    #FindRegions関数はまずフォームを読み込んで、読み取りたいColumnを識別する
    c1, c2, c3, c4,c5, c6, c7, c8 = easy_ocr.divide_form_cols(im)
    #Columnに分けてからOCRに進む。C1-C2は検査項目、C3-C4は結果、C5-C6は単位、C7-C8は結果のL/H
    #上のような分け方が一番OCR精度が高い。
    a, b, c, d, e, f, g  = easy_ocr.ocr(im, c1, c2, c3, c4, c5, c6, c7, c8)
    # 次は読み取りたいColumnから必要なテキスト（PLTとT-Bilの結果）を取り出す関数です。

    #読み取った結果の必要な項目だけをピックアップして画面で表示する
    print("T-Bil = ", a, b)
    print("CRE = ", f, g)
    print("PLT = ", c, d, e)


