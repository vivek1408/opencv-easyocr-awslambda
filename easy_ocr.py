
import pandas as pd
import time

from easyocr import Reader

MODULE_PATH = "/opt/models"
MODULE_ARGS = dict(
    gpu=True,
    model_storage_directory=MODULE_PATH,
    download_enabled=True,
    user_network_directory=".",
)


def ocr(img, c1, c2, c3, c4, c5, c6, c7, c8):
    print("[INFO] OCR'ing input image...")
    # break the input languages into a comma separated list
    # 今回は日本語がないので言語リストは英語だけに設定しておいてんも構わないです。
    langs = ["en"]
    print("[INFO] OCR'ing with the following languages: {}".format(langs))
    # Divide_form_cols関数で見つけた座標データによって列に分ける
    col1 = img[:, c1:c2]  # 検査項目の列
    col2 = img[:, c3:c4]  # 結果の列
    col3 = img[:, c5:c6]  # 単位の列
    col4 = img[:, c7:c8]  # 結果のL/Hの列
    x, y = col2.shape[:2]
    reader = Reader(langs, **MODULE_ARGS)
    t1 = time.time()
    results1 = reader.readtext(col1, paragraph=False, detail=1)
    # Min_sizeは2ピクセル以下の幅の文字を無視するようなパラメータです。
    # width_thsは並んでいる文字を別々に認識するためのパラメータです。0.1に設定したら少し空いていても別々で読み込むが、0.8でしたら結構スペースが入っていても一つの言葉として読み取る。
    # Allow_Listは指定した文字の中からOCRする。
    results2 = reader.readtext(
        col2, paragraph=False, detail=1, min_size=2,
        width_ths=0.8, allowlist="1234567890."
    )
    results3 = reader.readtext(
        col3, paragraph=False, detail=1, width_ths=0.8, allowlist="1234567890^-/uL"
    )
    results4 = reader.readtext(
        col4, paragraph=False, detail=1, width_ths=0.8, allowlist="HL"
    )

    t2 = time.time()
    print("\n\n time taken = %5.3f" % (t2 - t1))
    # 下記のコードはBoundingBoxが書いたイメージを出力するためです。
    # for (bbox, text, prob) in results:
    #     # display the OCR'd text and associated probability
    #     print("[INFO]  {}".format(text))
    #     # unpack the bounding box
    #     (tl, tr, br, bl) = bbox
    #     tl = (int(tl[0]), int(tl[1]))
    #     tr = (int(tr[0]), int(tr[1]))
    #     br = (int(br[0]), int(br[1]))
    #     bl = (int(bl[0]), int(bl[1]))
    #
    #     # cleanup the text and draw the box surrounding the text along
    #     # with the OCR'd text itself
    #     text = cleanup_text(text)
    #     cv2.rectangle(col3, tl, br, (0, 255, 0), 1)
    #     cv2.putText(col3, text, (tl[0] - 10, tl[1]),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Easyocrの結果リストのタイプからPandasデータフレームに変更する。データの簡単操作のためです。

    df1 = pd.DataFrame(results1, columns=["BBox", "Text", "Prob"])
    df2 = pd.DataFrame(results2, columns=["BBox", "Text", "Prob"])
    df3 = pd.DataFrame(results3, columns=["BBox", "Text", "Prob"])
    df4 = pd.DataFrame(results4, columns=["BBox", "Text", "Prob"])
    # df3["TLx"] = df3["BBox"].apply(lambda x: x[0][0])
    # BRyはBounding boxの右下のY座標です。このY座標によって読み取りたい分だけを切り取る。
    df1["BRy"] = df1["BBox"].apply(lambda x: x[2][1])
    df2["BRy"] = df2["BBox"].apply(lambda x: x[2][1])
    df3["BRy"] = df3["BBox"].apply(lambda x: x[2][1])
    df4["BRy"] = df4["BBox"].apply(lambda x: x[2][1])
    # OCRの結果をdiskに保存する。
    # df1[["Text", "BRy"]].to_csv("col1.csv", encoding='utf-8-sig')
    # df2[["Text", "BRy"]].to_csv("col2.csv", encoding='utf-8-sig')
    # df3[["Text", "BRy"]].to_csv("col3.csv", encoding='utf-8-sig')
    # df4[["Text", "BRy"]].to_csv("col4.csv", encoding='utf-8-sig')

    # OCRした資料から必要な列だけを探して読み取る。
    # 必要な列は項目がPLTやT-Bilになっているところだけですので、それを指定します。
    # T-Bil列のY座標を計算する
    TBil_ycoord = df1.loc[(df1["Text"] == "T-Bi l") | (df1["Text"] == "T-Bil"), "BRy"]
    TBil_ycoord = TBil_ycoord.reset_index()
    TBil_ycoord = TBil_ycoord["BRy"][0]
    # PLT列のY座標を計算する
    PLT_ycoord = df1.loc[(df1["Text"] == "PLT"), "BRy"]
    PLT_ycoord = PLT_ycoord.reset_index()
    PLT_ycoord = PLT_ycoord["BRy"][0]
    # CRE列のY座標を計算する
    CRE_ycoord = df1.loc[(df1["Text"] == "CRE"), "BRy"]
    CRE_ycoord = CRE_ycoord.reset_index()
    CRE_ycoord = CRE_ycoord["BRy"][0]
    # T-Bil列のY座標から＋－15ピクセル（行が斜めになっている可能性があるから）に離れているY座標をColumn2から探し出す。これはT-Bilに対する結果です。
    TBil_res = df2.loc[
        (df2["BRy"] > TBil_ycoord - 15) & (df2["BRy"] < TBil_ycoord + 15)]
    TBil_res = TBil_res.reset_index()
    TBil_res = TBil_res["Text"][0]
    # PLT列のY座標から＋－15ピクセルに離れているY座標をColumn2から探し出す。これはPLTに対する結果です（行が斜めになっている可能性があるから）
    PLT_res = df2.loc[(df2["BRy"] > PLT_ycoord - 15) & (df2["BRy"] < PLT_ycoord + 15)]
    PLT_res = PLT_res.reset_index()
    PLT_res = PLT_res["Text"][0]

    CRE_res = df2.loc[(df2["BRy"] > CRE_ycoord - 15) & (df2["BRy"] < CRE_ycoord + 15)]
    CRE_res = CRE_res.reset_index()
    CRE_res = CRE_res["Text"][0]

    # PLT列のY座標から＋－30ピクセルに離れているY座標をColumn3から探し出す。これはPLTに対する単位です（行が斜めになっている可能性があるから）
    units_PLT = df3.loc[(df3["BRy"] > PLT_ycoord - 30) & (df3["BRy"] < PLT_ycoord + 30)]
    units_PLT = units_PLT.reset_index()
    units_PLT_final = units_PLT.sum(axis=0)["Text"]

    # PLT列のY座標から＋－15ピクセルに離れているY座標をColumn4から探し出す。これはPLTに対する結果のL/Hです（行が斜めになっている可能性があるから）
    PLT_res_LorH = df4.loc[
        (df4["BRy"] > PLT_ycoord - 15) & (df4["BRy"] < PLT_ycoord + 15)]
    PLT_res_LorH = PLT_res_LorH.reset_index()

    # T-Bil列のY座標から＋－15ピクセルに離れているY座標をColumn4から探し出すこれはT-Bilに対する結果のL / Hです
    TBil_res_LorH = df4.loc[
        (df4["BRy"] > TBil_ycoord - 15) & (df4["BRy"] < TBil_ycoord + 15)]
    TBil_res_LorH = TBil_res_LorH.reset_index()

    CRE_res_LorH = df4.loc[
        (df4["BRy"] > CRE_ycoord - 15) & (df4["BRy"] < CRE_ycoord + 15)]
    CRE_res_LorH = CRE_res_LorH.reset_index()
    if len(PLT_res_LorH):
        PLT_res_LorH = PLT_res_LorH["Text"][0]
    else:
        PLT_res_LorH = " "
    if len(TBil_res_LorH):
        TBil_res_LorH = TBil_res_LorH["Text"][0]
    else:
        TBil_res_LorH = " "
    if len(CRE_res_LorH):
        CRE_res_LorH = CRE_res_LorH["Text"][0]
    else:
        CRE_res_LorH = " "
    return TBil_res, TBil_res_LorH, PLT_res, PLT_res_LorH, units_PLT_final, CRE_res, CRE_res_LorH


def divide_form_cols(im):
    # Column毎に分けるために最小のRowだけをよみとっても結構ですのでイメージをCropしてOCRに進む。
    # これはOCRの時間を削減するためです。
    crop = im[:200, :]
    # n言語リストを設定するとき、日本語と英語に設定する。
    langs = ["ja", "en"]
    print("Performing initial OCR to figure out rows & Columns")
    reader = Reader(langs, **MODULE_ARGS)
    # OCR時間を測定するため。
    t1 = time.time()
    # Paragraph = False の設定は読み取った文字を文章にしないようにするパラメータです。
    # Detail =Trueは読み取った文字だけでなく文字のBoundingBoxと結果の信頼性を返すようなパラメータです。
    results = reader.readtext(crop, paragraph=False, detail=1)
    t2 = time.time()
    print("\n\n time taken = %5.3f" % (t2 - t1))
    # Easyocrの結果リストのタイプからPandasデータフレームに変更する。データの簡単操作のためです。
    df = pd.DataFrame(results, columns=["BBox", "Text", "Prob"])
    # 文字のBounding boxから左上のX座標と右下のX座標を切り取って新たなColumnで保存する。
    df["TLx"] = df["BBox"].apply(lambda x: x[0][0])
    df["BRx"] = df["BBox"].apply(lambda x: x[2][0])
    # ”No”のColumnを探してそれの右下のX座標を取りプラス30ピクセルを一つ目のColumn1の最初値という設定をする。
    # （30ピクセルという値は手動でPaintで画像を開いて分析して分かったものです。）
    No_xcoord_BR = df.loc[df["Text"] == "No", "BRx"]
    col1_start = No_xcoord_BR + 15 * 2
    item_xcoord_BR = df.loc[df["Text"] == "検査項目", "BRx"]
    # 同じ様にColum1のエンドは検査項目の右下のX座標＋200ピクセルという定義をする。
    col1_end = item_xcoord_BR + 100 * 2
    result_xcoord_TL = df.loc[df["Text"] == "結果", "TLx"]
    col2_start = result_xcoord_TL
    result_xcoord_BR = df.loc[df["Text"] == "結果", "BRx"]
    col2_end = result_xcoord_BR + 100
    units_xcoord_TL = df.loc[df["Text"] == "単位名称", "TLx"]
    col3_start = units_xcoord_TL - 110 * 2
    units_xcoord_BR = df.loc[df["Text"] == "単位名称", "BRx"]
    col3_end = units_xcoord_BR + 15 * 2
    col4_start = result_xcoord_BR + 60 * 2
    col4_end = result_xcoord_BR + 100 * 2
    print(col1_start, col1_end, col2_start, col2_end, col3_start, col3_end, col4_start,
        col4_end)

    return int(col1_start), int(col1_end), int(col2_start), int(col2_end), int(
        col3_start), int(col3_end), int(col4_start), int(col4_end)


def ocr_rapidpoint(im):
    print("[INFO] OCR'ing RapidPoint image...")
    # break the input languages into a comma separated list
    langs = ["en"]
    reader = Reader(langs, **MODULE_ARGS)
    results = reader.readtext(im, paragraph=False, detail=1)
    df = pd.DataFrame(results, columns=["BBox", "Text", "Prob"])
    df["BRy"] = df["BBox"].apply(lambda x: x[2][1])
    df["TLx"] = df["BBox"].apply(lambda x: x[0][0])
    df = df.sort_values(["TLx"])
    #df[["Text", "BRy", "TLx"]].to_csv("rp.csv", encoding='utf-8-sig')
    po2 = df.loc[
        (df["Text"] == "pOz") | (df["Text"] == "poz") | (df["Text"] == "pO2"), "BRy"]
    reqd_text = po2.reset_index()
    po2_ycoord = reqd_text["BRy"][0]
    po2_res = df.loc[(df["BRy"] > po2_ycoord - 40) & (df["BRy"] < po2_ycoord + 40)]
    po2_res = po2_res.reset_index()
    po2_res = po2_res["Text"][1]
    return po2_res
