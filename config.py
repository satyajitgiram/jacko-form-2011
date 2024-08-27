#2,4,8,10
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
print("Inside configuration file")
SERVICE_ACCOUNT_FILE = 'helpers/telebank-380408-d406ab167e88.json'
print(SERVICE_ACCOUNT_FILE)
SAMPLE_SPREADSHEET_ID = '1oBsnKLrl3beqcSS-v6dppGbLYtj2j8qrUfNoSwWsNsc'
SHEET_USER_DATA_GET = '2023'

# Id of spreadsheet 2011 
SAMPLE_SPREADSHEET_ID_FSP_2011 = '1Cs_re8c58ngSWmpIBMJ-M-gjWVVr_hHQIYfT-Y7EncQ'
BANK_ACCCOUNTS_SPREADSHEET_ID = '1xPngaoGriIY_fwlzTkaOl4I4bJGtgiJnEwEa4dWQXm4'

SHEET_USER_DATA_LOG = 'Logs'
# Form Submission Post
SHEET_USER_DATA_FSP = 'Form Submission Post'
SHEET_CODE_STORAGE = 'Code Storage'
SHEET_FORM_DATA_STORAGE = 'גיליון1'

BANK_ACCOUNT_SHEET = 'BANK AC'


# Form Sunmission Responses
SHEET_USER_DATA_FSR = 'Form Sunmission Responses'


CLIENT_CRED_FILE = 'helpers/client_secret_182314447059-s8vtpqqqeapc3hbic28l4hiar4njt5v3.apps.googleusercontent.com.json'
# REFRESH_TOKEN = "1//04H3x2SGpMzkeCgYIARAAGAQSNwF-L9IrsJ_Sdh-gcwHDxX9gd6LWnDJTDmFUmUAYQa-JBIT6IqC2G_j7XD0ERqZdmTyclzujn98"
REFRESH_TOKEN = "1//04m12PPq2mpeSCgYIARAAGAQSNwF-L9Ir4d2QTnf4HXbEHot313Yt9CcZLYkGUlJZRPsdfWr6yq_3GT1-w1_oXcCke5If_Zff3Fg"


MYFAX_EMAIL = "6708410@gmail.com"
MYFAX_PASSWORD = "TXkaTBk84hAt"

master_db_cred = {
    'user': 'mosdottora',
    'password': 'kq1vzqZf8HdEkH1xR1Kb',
    'host': 'form-1090.c7ksqaiy2mds.eu-north-1.rds.amazonaws.com',
    'database': 'form1090',
    'raise_on_warnings': True
}

db_cred = {
    'user': 'mosdottora',
    'password': 'kq1vzqZf8HdEkH1xR1Kb',
    'host': 'form-1090.c7ksqaiy2mds.eu-north-1.rds.amazonaws.com',
    'database': 'form2011',
    'raise_on_warnings': True
}

# master_db_cred = {
#     'user': 'root',
#     'password': '1234',
#     'host': 'localhost',
#     'database': 'practice',
#     'raise_on_warnings': True
# }

# db_cred = {
#     'user': 'root',
#     'password': '1234',
#     'host': 'localhost',
#     'database': 'form2011',
#     'raise_on_warnings': True
# }


