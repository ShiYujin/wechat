# TODO:
# 2, 解决图片保存的问题
# 3，新建文件夹，图片、文件定期更新存储路径
# 4，生成聊天记录统计信息
# 5，导出所有联系人、群聊信息
# 6，

# coding:utf-8
import itchat
from itchat.content import *
import time
import re
import os
import io
import sys

import chardet

from db import *

log_filename = "./data/log.log"
log_file = None;
stdout_backup = sys.stdout
export_root = "./data/file/"
# face_bug=None  #针对表情包的内容

def printto(filename):
    global log_file;
    if(log_file != None):
        log_file.close();
    if(filename == None):
        sys.stdout = stdout_backup;
    else:
        log_file = open(filename, "w", encoding='utf-8')
        sys.stdout = log_file

def log(str):
    global log_filename;
    log_file = open(log_filename, "a", encoding='utf-8')
    print(str, file = log_file);
    log_file.close();

def export2db(msg):
    db_insert(msg);
    db.commit();

def querydb(id):
    print("Recall query: " + id)
    data = select_id(id);
    # print(data)
    return data;

# @itchat.msg_register([SYSTEM], isFriendChat=True, isGroupChat=True, isMpChat=True)
# def receive_other_msg(msg):
#     log(msg);
#     msg_time_rec = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())   #接受消息的时间
#     msg_share_url = "";
#     export2db({\
#         "msg_id": msg['MsgId'],\
#         "msg_from": msg['FromUserName'], "msg_to": msg['ToUserName'],\
#         "msg_time": msg['CreateTime'], "msg_time_rec": msg_time_rec,\
#         "msg_type": msg['Type'],\
#         "msg": msg['Text'], \
#         "url": msg_share_url\
#         });

@itchat.msg_register([TEXT, PICTURE, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO, FRIENDS, NOTE], \
    isFriendChat=True)
def receive_friend_msg(msg):
    receive_msg(msg, "friendchat");

@itchat.msg_register([TEXT, PICTURE, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO, FRIENDS, NOTE], \
    isGroupChat=True)
def receive_group_msg(msg):
    receive_msg(msg, "grouphat");

@itchat.msg_register([TEXT, PICTURE, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO, FRIENDS, NOTE], \
    isMpChat=True)
def receive_mp_msg(msg):
    receive_msg(msg, "mpchat");

def receive_msg(msg, source):
    msg_time_rec = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())   #接受消息的时间
    msg_from = msg['FromUserName'];
    msg_to = msg['ToUserName'];
    if(source == "friendchat"):
        from_info = itchat.search_friends(userName=msg['FromUserName']);
        if(from_info):
            if(from_info['RemarkName']):
                msg_from = from_info['RemarkName']   #在好友列表中查询发送信息的好友昵称
                msg_from += "(" + from_info['NickName'] + ")"
            else:
                msg_from = from_info['NickName']
        to_info = itchat.search_friends(userName=msg['ToUserName']);
        if(to_info):
            if(to_info['RemarkName']):
                msg_to = to_info['RemarkName']   #在好友列表中查询发送信息的好友昵称
                msg_to += "(" + to_info['NickName'] + ")"
            else:
                msg_to = to_info['NickName']

    elif(source == "grouphat"): # group chat
        from_info = itchat.search_friends(userName=msg['FromUserName']);
        if(from_info):
            if(from_info['RemarkName']):
                msg_from = from_info['RemarkName']   #在好友列表中查询发送信息的好友昵称
                msg_from += "(" + from_info['NickName'] + ")"
        else:
            msg_from = msg['ActualNickName'];
        group_info = itchat.search_chatrooms(userName = msg['FromUserName'])
        if(group_info):
            msg_to = 'GroupChat:' + group_info['NickName']
        else:
            msg_to = 'GroupChat:' + msg['FromUserName'];
    else:
        mp_info = itchat.search_mps(userName = msg['FromUserName'])
        if(mp_info):
            msg_from = "MpChat:" + mp_info['NickName'];
        else:
            msg_from = "MpChat:" + msg['FromUserName'];
        msg_to = msg_from;
    # print(msg_from);
    # print(msg_to);
    msg_time = msg['CreateTime']    #信息发送的时间
    msg_id = msg['MsgId']    #每条信息的id
    msg_content = ""      #储存信息的内容
    msg_share_url = ""    #储存分享的链接，比如分享的文章和音乐
#    log(msg_time_rec +'\n  --From ' + msg_from + ' to ' + msg_to + '\n  --Type ' + msg['Type']);
    log(msg);
    #如果发送的消息是文本
    if msg['Type'] == 'Text' or msg['Type'] == 'Friends':
        msg_content = msg['Text']
    #如果发送的消息是附件、视频、图片、语音
    elif msg['Type'] == "Attachment" or msg['Type'] == "Video" \
            or msg['Type'] == 'Picture' \
            or msg['Type'] == 'Recording':
        # print(msg_content)
        msg_content = msg['FileName']    #内容就是他们的文件名
        msg['Text'](export_root + str(msg_content))    #下载文件
    #如果消息是推荐的名片
    elif msg['Type'] == 'Card':
        #print(msg['RecommendInfo'])
        msg_content = msg['RecommendInfo']['NickName'] + '\'s card, \n'    #内容就是推荐人的昵称和性别
        if msg['RecommendInfo']['Sex'] == 1:
            msg_content += 'Sex: Male, \n'
        elif msg['RecommendInfo']['Sex'] == 2:
            msg_content += 'Sex: Female, \n'
        else:
            msg_content += 'Sex: Unknown, \n'
        msg_content += 'Alias: '+ msg['RecommendInfo']['Alias'] + ', \n'
        msg_content += 'QQNum: '+ str(msg['RecommendInfo']['QQNum']) + ', \n'
        msg_content += 'VerifyFlag: '+ str(msg['RecommendInfo']['VerifyFlag']) + ', \n'
        msg_content += 'Scene: '+ str(msg['RecommendInfo']['Scene']) + ', \n'
        msg_content += 'Province: '+ msg['RecommendInfo']['Province'] + ', \n'
        msg_content += 'City: '+ msg['RecommendInfo']['City'] + ', \n'
        msg_content += 'Signature: '+ msg['RecommendInfo']['Signature'] + ', \n'
        msg_content += 'AttrStatus: '+ str(msg['RecommendInfo']['AttrStatus']) + ', \n'
        msg_content += 'Ticket: '+ msg['RecommendInfo']['Ticket'] + ', \n'
        msg_content += 'OpCode: '+ str(msg['RecommendInfo']['OpCode']) + ', \n'
        msg_content += 'Content: '+ msg['RecommendInfo']['Content'];
        # print(msg_content)
    #如果消息为分享的位置信息
    elif msg['Type'] == 'Map':
        x, y, location = re.search(
            "<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1, 2, 3)
        # print(x)
        # print(y)
        # print(location)
        msg_content = msg['Text'] + '\n'
        msg_content += "latitude: " + x.__str__() + ",\nlongitude: " + y.__str__() + ',\n'
        msg_content += location;
    #如果消息为分享的音乐或者文章，详细的内容为文章的标题或者是分享的名字
    elif msg['Type'] == 'Sharing':
        msg_content = msg['Text']
        msg_share_url = msg['Url']
        # print(msg_share_url)
    elif msg['Type'] == 'Note':
        msg_content = msg['Text'];
        save_recall(msg);

    export2db({\
        "msg_id": msg_id,\
        "msg_from": msg_from, "msg_to": msg_to, \
        "msg_time": msg_time, "msg_time_rec": msg_time_rec,\
        "msg_type": msg["Type"],\
        "msg": msg_content, "url": msg_share_url\
        });
    # itchat.send_msg("test...", toUserName='filehelper')

##这个是用于监听是否有消息撤回
# @itchat.msg_register(NOTE, isFriendChat=True, isGroupChat=True, isMpChat=True)
def save_recall(msg):
    # itchat.send_msg("recall...", toUserName='filehelper')
    #这里如果这里的msg['Content']中包含消息撤回和id，就执行下面的语句
    if '撤回了一条消息' in msg['Content'] or 'recalled a message' in msg['Content']:
        old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)   #在返回的content查找撤回的消息的id
        old_msg = querydb(str(old_msg_id));
        # old_msg = msg_information.get(old_msg_id)    #得到消息
        log('Recalled message detected...\n  --From ' + old_msg.msg_from + '\n  --To' + old_msg.msg_to)
        if len(old_msg_id)<11:  #如果发送的是表情包
            itchat.send_file(old_msg.msg,toUserName='filehelper')
        else:  #发送撤回的提示给文件助手
            msg_body = "Warning:" + "\n" \
                       + old_msg.msg_time_rec + "\n" \
                       + old_msg.msg_from + " (to " + old_msg.msg_to + ") has recalled a " \
                       + old_msg.msg_type + " message" + "\n" \
                       + r"" + old_msg.msg
                       # + "Here is it ⇣" + "\n" \
            #如果是分享的文件被撤回了，那么就将分享的url加在msg_body中发送给文件助手
            if old_msg.msg_type == "Sharing":
                msg_body += "\nlink➣ \n" + old_msg.url

            # 将撤回消息发送到文件助手
            itchat.send_msg(msg_body, toUserName='filehelper')
            # 有文件的话也要将文件发送回去
            if old_msg.msg_type == "Picture" \
                    or old_msg.msg_type == "Recording" \
                    or old_msg.msg_type == "Video" \
                    or old_msg.msg_type == "Attachment":
                file = '@fil@%s' % (export_root + old_msg.msg)
                itchat.send(msg=file, toUserName='filehelper')


# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
# print('\U0001f426');
# enableCmdQR means show QRcode in cmd; otherwise QRcode will be showed in picture editor;
itchat.auto_login(hotReload=True, enableCmdQR=True)

# printto(log_filename);
init_db();

# debug mode
# itchat.run(debug=True)
itchat.run();
