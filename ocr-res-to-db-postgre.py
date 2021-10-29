import psycopg2
import os
import sys

RDS_NAME = os.environ.get("RDS_NAME")
endpoint = RDS_NAME
username = "postgres"
password = "ticu1234"
database_name = "ocrres"


def lambda_handler(event, context):
    connection = psycopg2.connect(
        database="postgres",
        user=username,
        password=password,
        host=endpoint,
        port='5432'
    )
    if event["doc_type"] == 1:
        try:
            with connection:
                with connection.cursor() as cursor:
                    # Create a new record

                    sql = "INSERT INTO `res_type1` (`user_id`, `time_now`, `item_name`, `result`, `resultLorH`, `units`) VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (
                        event["user_id"], event["time"], "T-Bil", event["T-Bil"][0], event["T-Bil"][1],
                        event["T-Bil"][2]))
                    cursor.execute(sql, (
                        event["user_id"], event["time"], "CRE", event["CRE"][0], event["CRE"][1], event["CRE"][2]))
                    cursor.execute(sql, (
                        event["user_id"], event["time"], "PLT", event["PLT"][0], event["PLT"][1], event["PLT"][2]))
                    connection.commit()
                    sql = "select * from res_type1"
                    cursor.execute(sql)
                    rows = cursor.fetchmany(3)
                    print(rows)

        except Exception as e:
            print("[ERROR] in writing results to res_type1 ", e)
            sys.exit(1)


    else:
        try:
            with connection:
                with connection.cursor() as cursor:
                    # Create a new record
                    sql = "INSERT INTO `res_type2` (`user_id`,`time_now`, `item_name`, `result` ) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (event["user_id"], event["time"], "po2", event["result"]))
                    connection.commit()

                with connection.cursor() as cursor:
                    sql = "select * from res_type2"
                    cursor.execute(sql)
                    rows = cursor.fetchmany(3)
                    print(rows)
        except Exception as e:

            print("[ERROR] in writing results to res_type2 ", e)
            sys.exit(1)
