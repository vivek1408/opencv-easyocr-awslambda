import cv2
import boto3
import os
import json
import easy_ocr
from datetime import datetime

BUCKET_NAME = os.environ.get("BUCKET_NAME")
RDS_INVOCATION_LAMBDA = os.environ.get("RDS_INVOCATION_LAMBDA")


def lambda_handler(event, context):
    print(event)
    records = event["Records"]
    s3 = boto3.client('s3')
    filepath = "Images\\RAPIDPoint\\s1.jpg"

    for record in records:
        key = record["s3"]["object"]["key"]
        filename = key.split("/")[-1]
        print(key)
        filepath = f"/tmp/{filename}"
        print(filepath)
        filename = filename.split(".")[0]
        with open(filepath, 'wb') as f:
            s3.download_fileobj(BUCKET_NAME, key, f)

    im = cv2.imread(filepath, 1)

    time = datetime.now()
    # イメージのシェープからイメージの種類を決める。RapidPointの画像の幅は1500ピクセルを超えない。
    x, y = im.shape[:2]
    if (x < 1500) | (y < 1500):
        # OCRをパケージ化した関数を呼ぶ、RapidPointのために定義した関数です。
        a = easy_ocr.ocr_rapidpoint(im)
        data = {
            "doc_type": 2,
            "time": time,
            "user_id": filename,
            "result": a
        }
        print(data)

    else:
        # OCRをパケージ化した関数を呼ぶ、採決結果フォームのOCRは違う関数を使用する
        # FindRegions関数はまずフォームを読み込んで、読み取りたいColumnを識別する
        c1, c2, c3, c4, c5, c6, c7, c8 = easy_ocr.divide_form_cols(im)
        # Columnに分けてからOCRに進む。C1-C2は検査項目、C3-C4は結果、C5-C6は単位、C7-C8は結果のL/H
        # 上のような分け方が一番OCR精度が高い。
        a, b, c, d, e, f, g = easy_ocr.ocr(im, c1, c2, c3, c4, c5, c6, c7, c8)
        # 次は読み取りたいColumnから必要なテキスト（PLTとT-Bilの結果）を取り出す関数です。

        # 読み取った結果の必要な項目だけをピックアップして画面で表示する
        data = {
            "doc_type": 1,
            "user_id": filename,
            "time": time,
            "T-Bil": [a, b, " "],
            "CRE": [f, g, " "],
            "PLT": [c, d, e]
        }

        print(data)
    # Connect to the RDS dump lambda function and pass the OCR data to that function.
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(FunctionName=RDS_INVOCATION_LAMBDA,
                         InvocationType="Event",
                         Payload=json.dumps(data)
                         )

    return {
        "statusCode": 200,
        "body": data,
        "message": "RDS Lambda invocation successful!"
    }

# print("callinghandler function...")
# lambda_handler({}, None)
