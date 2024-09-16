
import json
import config
import requests
from gevent.pywsgi import WSGIServer
from flask import Flask,jsonify,request, send_file, render_template
from flask_cors import CORS, cross_origin
from helpers.g_sheet_handler import GoogleSheetHandler
from datetime import datetime
from requests.exceptions import RequestException
from urllib.parse import unquote
import mysql.connector



app =   Flask(__name__)
CORS(app)

def get_conn(cred):
    db_cred = cred
    conn = mysql.connector.connect(**db_cred)
    return conn

def pop_push_func(data_list, index, data):
    data_list.pop(index)
    data_list.insert(index,data)

def append_in_code_storage(cred, data):
    q = '''INSERT INTO `form2011`.`code_storage`
            (`otp_date`,`status`,`phone_number`,`verify_code`,`response`)
            VALUES(%s,%s,%s,%s,%s);'''
    db = get_conn(cred)
    mycursor = db.cursor()
    mycursor.execute(q,data)
    db.commit()
    print('Data append in code storage')
    db.close()

def fetch_otp_from_google_sheet(passport_no, phone_no):
    try:
        q = f'''
            select * from code_storage 
            where phone_number = {phone_no} and 
            status='OK' order by otp_date desc limit 1;
            '''
        db = get_conn(config.db_cred)
        mycursor = db.cursor()
        mycursor.execute(q)
        filtered_data = mycursor.fetchone()
        # data_ = GoogleSheetHandler(sheet_name=config.SHEET_CODE_STORAGE, spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP).getsheet_records()
        db.close()
    except Exception as e:
        # logger.error(f"Error fetching otp from Google Sheets: {e}")
        return "Internal Server Error - Could not get data from Database", 500
    if filtered_data:
        latest_otp = filtered_data[3]
        return latest_otp
    return None 

@app.route('/', methods = ['GET', 'POST'])
@cross_origin(origin='*')
def home():
    date = datetime.now()

    if request.method == 'GET':
        phoneCode = request.args.get('CheckPhoneCode')
        passport_no = request.args.get('id')
        action = request.args.get('action')
        phone_no = request.args['Phone']
        try:
            # data_ = GoogleSheetHandler(sheet_name=config.SHEET_USER_DATA_GET, spreadsheet_id=config.SAMPLE_SPREADSHEET_ID).getsheet_records()
            q = f'''select * from data2023
                    where ID='{passport_no}';
                '''
            db = get_conn(config.master_db_cred)
            mycursor = db.cursor()
            mycursor.execute(q)
            data_ = mycursor.fetchall()
            # print(data_)
            # print(type(data_))
            db.close()
        except Exception as e:
            print("Exeption -", e)
            return "Internal Server Error-Could Not Get Data from Database", 500

        if passport_no == "" or (passport_no is None):
            # print("1")
            res = {}
            res["studentStatus"] = False
            res["message"] = "אתה לא נמצא ברשימות או שמספר הטלפון שלך לא מעודכן במערכת נא פנה לאחראי,You are not on the lists or your phone number is not updated in the system, please contact the manager"
            return json.dumps(res)

        # checkData = [item for item in data_ if item[11] == str(passport_no)]
        if len(data_) == 0:
            # print("2")
            res = {}
            res["studentStatus"] = False
            res["message"] = "אתה לא נמצא ברשימות או שמספר הטלפון שלך לא מעודכן במערכת נא פנה לאחראי,You are not on the lists or your phone number is not updated in the system, please contact the manager"
            return json.dumps(res)
        # db.close()

        if phoneCode is None:
            if len(passport_no) > 0 and len(phone_no) > 0:
                for data in data_:
                    if action == 'GetStudentsByid':
                        # print(data)
                        # print(data[10],data[16])
                        if data[10] == passport_no and data[16] == phone_no[1:]:
                            print("--------------------------------------- Matched for normal user ------------------------")
                            customValue = str(request.query_string, 'utf-8')
                            customResponse = [[date.strftime("%Y/%m/%d, %H:%M:%S"), 'GET', customValue]]
                            # data_ = GoogleSheetHandler(data = customResponse,
                            #             sheet_name=config.SHEET_USER_DATA_LOG,
                            #             spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
                            q = '''INSERT INTO `logs`
                                    (`log_time`,
                                    `request`,
                                    `log`)
                                    VALUES
                                    (%s,%s,%s);
                                '''
                            value = tuple(customResponse[0])
                            db = get_conn(config.db_cred)
                            mycursor = db.cursor()
                            mycursor.execute(q,value)
                            db.commit()
                            db.close()
                            response = requests.get(f'https://www.call2all.co.il/ym/api/RunTzintuk?token=025089532:7974153&callerId=RAND&phones=${phone_no}')
                            response_json = json.loads(response.text)

                            if response_json['responseStatus'] == 'ERROR':
                                data_append = [[date.strftime("%Y-%m-%d %H:%M:%S"),response_json['responseStatus'],int(phone_no),'',response.text]]
                                # GoogleSheetHandler(data = data_append, sheet_name=config.SHEET_CODE_STORAGE,
                                #             spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
                                data_append = tuple(data_append[0])
                                append_in_code_storage(config.db_cred,data_append)
                                
                                return json.dumps({
                                        "Data" : data,
                                        "Validation" : "Successful",
                                        "studentStatus": True,
                                        "CheckPhoneCodeStatus": False,
                                        "Passport Number" : passport_no,
                                        "Phone Number" : phone_no,
                                        'message' : f'Some Error occured : {response_json["message"]}'
                                        })
                            elif response_json['responseStatus'] == 'Exception':
                                data_append = [[date.strftime("%Y-%m-%d %H:%M:%S"),response_json['responseStatus'],int(phone_no),'',response.text]]
                                # GoogleSheetHandler(data = data_append, sheet_name=config.SHEET_CODE_STORAGE,
                                #             spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()

                                data_append = tuple(data_append[0])
                                append_in_code_storage(config.db_cred,data_append)

                                return json.dumps({
                                        "Data" : data,
                                        "studentStatus" : True,
                                        "CheckPhoneCodeStatus" : False,
                                        "Passport Number" : passport_no,
                                        "Phone Number" : phone_no,
                                        "Validation" : "Successful",
                                        'message' : f'Exception occured : {response_json["message"]}'
                                        })
                            else:
                                data_append = [[date.strftime("%Y-%m-%d %H:%M:%S"),response_json['responseStatus'],int(phone_no),response_json['verifyCode'],response.text]]
                                # GoogleSheetHandler(data = data_append, sheet_name=config.SHEET_CODE_STORAGE,
                                #                 spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()

                                data_append = tuple(data_append[0])
                                # print(data_append)
                                append_in_code_storage(config.db_cred,data_append)

                            # Define a mapping of indices to keys for the data list
                                # keys_mapping = {
                                #     9: "FirstName", 10: "Family", 6: "Zihuy", 7: "ZihuyType", 5: "StudyTypeID",
                                #     12: "BDE", 14: "Group", 0: "Mosd", 15: "GroupZaraeim", 23: "KolelBoker",
                                #     24: "KolelZarim", 38: "Mail", 33: "StreetNum", 32: "Street", 31: "City",
                                #     34: "Bank", 35: "Snif", 36: "Account", 39: "MosdName", 40: "MosdAdd",
                                #     41: "MosdAuthorizedName", 2: "JoiningDate", 37: "MosdId", 4: "MaritalStatus",
                                #     43: "AdminMail", 8: "Country"
                                # }

                                # # Create studentData dictionary using a dictionary comprehension
                                # studentData = {keys_mapping[i]: data[i] if len(data) > i else '' for i in keys_mapping}


                                res = json.dumps({
                                        #"studentData": studentData,
                                        "Passport Number" : passport_no,
                                        "Phone Number" : phone_no,
                                        "Validation" : "Successful",
                                        "studentStatus": True,
                                        "CheckPhoneCodeStatus": True,
                                        "PhoneLast4": f"******{phone_no[-4:]}",
                                        "message" : f"A call was sent to phone ******{phone_no[-4:]}"
                                        })

                                # GoogleSheetHandler(data = [res], sheet_name=config.SHEET_USER_DATA_FSR,spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()

                                return res
                    elif action == 'GetStudentsByMosd':
                        if data[11] == passport_no and (data[45] == phone_no[1:] or data[46] == phone_no[1:]):
                            print("----------------------- Matched for Admin ---------------------")
                            customValue = str(request.query_string, 'utf-8')
                            customResponse = [[date.strftime("%Y/%m/%d, %H:%M:%S"), 'GET', customValue]]
                            # data_ = GoogleSheetHandler(data = customResponse,
                            #             sheet_name=config.SHEET_USER_DATA_LOG,
                            #             spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
                            q = '''INSERT INTO `logs`
                                    (`log_time`,
                                    `request`,
                                    `log`)
                                    VALUES
                                    (%s,%s,%s);
                                '''
                            value = tuple(customResponse[0])
                            db = get_conn(config.db_cred)
                            mycursor = db.cursor()
                            mycursor.execute(q,value)
                            db.commit()
                            db.close()
                            response = requests.get(f'https://www.call2all.co.il/ym/api/RunTzintuk?token=025089532:7974153&callerId=RAND&phones=${phone_no}')
                            response_json = json.loads(response.text)

                            if response_json['responseStatus'] == 'ERROR':
                                data_append = [[date.strftime("%Y-%m-%d %H:%M:%S"),response_json['responseStatus'],int(phone_no),'',response.text]]
                                # GoogleSheetHandler(data = data_append, sheet_name=config.SHEET_CODE_STORAGE,
                                #             spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
                                data_append = tuple(data_append[0])
                                append_in_code_storage(config.db_cred,data_append)
                                return json.dumps({
                                        "Data" : data,
                                        "Validation" : "Successful",
                                        "studentStatus": True,
                                        "CheckPhoneCodeStatus": False,
                                        "Passport Number" : passport_no,
                                        "Phone Number" : phone_no,
                                        'message' : f'Some Error occured : {response_json["message"]}'
                                        })
                            elif response_json['responseStatus'] == 'Exception':
                                data_append = [[date.strftime("%Y-%m-%d %H:%M:%S"),response_json['responseStatus'],int(phone_no),'',response.text]]
                                # GoogleSheetHandler(data = data_append, sheet_name=config.SHEET_CODE_STORAGE,
                                #             spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
                                data_append = tuple(data_append[0])
                                append_in_code_storage(config.db_cred,data_append)
                                return json.dumps({
                                        "Data" : data,
                                        "studentStatus" : True,
                                        "CheckPhoneCodeStatus" : False,
                                        "Passport Number" : passport_no,
                                        "Phone Number" : phone_no,
                                        "Validation" : "Successful",
                                        'message' : f'Exception occured : {response_json["message"]}'
                                        })
                            else:
                                data_append = [[date.strftime("%Y-%m-%d %H:%M:%S"),response_json['responseStatus'],int(phone_no),response_json['verifyCode'],response.text]]
                                # GoogleSheetHandler(data = data_append, sheet_name=config.SHEET_CODE_STORAGE,
                                #                 spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
                                data_append = tuple(data_append[0])
                                append_in_code_storage(config.db_cred,data_append)


                            # Define a mapping of indices to keys for the data list
                                keys_mapping = {
                                    9: "FirstName", 10: "Family", 6: "Zihuy", 7: "ZihuyType", 5: "StudyTypeID",
                                    12: "BDE", 14: "Group", 0: "Mosd", 15: "GroupZaraeim", 23: "KolelBoker",
                                    24: "KolelZarim", 38: "Mail", 33: "StreetNum", 32: "Street", 31: "City",
                                    34: "Bank", 35: "Snif", 36: "Account", 39: "MosdName", 40: "MosdAdd",
                                    41: "MosdAuthorizedName", 2: "JoiningDate", 37: "MosdId", 4: "MaritalStatus",
                                    43: "AdminMail", 8: "Country"
                                }

                                # Create studentData dictionary using a dictionary comprehension
                                studentData = {keys_mapping[i]: data[i] if len(data) > i else '' for i in keys_mapping}


                                res = json.dumps({
                                        #"studentData": studentData,
                                        "Passport Number" : passport_no,
                                        "Phone Number" : phone_no,
                                        "Validation" : "Successful",
                                        "studentStatus": True,
                                        "CheckPhoneCodeStatus": True,
                                        "PhoneLast4": f"******{phone_no[-4:]}",
                                        "message" : f"A call was sent to phone ******{phone_no[-4:]}"
                                        })

                                # GoogleSheetHandler(data = [res], sheet_name=config.SHEET_USER_DATA_FSR,spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()

                                return res

                customValue = str(request.query_string, 'utf-8')
                customResponse = [[date.strftime("%d/%m/%Y, %H:%M:%S"), 'GET', customValue]]
                # data_ = GoogleSheetHandler(data = customResponse,
                #                     sheet_name=config.SHEET_USER_DATA_LOG,
                #                     spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
                q = '''INSERT INTO `logs`
                                    (`log_time`,
                                    `request`,
                                    `log`)
                                    VALUES
                                    (%s,%s,%s);
                    '''
                value = tuple(customResponse[0])
                db = get_conn(config.db_cred)
                mycursor = db.cursor()
                mycursor.execute(q,value)
                db.commit()
                db.close()
                return json.dumps({
                                "Passport Number" : passport_no,
                                "Phone Number" : phone_no,
                                "studentStatus" : False,
                                "CheckPhoneCodeStatus" : False,
                                "message" : "אתה לא נמצא ברשימות או שמספר הטלפון שלך לא מעודכן במערכת נא פנה לאחראי,You are not on the lists or your phone number is not updated in the system, please contact the manager",
                            })


            else:
                customValue = str(request.query_string, 'utf-8')
                customResponse = [[date.strftime("%d/%m/%Y, %H:%M:%S"), 'GET', customValue]]
                # data_ = GoogleSheetHandler(data = customResponse,
                #                     sheet_name=config.SHEET_USER_DATA_LOG,
                #                     spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
                q = '''INSERT INTO `logs`
                                    (`log_time`,
                                    `request`,
                                    `log`)
                                    VALUES
                                    (%s,%s,%s);
                    '''
                value = tuple(customResponse[0])
                db = get_conn(config.db_cred)
                mycursor = db.cursor()
                mycursor.execute(q,value)
                db.commit()
                db.close()

                return json.dumps(
                    {
                        "Passport Number" : passport_no,
                        "Phone Number" : phone_no,
                        "Validation" : "Failed",
                        "Error Msg":"please fill all the fields",
                    }
                )
        else :
            otp = request.args.get('CheckPhoneCode')
            if len(passport_no) > 0 and len(phone_no) > 0:
             
                for data in data_:

                    if data[10] == passport_no and data[16] == phone_no[1:]:
                        customValue = str(request.query_string, 'utf-8')
                        customResponse = [[date.strftime("%d/%m/%Y, %H:%M:%S"), 'GET', customValue]]
                        # data_ = GoogleSheetHandler(data = customResponse,
                        #             sheet_name=config.SHEET_USER_DATA_LOG,
                        #             spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
                        #response = requests.get(f'https://www.call2all.co.il/ym/api/RunTzintuk?token=025089532:7974153&callerId=RAND&phones=${phone_no}')
                        #response_json = json.loads(response.text)
                        q = '''INSERT INTO `logs`
                                    (`log_time`,
                                    `request`,
                                    `log`)
                                    VALUES
                                    (%s,%s,%s);
                            '''
                        value = tuple(customResponse[0])
                        db = get_conn(config.db_cred)
                        mycursor = db.cursor()
                        mycursor.execute(q,value)
                        db.commit()
                        db.close()

                        studentData = {
                            "FirstName": data[9] if len(data) > 9 else "",
                            "Family": data[10] if len(data) > 10 else "",
                            "Zihuy": data[6] if len(data) > 6 else "",
                            "ZihuyType": data[7] if len(data) > 7 else "",
                            "StudyTypeID":  "StudyType_" + data[5],
                            "BDE": data[12] if len(data) > 12 else "",
    				        #"MosdOLD": f"{data[0] if len(data) > 0 else ''}, {data[5] if len(data) > 5 else ''}",
    				        "Group": data[14] if len(data) > 14 else '',
                            "Mosd": data[0] if len(data) > 0 else '',
                            "GroupZaraeim": data[15] if len(data) > 15 else "",
                            "KolelBoker": data[23] if len(data) > 23 else "",
                            "KolelZarim": data[24] if len(data) > 24 else "",
                            "Mail": data[38] if len(data) > 38 else "",
                            "StreetNum": data[33] if len(data) > 33 else "",
                            "Street": data[32] if len(data) > 32 else "",
                            "City": data[31] if len(data) > 31 else "",
                            "Bank": data[34] if len(data) > 34 else "",
                            "Snif": data[35] if len(data) > 35 else "",
                            "Account": data[36] if len(data) > 36 else "",
                            "MosdName": data[39] if len(data) > 39 else "",
                            "MosdAdd": data[40] if len(data) > 40 else "",
                            "MosdAuthorizedName": data[41] if len(data) >= 41 else "",
                            "JoiningDate": data[2] if len(data) >= 2 else "",
                            "MosdId": data[37] if len(data) > 37 else "",
                            "StudyType": data[5] if len(data) > 5 else "",
                            "MaritalStatus": data[4] if len(data) > 4 else "",
                            "AdminMail": data[43] if len(data) > 43 else '',
                            "Country": data[8] if len(data) > 8 else ""
                        }

                        res = {
                                # "Data" : data,
                                "studentData": studentData,
                                "Passport Number" : passport_no,
                                "Phone Number" : phone_no,
                                "Validation" : "Successful",
                                "studentStatus": True,
                                "CheckPhoneCodeStatus": True,
                                "PhoneLast4": f"******{phone_no[-4:]}",
                                "message" : "otp validation successfull"
                                }

                        #GoogleSheetHandler(data = customResponse,
                        #           sheet_name=config.SHEET_USER_DATA_LOG,
                        #           spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
                        json_string = json.dumps(res)
                        actual_otp = fetch_otp_from_google_sheet(passport_no, phone_no)

                        if actual_otp is None:
                            return json.dumps({"message": "Could not get OTP, please try again later"})

                        return json_string if otp == actual_otp and len(otp) > 0 else json.dumps({"status": 400, "CheckPhoneCodeStatus": False, "studentStatus": True, "message": "OTP validation failed"})

                    else:
                        pass


    if request.method == 'POST':
        requestData = request.json

        requestData = json.dumps(request.json)
        decoded_string = unquote(str(requestData), encoding='utf-8')

        formData = json.loads(decoded_string)
        # print('printing form data',formData)

        customResponse = [[date.strftime("%Y/%m/%d, %H:%M:%S"), 'POST', str(decoded_string)]]
        # GoogleSheetHandler(data = customResponse, sheet_name=config.SHEET_USER_DATA_FSP, spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
        customResponse = tuple(customResponse[0])
        q = '''INSERT INTO `form_submission_logs`
                (`post_date`,
                `request`,
                `data`)
                VALUES
                (%s,%s,%s);
            '''
        db = get_conn(config.db_cred)
        mycursor = db.cursor()
        mycursor.execute(q,customResponse)
        db.commit()
        db.close()
        # preparing data to add int Bank Account sheet
        first_name = formData.get('FirstName')
        family = formData.get('Family')
        zeout = formData.get('Zeout')
        phone_no = formData.get('Tel1')
        bank = formData.get('Bank')
        snif = formData.get('Snif') # branch
        account = formData.get('Account')
        bank_date = str(date.strftime("%d/%m/%Y %H:%M:%S"))
        tofes_id = formData.get('TofesId')
        City = formData.get('City')
        Street = formData.get('Street')
        StreetNum = formData.get('StreetNum') # home
        Email = formData.get('Mail')

        list_of_lists = [''] * 20

        positions_to_add = {
            0: first_name + ' ' + family,
            1: zeout,
            2: bank,
            3: snif,
            4: account,
            5: bank_date,
            9: tofes_id
        }

        # Add elements to the specified positions
        for position, element in positions_to_add.items():
            list_of_lists[position] = element


        bank_data = [list_of_lists]

        # respo = GoogleSheetHandler(data = bank_data, sheet_name=config.BANK_ACCOUNT_SHEET, spreadsheet_id=config.BANK_ACCCOUNTS_SPREADSHEET_ID).appendsheet_records()
        bank_data = bank_data[0][:10]
        bank_data = tuple(bank_data)
        # print('bank data',bank_data)
        q = '''INSERT INTO `form2011`.`bank_account`
            (`FirstName&Family`,`Zeout`,`bank`,`snif`,`account`,`date`,`AccountByDate_and_ByF`,
            `legal`,`DONT_TOUCH`,`TofesId`)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'''
        db = get_conn(config.db_cred)
        mycursor = db.cursor()
        mycursor.execute(q,bank_data)
        db.commit()
        db.close()
        

        data_list = ["-"] * 86  # Initialize data_list with 86 "-"

        # Define a list of keys to extract from formData
        keys_to_extract = [
            'FirstName', 'Family', 'Group', 'BDE', 'Zeout', 'Tel1', 'address', 'BankToChange', 'MailToChange', 
            'ReceivingPayslip', 'StartingCollegeStudies', 'InterruptionOfStudiesInKollel', 'passportNumber', 
            'passportToIdNumber', 'City', 'Street', 'StreetNum', 'Bank', 'Snif', 'Account', 'Mail', 'IsTlush', 
            'NameMosad1', 'TypeMosad1', 'GovaTlush1', 'Numtime1', 'Ishur', 'IsMslullimudim', 'NameMosad2', 
            'Numtime2', 'Ishur2', 'DateOfCessationOfStudiesInKollel', 'IsBeginTlush', 'StartDateOfReceivingAPayslip', 
            'passportToChange', 'IdNumber', 'TofesID', 'CheckPhoneCode'
        ]

        # Loop through keys_to_extract and populate data_list
        for i, key in enumerate(keys_to_extract, start=4):
            if i < len(data_list):
                data_list[i] = formData.get(key, "-")

            else:
                # Handle the case where the index is out of range
                pass

        data_list[1] = date.strftime("%Y/%m/%d %H:%M:%S")

        resp = GoogleSheetHandler(data = [data_list], sheet_name=config.SHEET_FORM_DATA_STORAGE,spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
        q = f'''UPDATE data2023
                SET City = '{City}', 
                Street = '{Street}',
                Home = '{StreetNum}', 
                Bank = '{bank}',
                Branch = '{snif}', 
                Account = '{account}',
                Email = '{Email}'
                WHERE 
                ID = '{zeout}' and  Phone_Number='{phone_no[1:]}';'''
        db = get_conn(config.master_db_cred)
        mycursor = db.cursor()
        mycursor.execute(q)
        db.commit()
        db.close()
        print("Fileds in master data table is updated- data2023")
        customResponse = [[date.strftime("%Y/%m/%d, %H:%M:%S"), 'DATA: '+  str(data_list), 'Status: Success']]
        res = {
                "Update" : "Success",
                "Request Value" : decoded_string,
                "Update Data" : data_list,
            }
        # GoogleSheetHandler(data = customResponse, sheet_name=config.SHEET_USER_DATA_FSR,spreadsheet_id=config.SAMPLE_SPREADSHEET_ID_FSP_2011).appendsheet_records()
        customResponse = tuple(customResponse[0])
        q = '''INSERT INTO `form_submission_response`
                (`post_date`,
                `response`,
                `status`)
                VALUES
                (%s,%s,%s);
            '''
        db = get_conn(config.db_cred)
        mycursor = db.cursor()
        mycursor.execute(q,customResponse)
        db.commit()
        db.close()
        
        return res
   
       
if __name__=='__main__':
    app.run(host='0.0.0.0',port=2011, debug=True)
    #app.run(ssl_context=('cert.pem','key.pem'))
    #http_server = WSGIServer(('212.227.238.32', 5000), app)
    #http_server.serve_forever()
