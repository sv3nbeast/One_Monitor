# -*- coding:utf-8 -*-
import re
import sys
import os
import time
import datetime

path="C:/Users/Administrator/Desktop/tools/OneForAll/oneforall"             #OneForAll绝对路径，需手动配置
old=path+"/域名监控/old_domain/"                                            #存放上次扫描结果的文件夹，需手动创建并填写此配置
new=path+"/域名监控/new_domain/"                                            #存放最新扫描结果的文件夹，需手动创建并填写此配置
update=path+"/域名监控/update/"                                             #存放新增域名结果的文件夹,需手动创建并填写此配置
old_import=path+"/域名监控/old_import/"                                     #存放目标域名数据库导出的上次结果,需手动创建并填写此配置

result_name=path+"/results/"                                              #存放oneforall结果的文件夹路径,默认配置即可


# print f_list

def result_txt(result_name):   #生成监控域名扫描结果的txt文件名字
    f_list = os.listdir(result_name)
    with open("result_name.txt","w") as r:
        for i in f_list:
            # os.path.splitext():分离文件名与扩展名
            if os.path.splitext(i)[1] == '.txt':
                r.write(i+"\n")
    return True

def update_domain():         #简化新旧扫描结果并进行对比，发现新增域名
    f=open('result_name.txt','r')
    lines=f.readlines()
    f.close()
    for line in lines:
        line1=line.strip('\n')
        target=line1[0:(line1.rfind('_', 1))]          #获得本次扫描目标域名
        table_name=target.replace('.',"_")+"_now"        #获得目标域名数据库存储表名
        
        print("[+] 开始导出<"+target+">数据库记录，用做后面的对比")
        print(os.system("python dbexport.py --table %s --format txt --dpath %s" %(table_name,old_import)))
        old_path=old+line1          #存放上次域名结果文件
        new_path=new+line1          #存放本次域名结果文件
        old_result_subdomain=old_import+table_name+"_subdomain.txt"    #存放域名扫描结果文件
        new_result_subdomain=result_name+line1
        
        now_time = datetime.datetime.now().strftime('%Y-%m-%d') #获得当前日期，为新增域名做准备
        update_subdomain=update+"update_"+now_time+"_"+line1   #为新增域名文件起个名字，防止重复


        f=open(old_result_subdomain, encoding="utf-8")
        f.close
        lines=f.read()
        pattern = re.compile(r'\|(http.*?://.*?)[ |]')
        result = pattern.findall(lines)

        print("[+] 获得<"+target+">上次扫描子域名结果中 ")
        with open(old_path,'w') as fopen:
            for subdomain_old in result:
                fopen.write(subdomain_old+"\n")

        print("[+] 开始扫描子域名,时间较长，请耐心等待...")
        os.system("python oneforall.py --target %s --format txt run" %target)
        #print("[+]当前监控域名:"+target+"[+]"+os.system("python oneforall.py --target %s --format txt run" %target))
        f=open(new_result_subdomain, encoding="utf-8")
        f.close
        lines=f.read()
        pattern = re.compile(r'\|(http.*?://.*?)[ |]')
        result = pattern.findall(lines)
        print("[+] 扫描完成，获得<"+target+">最新扫描子域名结果中 ")
        with open(new_path,'w') as fopen:
            for subdomain_new in result:
                fopen.write(subdomain_new+"\n")
                

        print("[*] 开始检测<"+target+">域名是否新增...")

        str1 = []
        file_1 = open(old_path,"r",encoding="utf-8")
        print("[+] 已打开old_domain存储的上次扫描结果："+line1+"文件，开始获取域名并存入数组old")
        for line in file_1.readlines():
            str1.append(line.replace("\n",""))

        str2 = []
        file_2 = open(new_path, "r", encoding="utf-8")
        print("[+] 已打开new_domain存储的本次扫描结果："+line1+"文件，开始获取域名并存入数组new")
        for line in file_2.readlines():
            str2.append(line.replace("\n", ""))


        str_dump = []
        print("[+] 正在对比数组获得新增域名中")
        for line in str2:
            if line not in str1:
                str_dump.append(line)    #将两个文件重复的内容取出来
        if len(str_dump) < 1:
            print("[+] 检测完成，不存在新增域名，请等待下一周期检测！")
        else:
            print("[+] 检测完成，存在新增域名:"+"\n")
            for str in str_dump:             #去重后的结果写入文件
                print(" "+str)
                with open(update_subdomain,"a+",encoding="utf-8") as f:
                    f.write(str + "\n")
            num=len(str_dump)

            number=num*900
            min=num*30
            print("\n"+"[+] "+"本次新增%s"%num +"个域名，将等待%s"%min+"分钟后执行下次任务")
            #time.sleep(number)
        
        




if __name__ == '__main__':
    result_txt(result_name)
    update_domain()