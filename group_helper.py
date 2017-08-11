#-*- coding: UTF-8 -*- 
import pickle,os,time,shutil

source = 'source.csv'
target = 'data.pkl'
data = dict()

if not os.path.exists(target):
    raw_input("source.csv文件不存在！")
    return

if os.path.exists(target):
    back_up_data_file = 'back_data_'+time.strftime('%Y%m%d%H%M%S')+'.pkl'
    print("备份现有数据到"+back_up_data_file)
    shutil.copy('data.pkl', back_up_data_file)
    pkl_file = open(target, 'wb+')
    data = dict(pickle.load(pkl_file))
    successCount = 0
    repeatCount = 0
    csv_reader = csv.reader(open(source, encoding='utf-8'))
        for row in csv_reader:
            rfidCode = row[0]
            oneCode = row[1]
            if rfidCode in data:
                repeatCount = repeatCount+1
            else:
                data[rfidCode]=oneCode
                data[rfidCode]=oneCode
                successCount = successCount+1
    pickle.dump(data, pkl_file)
    pkl_file.close()
    print("批量导入完成，成功"+ successCount +"个，重复"+ repeatCount +"个")