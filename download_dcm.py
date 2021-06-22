import configparser
import logging
import requests
import zipfile
import tempfile
import json

ini_config = configparser.ConfigParser()
ini_config.read('./config.ini')

exit_program_msg = '您输入编号有误，程序结束运行!'
base_url = 'http://192.168.1.212:81'

# 复制dcm文件
unzip_to_dir = ini_config['unzip']['unzip_to_dir']

log_level = logging.INFO
if 'debug' in ini_config['local']:
    if ini_config['local']['debug'] == 'True':
        print('开启调试模式')
        log_level = logging.DEBUG

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - Levelname: %(levelname)s Filename: %(filename)s '
                        'Line: [%(lineno)d] Thread: %(threadName)s MSG: \n'
                        '%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    # filename='run.txt'
)

def get_zip_file_data(url, headers={}):
    response = requests.get(url, headers=headers)
    return response.content

if __name__ == "__main__":
    logging.info('程序开始运行')
    logging.info(unzip_to_dir)

    print("按回车键确认")
    PatientID = input("请输入影像编号: ")

    try:
        if PatientID == 0 or not isinstance(int(PatientID), int):
            logging.error(exit_program_msg)
            exit()
    except Exception as e:
        logging.error(e)
        logging.error(exit_program_msg)
        exit()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic aG06Mjc1MTYxMjA='
    }
    data = {
        'Level': 'Study',
        'Expand': True,
        'Limit': 1,
        'Query': {
            'PatientID': PatientID
        }
    }

    response = requests.post(url=base_url + '/pacs/tools/find', headers=headers, data=json.dumps(data))
    res_data = response.json()
    if len(res_data) == 0:
        print('不存在数据，程序结束！')
        exit()

    ID = res_data[0]['ID']
    PatientMainDicomTags = res_data[0]['PatientMainDicomTags']
    print(ID)

    next_input = input('患者名称：{name} 请输入Y/y 回车后继续'.format(name=PatientMainDicomTags['PatientName'] ))
    if next_input != 'y':
        if next_input != 'Y':
            print('没有输入Y/y，程序结束')
            exit()

    # 开始下载dcm文件
    zip_data = get_zip_file_data(url=base_url + '/pacs/studies/{ID}/archive'.format(ID=ID), headers=headers)  # data为byte字节
 
    _tmp_file = tempfile.TemporaryFile()  # 创建临时文件
    print(_tmp_file)
 
    _tmp_file.write(zip_data)  # byte字节数据写入临时文件
    # _tmp_file.seek(0)
 
    zf = zipfile.ZipFile(_tmp_file, mode='r')
    for names in zf.namelist():
        f = zf.extract(names, unzip_to_dir)  # 解压到zip目录文件下
        print(f)

    zf.close()

