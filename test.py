import config
import mysql.connector

def get_conn(cred):
    db_cred = cred
    conn = mysql.connector.connect(**db_cred)
    return conn
passport_no = '58027459'
# q = f'''select * from data2023
#     where ID='{passport_no}';
#    '''
# data_append = ('2024/08/21 18:53:08', 'OK', 507975080, '5284', '{"responseStatus":"OK","yAfastVersion":"6.6.156","verifyCode":"5284","callerId":"0799405284","callsCount":1,"bilingPerCall":0.1,"biling":"0.10","errors":{},"callsTimeout":9,"campaignId":"YA-24054-025089532-Yemot-1724246589311468"}')
# q = '''INSERT INTO `form2011`.`code_storage`
#             (`otp_date`,`status`,`phone_number`,`verify_code`,`response`)
#             VALUES(%s,%s,%s,%s,%s);'''
# db = get_conn(config.master_db_cred)
# mycursor = db.cursor()
# mycursor.execute(q,data_append)
# data2023 = mycursor.fetchall()
data2023 = ('ביליצר 35711415', '35711415', '8375', '55', '48484', '21/08/2024 21:26:59', '', '', '', 'detailsUpdateForm', '', '', '', '', '', '', '', '')
print(data2023[:10])