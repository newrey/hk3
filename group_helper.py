#-*- coding: UTF-8 -*- 
import pickle,os,time,shutil,csv

source = 'source.csv'
target = 'data.pkl'
data = dict()

if not os.path.exists(source):
    input("错误：source.csv文件不存在！请检查绑定数据文件路径和名称")
    os._exit()

if os.path.exists(target):
    if not os.path.isdir('backup'):
        os.mkdir('backup')
    back_up_data_file = 'backup/'+time.strftime('%Y%m%d%H%M%S')+'.pkl'
    print("\n#####################\n旧数据备份中... 路径："+ back_up_data_file+ "\n#####################\n" )
    shutil.copy(target, back_up_data_file)
    pkl_file = open(target, 'rb')
    data = dict(pickle.load(pkl_file))
    pkl_file.close()

pkl_file = open(target, 'wb')
successCount = 0
repeatCount = 0
csv_reader = csv.reader(open(source, encoding='utf-8'))
for row in csv_reader:
    rfidCode = row[0]
    oneCode = row[1]
    #print(row)
    if rfidCode in data:
        repeatCount = repeatCount+1
    else:
        data[rfidCode]=oneCode
        data[rfidCode]=oneCode
        successCount = successCount+1
pickle.dump(data, pkl_file)
pkl_file.close()
print("批量导入完成，成功"+ str(successCount) +"个，重复"+ str(repeatCount) +"个")
