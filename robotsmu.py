import asyncio
import os
import discord
import random
import smtplib
import hashlib
import arrow
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def showtime():
    local = arrow.now()
    local.format('YYYY-MM-DD HH:mm:ss')
    return str(local.format('YYYY-MM-DD HH:mm:ss'))

    
#학번을 받아 암호화 후 반환
def encoding(studentID):
     salt = "This is salt of smu"
     saltedSID = salt+studentID
     encryptedStudentID = hashlib.sha256(saltedSID.encode())
     return str(encryptedStudentID.hexdigest())

def checkVerified(discordID):
    with open("data/discord.txt", 'r', encoding = 'UTF-8') as f:
        discordlist = f.readlines()
        for i in discordlist:
            if i == str(discordID)+"\n":
                print("["+showtime()+"]이미 인증된 사용자("+str(discordID)+")가 !인증을 입력했습니다.")
                return 1
        return 0

def discordtxt(discordID):
    with open("data/discord.txt", 'r', encoding = 'UTF-8') as f:
        discordlist = f.readlines()
        for i in discordlist:
            if i == str(discordID)+"\n":
                print("이미 연동된 디스코드 계정입니다.(1:1문의 필요) 에러코드:1000")
                return 0
    with open("data/discord.txt", 'a', encoding = 'UTF-8') as f:
        f.write(str(discordID)+"\n")
        print("디스코드 계정을 목록에 추가했습니다.")
        return 1
        
def studentIDtxt(encryptedStudentID):
    with open("data/studentID.txt", 'r', encoding = 'UTF-8') as f:
        studentIDlist = f.readlines()
        for i in studentIDlist:
            if i == str(encryptedStudentID)+"\n":
                print("입력하신 학번은 이미 연동되어 있습니다. 1인1계정이 원칙입니다.")
                return 0
    with open("data/studentID.txt", 'a', encoding = 'UTF-8') as f:
        f.write(str(encryptedStudentID)+"\n")
        print("암호화된 학번을 목록에 추가했습니다.")
        return 1

def usertxt(discordID,discordName,encryptedStudentID,authcode):
    try:
        f = open("data/user/"+str(discordID)+".txt", 'r')
    except:
        print(str(discordName)+".txt생성")                    #아이디.txt를 생성합니다.
        f = open("data/user/"+str(discordID)+".txt", 'w', encoding = 'UTF-8')
    else:
        print(str(discordName)+"("+str(discordID)+")님의 디스코드 아이디는 이미 인증 경력이 있습니다. 에러코드:1100")
        return 0
    f.write("discordID = "+str(discordID)+"\n")
    f.write("discordName = "+str(discordName)+"\n")
    f.write("encryptedStudentID = "+str(encryptedStudentID)+"\n")
    f.write("authcode = "+str(authcode)+"\n")
    f.close()
    return 1
            
                
    
client = discord.Client()
access_tocken = os.environ["BOT_TOCKEN"]
token = access_tocken

@client.event
async def on_ready():

    print("=========================")
    print("다음으로 로그인 합니다 : ")
    print(client.user.name)
    print(client.user.id)
    print("connection was successful")
    game = discord.Game("이메일 인증")
    print("=========================")
    await client.change_presence(status=discord.Status.online, activity=game)


@client.event
async def on_message(message):
    if message.author.bot:
        return None
    else:
        try:
            if 201400000<int(message.content)<202100000:
                with open("data/log.txt", 'a', encoding = 'UTF-8') as f:
                    f.write(str(message.author)+"||"+str(message.author.id)+"||["+showtime()+"*]:<보안을 위해 메세지 내용을 기록하지 않았습니다.>\n")
            else:
                with open("data/log.txt", 'a', encoding = 'UTF-8') as f:
                    f.write(str(message.author)+"||"+str(message.author.id)+"||["+showtime()+"]:"+str(message.content)+"\n")
        except:
            with open("data/log.txt", 'a', encoding = 'UTF-8') as f:
                f.write(str(message.author)+"||"+str(message.author.id)+"||["+showtime()+"]:"+str(message.content)+"\n")
    if message.content == "!인증안내":
        await message.channel.send("안녕하새오 로봇슴우애오!\학교 이메일 자동 인증이 필요하다면 저에게 DM(개인 메세지)으로```!인증```이라고 보내주새오\n 봇을 악용하면 로그를 바탕으로 책임을 물을 수 있습니다.")




    if message.content == "!인증":
        serverguild = client.get_guild(680434865715675200) #괄호 안에 서버 ID를 써주세요
        servermember = serverguild.get_member(message.author.id)
        vrole = discord.utils.get(serverguild.roles, name="Verified")
        if vrole in servermember.roles:
            await message.channel.send("당신은 이미 인증된 사용자입니다.")
            return 0
        
        if checkVerified(message.author.id) == 1:
            await message.channel.send("해당 디스코드 계정은  이미 인증 경력이 있습니다.(1:1문의 바람)")
            return 0

        num=1
        agree=1
        authcode=0
        ismailsent=1
        verified=1
        encryptedStuedntID = "abc"
        await message.channel.send("자신의 학번을 9자리 숫자 형태로 입력 해 주세요\n예시)```202012345```")
        
        def pred(m):
            return m.author == message.author and m.channel == message.channel
        try:

            msg1 = await client.wait_for('message', check=pred, timeout=60.0)
        except asyncio.TimeoutError:
            await message.channel.send('입력 시간이 만료되어 인증 과정이 종료되었습니다.\n처음부터 다시 시도해 주세요.')
            return 0
        else:
            try:
                if 201400000<int(msg1.content)<202100000:
                    await message.channel.send('{0.content}@sangmyung.kr로 메일을 보내고,\n서버 보안을 위해 학번과 디스코드 닉네임을 수집합니다.\n학번은 SHA256으로 암호화되어 서버에 저장됩니다.\n(단, gmail에는 학번이 평문으로 저장되어 서버 공격 발생시 관리자가 열람할 수 있습니다.")\n동의하시겠습니까?\n동의하면 ```동의``` 를 입력해주세요.'.format(msg1))
                    #num=1
                else:
                    await message.channel.send('잘못된 학번이거나 14학번 이전 학번입니다.\n보안 문제로 인해 14학번부터 자동 인증이 가능합니다(1:1 문의 필요)\n단순히 잘못 입력한 것이라면 처음부터 다시 시도해주세요')
                    return 0
            except:
                if msg1.content != "!인증":
                    await message.channel.send("숫자가 아닌 문자를 입력하셨습니다!\n처음부터 다시 시도해주세요!")
                return 0
        if num == 1:
            try:
                msg2 = await client.wait_for('message', check=pred, timeout=60.0)
            except asyncio.TimeoutError:
                await message.channel.send('입력 시간이 만료되어 자동으로 거부되었습니다.\n메일 인증을 받으려면 처음부터 다시 시도해주세요.')
                return 0
            else:
                if msg2.content=='동의':
                    #agree=1
                    await message.channel.send('메일 보내기 시도중...')
                else:
                    if msg2.content != "!인증":
                        await message.channel.send('잘못된 입력으로 인해 거부되었습니다. 동의 라고 정확히 입력해주세요. 처음부터 다시 시도해주세요.')
                    return 0
        if agree == 1:
            # 지메일 아이디,비번 입력하기
            email_user = 'mcsmu20@gmail.com'      #<ID> 본인 계정 아이디 입력
            email_password = str(os.environ.get("MAIL_PW"))      #<PASSWORD> 본인 계정 암호 입력
            email_send =str(msg1.content)+'@sangmyung.kr'         # <받는곳주소> 수신자 이메일 abc@abc.com 형태로 입력
        
            # 제목 입력
            subject = '상명대 마크 서버 디스코드 인증 메일입니다.'

            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = email_send
            msg['Subject'] = subject

            authcode = random.randint(100000,999999)
            #print(authcode) 인증코드 출력

            # 본문 내용 입력
            body = str(msg2.author)+"("+str(msg2.author.id)+")님이 요청하신 인증번호는 아래와 같습니다.\n인증번호 6자리를 로봇슴우에게 보내주세요!"+"\n\n인증번호:"+str(authcode)
            msg.attach(MIMEText(body,'plain'))

            text = msg.as_string()
            server = smtplib.SMTP('smtp.gmail.com',587)
            server.starttls()
            server.login(email_user,email_password)

            try:
                server.sendmail(email_user,email_send,text)
            except:
                print("오류:메일을 전송하지 못했습니다.")
                await message.channel.send("오류:메일을 전송하지 못했습니다.")
                return 0
            finally:
                ismailsent=1
                print(str(msg2.author)+"("+str(msg2.author.id)+")"+"에게 메일 보내기 성공")
                await message.channel.send("메일로 인증번호를 보냈습니다.\n인증번호 6자리를 5분 안에 입력해주세요.")
                
        if ismailsent == 1:
            try:
                msg3 = await client.wait_for('message', check=pred, timeout=300.0)
            except:
                ("5분이 지나 만료되었습니다. 다시 인증을 요청해주세요.")
                return 0
            else:
                if msg3.content == str(authcode):
                    encryptedStudentID = encoding(str(msg1.content))
                    
                    if studentIDtxt(encryptedStudentID) == 1:
                        
                        if discordtxt(str(msg1.author.id)) == 0:
                            await message.channel.send("무슨 짓을 하셨길래 이런 메세지가 뜬거죠?\n당신의 디스코드계정은 이미 인증 경력이 있는 것 같습니다. 에러코드:1000")
                            return 0
                        if usertxt(str(msg1.author.id),str(msg1.author),str(encryptedStudentID),str(authcode)) == 0:
                            await message.channel.send("무슨 짓을 하셨길래 이 메세지가 뜬거죠?\n당신의 디스코드 아이디는 이미 인증되어 있습니다.(1:1문의 필요) 에러코드:1100")
                            return 0   
                        await message.channel.send("인증 성공! 이제 디스코드 채널을 사용하실 수 있습니다.\n오픈채팅방에 들어와주세요!\nhttps://open.kakao.com/o/gnFN8u6b?t=2230155194909093888\n```참여코드:상명대생은 다 아는 그 버스 번호는?(4자리 숫자로 입력)```")
                        print("******************************")
                        print("디스코드닉네임:"+str(msg1.author)+"\n디스코드ID:"+str(msg1.author.id)+"\n인증번호:"+str(authcode))
                        print("******************************")
                        verified=1                        
                    else:
                        await message.channel.send("입력하신 학번은 이미 인증 이력이 있습니다. 1인1계정이 원칙입니다.")
                        return 0
                else:
                    if msg3.content != "!인증":
                        await message.channel.send("잘못 입력하셨습니다. 처음부터 다시 시도해 주세요.")
                    return 0
        if verified==1:
            role=discord.utils.get(client.get_guild(680434865715675200).roles, name="Verified")     #괄호 안에 서버 아이디를 써주세요
            servermember = serverguild.get_member(msg1.author.id)
            await servermember.add_roles(role)
                    
                    
                
            server.quit()
        #print(msg1.author)
        #print(msg1.author.id)
                
client.run(token)
