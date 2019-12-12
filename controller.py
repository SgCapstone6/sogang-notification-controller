import json
import pymysql
import traceback
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.models import QuickReply
from linebot.models import QuickReplyButton
from linebot.models import MessageAction
from linebot.exceptions import LineBotApiError

line_bot_api = LineBotApi()
admin_id =  ""
tags = set(['을','를','이','가', '이가','는','은', '께서','에서', '에게','에','이다','에게서','로','으로','한테','와','과'])
personal_data=
        [
        ]
def lambda_handler(event, context):
    # TODO implement
    msg = ''
    try:
        db = pymysql.connect(host = personal_data[0], port =3306,
                user = personal_data[1],
                passwd = personal_data[2],
                db = personal_data[3],
                charset = 'utf8')
    except Exception as e:
        print("db open error!")
        print(e)

    try:
        for e in event["events"]:
            if (e["source"]["type"] != "user"):
                return # User가 아닌 방 같은 경우 처리
        type_msg = e['type']

        if (type_msg != "message"):
            return # 메세지가 아닌 팔로우/언팔로우 처리
        user_id = e['source']['userId']
        msg = e['message']['text']
        rpl_tok = e['replyToken']


        mSplit = msg.split(' ');
        if len(mSplit) < 1:
            reply(rpl_tok,"잘못된 명령어 입니다.")

        if mSplit[0] == "도움말":
            reply(rpl_tok,"####도움말####\n"+\
                    "가능한 명령어 목록입니다.\n"+\
                    "1. 부처 검색\n"+\
                    "2. 부서 검색[부처 명]\n"+\
                    "3. 게시판 검색[부서명]\n"+\
                    "4. 게시판 구독 [부처], [부서], [게시판]\n"+\
                    "5. 게시판 구독 취소[부처], [부서], [게시판]\n"+\
                    "6. 키워드 구독 [키워드]\n"+\
                    "7. 키워드 구독 취소[키워드]\n"+\
                    "8. 고급구독 [키워드] [부처], [부서], [게시판]\n"+\
                    "9. 고급구독 취소 [키워드] [부처], [부서], [게시판]\n"+\
                    "10. 구독 조회\n"+\
                    "\n*모든 명령어는 예시처럼 공백이나 쉼표(,) 로 구분되어야 합니다*")

        elif mSplit[0] == "문의": # 문의 사항 전송 
            if len(mSplit) >1:
                send(admin_id,user_id + " : "+ " ".join(mSplit[1:]));
                reply(rpl_tok,"문의 사항을 전송했습니다.");
            else:
                reply(rpl_tok,"[문의 (문의사항 내용)]의 형식으로 보내야 합니다. ");

        elif len(mSplit) > 1 and mSplit[0] == "부처" and mSplit[1] == "검색" : #명령어 : 부처 검색
            with db.cursor() as cursor:
                sql = "select site_layer_1 from site_info group by site_layer_1"
                cursor.execute(sql)
                result = cursor.fetchall()
                name_list = []
                for temp in result:
                    name_list.append(temp[0])
                reply(rpl_tok,'\n'.join(name_list));

        elif len(mSplit) > 1 and mSplit[0] == "부서" and mSplit[1] == "검색": # 명령어 : 부서 검색 [부처명]
            if len(mSplit) < 3:
                try:
                    line_bot_api.reply_message(rpl_tok, TextSendMessage(text="부서 검색 [부처명] 을 입력하여야 합니다.",
                        quick_reply = QuickReply(items=[
                            QuickReplyButton(action = MessageAction(label="도움말",text="도움말")),
                            QuickReplyButton(action = MessageAction(label="부처 목록",text="부처 검색"))
                            ])))
                except LineBotApiError as e:
                    print(msg) #Exception Handling(Line Bot Error)
                    print("error: in 부서 검색")
                    print(e)
            else:
                with db.cursor() as cursor:
                    sql = "".join(["select site_layer_2 from site_info where site_layer_1 ='", " ".join(mSplit[2:]) ,"' group by site_layer_2;"]);
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    result_list = []
                    for temp in result:
                        result_list.append(temp[0])
                    if len(result_list) == 0:
                        line_bot_api.reply_message(rpl_tok,TextSendMessage(text="지원하지 않거나 잘못 입력된 부서명 입니다.",
                            quick_reply = QuickReply(items=[
                                QuickReplyButton(action = MessageAction(label="도움말",text="도움말")),
                                QuickReplyButton(action = MessageAction(label="부처 목록",text="부처 검색"))
                                ])))
                    else:
                        item_list = []
                        """
                        for result in result_list:
                            item_list.append(QuickReplyButton(action = MessageAction(label = result,text=result)))
                        line_bot_api.reply_message(rpl_tok,TextSendMessage(text=".",quick_reply = QuickReply(items= item_list)))
                        """
                        reply(rpl_tok,'\n'.join(result_list))


        elif len(mSplit) > 1 and mSplit[0] == "게시판" and mSplit[1] == "검색": # 명령어 : 게시판 검색 [부서명]
            if len(mSplit) < 3:
                try:
                    line_bot_api.reply_message(rpl_tok, TextSendMessage(text="게시판 검색 [부서명] 을 입력하여야 합니다.\n 부서 목록은 [부서 검색 [부처명]] 명령어를 입력해주세요.",
                        quick_reply = QuickReply(items=[
                            QuickReplyButton(action = MessageAction(label="도움말",text="도움말")),
                            QuickReplyButton(action = MessageAction(label="부처 목록",text="부처 검색"))
                            ])))
                except LineBotApiError as e:
                    print(msg) #Exception Handling(Line Bot Error)
                    print("error: in 게시판 검색")
                    print(e)
            else:
                with db.cursor() as cursor:
                    sql = "".join(["select site_layer_3, site_url from site_info where site_layer_2 ='" ," ".join(mSplit[2:]) , "';"])
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    result_list = []
                    url_list = []
                    for temp in result:
                        result_list.append(temp[0])
                        url_list.append(temp[1])
                    if len(result_list) == 0:
                        line_bot_api.reply_message(rpl_tok,TextSendMessage(text="지원하지않거나 잘못 입력된 부서명 입니다.\n",
                            quick_reply = QuickReply(items=[
                                QuickReplyButton(action = MessageAction(label="도움말",text="도움말"))
                                ])))
                    else:
                        url_list = list(map("({0})".format,url_list))
                        with_url = list(zip(result_list, url_list))
                        with_url = list(map("".join,with_url))
                        reply(rpl_tok,'\n'.join(with_url) );


        elif len(mSplit) > 1 and mSplit[0] == "키워드" and mSplit[1] == "구독":
            if len(mSplit) < 3:
                reply(rpl_tok,"키워드 구독 [키워드] or [취소 키워드] 를 입력하여야 합니다.");
            else:
                if mSplit[2] == "취소": #키워드 구독 취소 키워드
                    if len(mSplit) <4:
                        reply(rpl_tok,"키워드 구독 취소 [키워드] 를 입력하여야 합니다.");
                    else:
                        word = mSplit[3]
                        with db.cursor() as cursor:
                            sql = 'delete from word_subscribe where word = %s and user_id = %s'
                            cursor.execute(sql,(word,user_id))
                            db.commit()
                            reply(rpl_tok," ".join(["키워드",mSplit[3],"구독 취소 완료되었습니다."]))

                else:                   #키워드 구독 키워드
                    word = mSplit[2]
                    if len(word) < 2 or set(mSplit[2:]).issubset(tags):
                        reply(rpl_tok,"키워드가 너무 짧거나, 불량합니다")
                    else:
                        with db.cursor() as cursor:
                            sql = 'insert into word_subscribe value(%s,%s,%s)'
                            cursor.execute(sql,(word,user_id,0))
                            db.commit()
                            reply(rpl_tok," ".join(["키워드",mSplit[2],"구독 완료되었습니다."]))

        elif len(mSplit) > 1 and mSplit[0] == "게시판" and mSplit[1] == "구독":
            if len(mSplit) < 3:
                reply(rpl_tok,"게시판 구독 (취소) [부처], [부서], [게시판] 을 입력하여야 합니다.");
            else:
                if mSplit[2] == "취소": #게시판 구독 취소 부처, 부서, 게시판
                    if len(mSplit) <4:
                        reply(rpl_tok,"게시판 구독 취소 [부처], [부서], [게시판] 을 입력하여야 합니다.");
                    else:
                        coord = " ".join(mSplit[3:])
                        site = coord.split(',')
                        site = list(map(str.strip,site))
                        if len(site) < 3:
                            reply(rpl_tok,"게시판 구독 취소 [부처], [부서], [게시판] 을 입력하여야 합니다.");
                        else:
                            with db.cursor() as cursor:
                                sql = "".join(["select site_id from site_info where site_layer_1 = '",site[0], " ' and site_layer_2 = '" ,site[1], "'and site_layer_3 = '", site[2],"'" ])
                                cursor.execute(sql)
                                row = cursor.fetchall()
                                site_id = row[0][0]
                                sql = 'delete from site_subscribe where user_id = %s and site_id = %s'
                                cursor.execute(sql,(user_id,site_id))
                                db.commit()
                                reply(rpl_tok," ".join(["게시판",site[1],site[2],"구독 취소 완료되었습니다."]))

                else:               #게시판 구독 부처, 부서, 게시판
                    if len(mSplit) < 3 :
                        reply(rpl_tok,"게시판 구독 [부처], [부서], [게시판] 을 입력하여야 합니다.");
                    else:
                        coord = " ".join(mSplit[2:])
                        site = coord.split(',')
                        site = list(map(str.strip,site))
                        if len(site) < 3:
                            reply(rpl_tok,"게시판 구독 [부처], [부서], [게시판] 을 입력하여야 합니다.");
                        else:
                            with db.cursor() as cursor:
                                sql = "".join(["select site_id from site_info where site_layer_1 = '"+site[0]+"' and site_layer_2 = '"+site[1]+"' and site_layer_3 = '"+site[2]+"'" ]) 
                                cursor.execute(sql)
                                row = cursor.fetchall()
                                site_id=row[0][0]
                                sql = 'insert into site_subscribe Value(%s,%s)'
                                cursor.execute(sql,(site_id,user_id))
                                db.commit()
                                reply(rpl_tok," ".join(["게시판",site[1],site[2],"구독 완료되었습니다."]))



        elif len(mSplit) > 1 and mSplit[0] == "구독" and mSplit[1] == "조회":
            with db.cursor() as cursor:
                sql = 'select word,site_id from word_subscribe where user_id = %s'
                cursor.execute(sql,user_id)
                rows = cursor.fetchall()
                temp = "구독 키워드:\n"
                for row in rows:
                    if row[1] != 0:
                        sql= 'select site_layer_1,site_layer_2,site_layer_3 from site_info where site_id = %s'
                        cursor.execute(sql,row[1])
                        site_infos = cursor.fetchall()
                        temp += row[0] + '-' + site_infos[0][0] +' '+ site_infos[0][1] +' '+ site_infos[0][2] + '\n'
                    else:
                        temp +=row[0]+'\n'
                send(user_id,temp)

                sql= 'select sl.site_layer_1,sl.site_layer_2,sl.site_layer_3 from site_info as sl, site_subscribe as ss where ss.user_id = %s and ss.site_id = sl.site_id'
                cursor.execute(sql,user_id)
                rows = cursor.fetchall()

                temp = "구독 게시판:\n"
                for row in rows:
                    temp +=row[0] +' ' +row[1]+' '+row[2] +'\n'
                send(user_id,temp);
       
        elif len(mSplit) > 1 and mSplit[0] == "구독" and mSplit[1] == "최신글":
            #SQL
            #result_list = [ [제목,URL] , [제목,URL] ,.... ] 형태
            reply(rpl_tok,"현재 구독사항 최신 글은 다음과 같습니다")
            for result in result_list:
                reply(rpl_tok, result[0] + "\n" +result[1]);
      
                
        elif mSplit[0] == "고급구독":
            if len(mSplit) > 1 and mSplit[1] == "취소":
                if len(mSplit)<4 :
                    #메세지
                    try:
                        line_bot_api.reply_message(rpl_tok, TextSendMessage(text="고급구독 취소 [키워드] [부처, 부서, 게시판] 을 입력하여야 합니다.\n 부처 목록은 [부처 검색] 명령어를 입력해주세요.",
                            quick_reply = QuickReply(items=[
                                  QuickReplyButton(action = MessageAction(label="도움말",text="도움말")),
                                  QuickReplyButton(action = MessageAction(label="부처목록",text="부처 검색"))
                                  ])))
                    except LineBotApiError as e:
                        print('msg')
                        print('error in 고급 구독 취소 실패 사이트 없음') #Exception Handling(Line Bot Error)
                        print(e)
                else:#고급구독 취소
                    word = mSplit[2]
                    coord = "".join(mSplit[3:])
                    site = coord.split(",")
                    site = list(map(str.strip,site))
                    if len(site) < 3:
                        try:
                            line_bot_api.reply_message(rpl_tok, TextSendMessage(text="고급구독 취소 [키워드] [부처,부서,게시판] 을 입력하여야 합니다.\n 부처 목록은 [부처 검색] 명령어를 입력해주세요.",
                                    quick_reply = QuickReply(items=[
                                        QuickReplyButton(action = MessageAction(label="도움말",text="도움말")),
                                        QuickReplyButton(action = MessageAction(label="부처목록",text="부처 검색"))
                                        ])))
                        except LineBotApiError as e:
                            print('msg')
                            print('error in 고급 구독 취소 사이트 실패') #Exception Handling(Line Bot Error)
                            print(e)
                    else:
                        with db.cursor() as cursor:
                            sql = "".join(["select site_id from site_info where site_layer_1 = '",site[0], " ' and site_layer_2 = '" ,site[1], "'and site_layer_3 = '", site[2],"'" ])
                            cursor.execute(sql)
                            row = cursor.fetchall()
                            site_id = row[0][0]
                            sql = 'delete from word_subscribe where user_id = %s and site_id = %s and word = %s'
                            cursor.execute(sql,(user_id,site_id,word))
                            db.commit()
                            reply(rpl_tok," ".join(["게시판",site[1],site[2],"키워드",word,"구독 취소 완료되었습니다."]))

            else: #명령어: 고급구독 (키워드) (부처,부서,게시판)
                if len(mSplit) < 3:
                  #메세지
                    try:
                        line_bot_api.reply_message(rpl_tok, TextSendMessage(text="고급구독 [키워드] [부처,부서,게시판] 을 입력하여야 합니다.\n 부처 목록은 [부처 검색] 명령어를 입력해주세요.",
                            quick_reply = QuickReply(items=[
                                QuickReplyButton(action = MessageAction(label="도움말",text="도움말")),
                                QuickReplyButton(action = MessageAction(label="부처목록",text="부처 검색"))
                                ])))
                    except LineBotApiError as e:
                        print('msg')
                        print('error in 고급 구독실패') #Exception Handling(Line Bot Error)
                        print(e)
                else:
                    word = mSplit[1]
                    coord = "".join(mSplit[2:])
                    site = coord.split(",")
                    site = list(map(str.strip,site))
                    if len(site) < 3:
                        try:
                            line_bot_api.reply_message(rpl_tok, TextSendMessage(text="고급구독 취소 [키워드] [부처,부서,게시판] 을 입력하여야 합니다.\n 부처 목록은 [부처 검색] 명령어를 입력해주세요.",
                                    quick_reply = QuickReply(items=[
                                        QuickReplyButton(action = MessageAction(label="도움말",text="도움말")),
                                        QuickReplyButton(action = MessageAction(label="부처목록",text="부처 검색"))
                                        ])))
                        except LineBotApiError as e:
                            print('msg')
                            print('error in 고급 구독정상 상황') #Exception Handling(Line Bot Error)
                            print(e)
                    else:
                          #pass #SQL 여기(고급구독 등록)
                        with db.cursor() as cursor:
                            sql = "".join(["select site_id from site_info where site_layer_1 = '",site[0], " ' and site_layer_2 = '" ,site[1], "'and site_layer_3 = '", site[2],"'" ])
                            cursor.execute(sql)
                            row = cursor.fetchall()
                            site_id = row[0][0]
                            sql = 'insert into word_subscribe Value(%s,%s,%s)'
                            cursor.execute(sql,(word,user_id,site_id))
                            db.commit()
                            reply(rpl_tok," ".join(["게시판",site[1],site[2],"키워드",word,"구독 완료되었습니다."]))
        else:
            reply(rpl_tok,"잘못된 명령어 입니다.")
            #site = [0] [1] [2] 순으로 부처 부서 게시판
            #word에 키워드
            #예외처리하기
    except Exception as e:
        print("MSG:"+msg)
        print(traceback.format_exc())
    finally:
        db.close()
    #   tmp_tag = set(msg.split(' '))
    #   if tmp_tag.issubset(tags) :
    #   pass
          #error_handler(Keyword Error)


    #    reply(rpl_tok,msg)
    #    send(user_id,msg)

    return {
            'statusCode': 200,
            'body': json.dumps(event),
            }

def send (uId, string): #send string to uId
    try:
        line_bot_api.push_message(uId, TextSendMessage(string))
    except LineBotApiError as e:
      print("send error"); #Exception Handling(Line Bot Error)

def reply(tok, string): #send reply to token
    try:
        line_bot_api.reply_message(tok, TextSendMessage(string))
    except LineBotApiError as e:
        print('reply error') #Exception Handling(Line Bot Error)
        print(e)
