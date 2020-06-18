from tkinter import *
from tkinter import ttk
import folium
import webbrowser

from http.client import HTTPSConnection
from http.server import BaseHTTPRequestHandler, HTTPServer
from operator import itemgetter

import http.client
import telepot
import copy
import requests
import smtplib

class MainGUI:

    global fileName, conn, client_id, searchYearCd, siDo, guGun, pageNo, numOfRows, server, DataList, \
        sortData_Num, sortData, DataList_sortData, Data_to_tkinter, chatId, chatBot, \
        graph_title, GraphCanvas, graph_bar, graph_label1, graph_label2, \
        map_conn, map_client_id, map_server, MapDataList

    fileName = "D:\3학년\스크립트\텀프로젝트\중간\교통사고_TkInter/교통사고정보.txt"

    ##################      교통사고 데이터 받아오는 정보        ###################################################
    conn = None
    client_id = "t5oMrbXTtq4jIGLnhsqeY3dgl6ZE7OJvp7W6VWLABuIThDD%2BTxc88xEit9tU0gS%2BtDWK9x%2BPzMk7tpwq1zwoYw%3D%3D"

    searchYearCd = ""
    siDo = ""
    guGun = ""
    pageNo = "1"
    numOfRows = "1143"  # 한 페이지에 몇개의 정보를 받아올지. -> 전국 전체 시군구 전부 출력하는 숫자.
    # OpenAPI 접속 정보 information
    server = "apis.data.go.kr"
    ############################################################################################################

    ###################     지도 좌표 받아오는 정보        ###################################################
    map_conn = None
    map_client_id = "CB54EED6-EA76-39F9-81EE-0B601E4B4FD0"

    # OpenAPI 접속 정보 information
    map_server = "http://api.vworld.kr"

    ############################################################################################################



    # smtp 정보
    # host = "smtp.gmail.com" # Gmail SMTP 서버 주소.
    # port = "587"

    # 챗 아이디
    chatId = '1164557859'
    # 텔레그램 챗 봇
    chatBot = telepot.Bot('1210310534:AAHwFLrsxmEJzDhTT-Gmp5vbZ_luN0aXUqg')


    DataList = []  # 검색해서 받은 정보를 저장할 리스트.
    sortData_Num = []  # 정렬할 때 사고 횟수 받는 컨테이너.....
    sortData = []  # 정렬할 때 지역 이름 받는 컨테이너...
    DataList_sortData = []  # 정렬되있는 데이터 받아놓는 컨테이너.....

    Data_to_tkinter = []  # 검색결과를 tkinter로 전달하는 컨테이너

    MapDataList = [] # 검색결과 지도 좌표 받는 컨테이너

    #그래프
    graph_title= None
    GraphCanvas = None
    graph_bar = []
    graph_label1 = []
    graph_label2 = []
    ################################################################
    #
    #   DataList
    #   0 : 시도군 이름
    #   1 : 사고 종류
    #   2 : 사고 횟수
    #
    #
    #
    #   추가 예정
    #
    #
    #        <acc_cl_nm>노인사고</acc_cl_nm>                  # 사고 종류
    #        <sido_sgg_nm>서울특별시 강남구</sido_sgg_nm>      # 사고 지역
    #        <acc_cnt>324</acc_cnt>                         # 사고 건수
    #        <acc_cnt_cmrt>0.86</acc_cnt_cmrt>              # 사고건수 구성비
    #        <dth_dnv_cnt>4</dth_dnv_cnt>                   # 사망자수
    #        <dth_dnv_cnt_cmrt>0.23</dth_dnv_cnt_cmrt>      # 사망자수 구성비
    #        <ftlt_rate>1.23</ftlt_rate>                    # 치사율
    #        <injpsn_cnt>347</injpsn_cnt>                   # 부상자수
    #        <injpsn_cnt_cmrt>0.86</injpsn_cnt_cmrt>        # 부상자수 구성비
    #        <tot_acc_cnt>37555</tot_acc_cnt>               # 대상사교별 총사고건수
    #        <tot_dth_dnv_cnt>1767</tot_dth_dnv_cnt>        # 대상사고별 총사망자수
    #        <tot_injpsn_cnt>40579</tot_injpsn_cnt>         # 대상사고별 총부상자수
    #
    #################################################################

    ###########         함수 부분 시작     ########################################################
    #############################################################################################
    #############################################################################################
    #############################################################################################

    def handle(self, msg):
        global chatBot, Data_to_tkinter
        #input = telepot.glance(msg)
        text = msg['text']
        self.FindAccFrom_SiDo_GuGun(text)

        if not Data_to_tkinter:
            chatBot.sendMessage(chatId, '지역명을 제대로 입력해 주세요.')
        else:
            for data in Data_to_tkinter:  # 입력받은 문자로 검색해서 출력한다.
                chatBot.sendMessage(chatId, '지역명 : ' + data[0] + '사고 종류 : ' + data[1] + '사고 횟수 : ' + str(data[2]))

    def sendMessageButtonPush(self):
        global chatBot, Data_to_tkinter

        for data in Data_to_tkinter:  # 입력받은 문자로 검색해서 출력한다.
            chatBot.sendMessage(chatId, '지역명 : ' + data[0] + '사고 종류 : ' + data[1] + '사고 횟수 : ' + str(data[2]))


    # 2020 / 06 / 17 김현식
    # gmail 로그인과 본인에게 Email 보내기 기능 구현
    def googleLoginAndSendEmail(self):
        global Data_to_tkinter
        import mimetypes
        import smtplib
        from email.mime.base import MIMEBase
        from email.mime.text import MIMEText

        htmlTxt = self.MakeHtmlDoc(Data_to_tkinter)

        senderAddr = ""
        recipientAddr = ""
        msg = MIMEBase("multipart", "alternative")
        msg['Subject'] = "AccTeamProject "+self.searchPlaceInput.get()+" 사고내역"
        msg['From'] = senderAddr
        msg['To'] = recipientAddr

        # MIME 문서를 생성
        #htmlFD = open(htmlFileName, 'rb')
        #HtmlPart = MIMEText(htmlFD.read(), 'html', _charset='UTF-8')
        #htmlFD.close()

        messagePart = MIMEText(htmlTxt, 'html', _charset='UTF-8')

        # 메세지에 생성한 MIME 문서를 첨부합니다.
        msg.attach(messagePart)

        # 메일 발송하기

        mySmtp = smtplib.SMTP("smtp.gmail.com", 587)
        mySmtp.ehlo()
        mySmtp.starttls()
        mySmtp.ehlo()
        mySmtp.login(senderAddr, "")
        mySmtp.sendmail(senderAddr, [recipientAddr], msg.as_string())
        mySmtp.close()

    def MakeHtmlDoc(self, searchReturn): # HTML로 변환
        from xml.dom.minidom import getDOMImplementation
        # get Dom Implementation
        impl = getDOMImplementation()

        newdoc = impl.createDocument(None, "html", None)  # DOM 객체 생성
        top_element = newdoc.documentElement
        header = newdoc.createElement('header')
        top_element.appendChild(header)

        # Body 엘리먼트 생성.
        body = newdoc.createElement('body')

        for item in searchReturn:
            # create 주소 엘리먼트
            where = newdoc.createElement('where')
            # create text node
            whereText = newdoc.createTextNode("   주소 :" + item[0])
            where.appendChild(whereText)

            body.appendChild(where)

            # BR 태그 (엘리먼트) 생성.
            br = newdoc.createElement('br')

            body.appendChild(br)

            # 사고 종류
            what = newdoc.createElement('what')
            # create text node
            whatText = newdoc.createTextNode("   사고 종류:" + item[1])
            what.appendChild(whatText)

            body.appendChild(what)

            # 사고 수
            howMany = newdoc.createElement('howMany')
            # create text node
            howManyText = newdoc.createTextNode("   사고 수:" + str(item[2]))
            howMany.appendChild(howManyText)

            body.appendChild(howMany)

            body.appendChild(br)  # line end

        # append Body
        top_element.appendChild(body)

        return newdoc.toxml()

    def ConnectOpenAPIServer(self):
        global conn, server
        conn = http.client.HTTPConnection(server)  # 받아올 정보에 필요한 여러 요소들 정의
        conn.set_debuglevel(1)

    def GetAllAccDataFromSidoSgg(self, searchYear):
        global server, conn, client_ID, client_secret, client_id, siDo, guGun, numOfRows, searchYearCd

        searchYearCd = str(searchYear)

        if conn == None:
            self.ConnectOpenAPIServer()
        conn.request("GET", "/B552061/lgStats/getRestLgStats?serviceKey=" + client_id + "&searchYearCd=" + searchYearCd + "&siDo=" + siDo + "&guGun=" + guGun + "&type=xml&numOfRows=" + numOfRows + "&pageNo=1&")

        req = conn.getresponse()
        print(req.status)
        if int(req.status) == 200:
            #print("All data downloading complete!")
            return self.ExtractAccData(req.read())
        else:
            print("OpenAPI request has been failed!! please retry")
            return None

    def ExtractAccData(self, strXml):
        global DataList
        from xml.etree import ElementTree

        DataList.clear()

        tree = ElementTree.fromstring(strXml)
        # Acc 엘리먼트를 가져옵니다.
        itemElements = list(tree.iter("item"))  # return list type

        for item in itemElements:
            sido_sgg_name = item.find("sido_sgg_nm")
            acc_cl_name = item.find("acc_cl_nm")
            acc_count = item.find("acc_cnt")
            if len(sido_sgg_name.text) > 0:
                DataList.append((sido_sgg_name.text, acc_cl_name.text, acc_count.text))
        b = set(DataList)
        DataList = list(b)
        self.sortByName(DataList)

    # 2020. 06. 17
    # 맵 좌표 데이터 받아오기
    def GetAllMapDataFromSidoSgg(self, searchWord):
        global map_client_id, map_server

        map_req = requests.get("http://map.vworld.kr/search.do?category=jibun&q="+searchWord+"&pageunit=10000&output=xml&pageindex=100&apiKey="+map_client_id)
        map_req.status_code

        return self.ExtractMapData(map_req.text)

    # 2020. 06. 17
    # 맵 좌표를 검색한 이름으로 받아와서 저장하기.
    def ExtractMapData(self, strXml):
        global MapDataList
        from xml.etree import ElementTree

        MapDataList.clear()

        tree = ElementTree.fromstring(strXml)
        # Acc 엘리먼트를 가져옵니다.
        itemElements = list(tree.iter("item"))  # return list type
        for item in itemElements:
            road_name = item.find("JUSO")
            point_x = item.find("xpos")
            point_y = item.find("ypos")
            print(road_name.text + "  : " + point_x.text + " " +point_y.text)
            if len(road_name.text) > 0:
                MapDataList.append((road_name.text, point_x.text, point_y.text))
        b = set(MapDataList)
        MapDataList = list(b)
        self.sortByName(MapDataList)
        pass


    def sortFromAllAcc(self, DataList, areaKey):
        global sortData, sortData_Num, DataList_sortData
        DataList_sortData.clear()
        sortData.clear()
        sortData_Num.clear()
        areaName = ""
        dataNum = 0
        getAreaNum = 0
        if areaKey == "d":
            getAreaNum = 0
        else:
            getAreaNum = 1

        for data in DataList:  # 뱅뱅 돌면서 '도'가 같으면 사고 수에 추가, 다르면 새로 appand
            if (len(data[0].split(' ')) == 2):
                if areaName != data[0].split(' ')[getAreaNum]:
                    areaName = data[0].split(' ')[getAreaNum]

                    if getAreaNum == 0:  # '도' 기준일 때는 도만, 아닐 때는 전부 넣어준다.
                        sortData.append(data[0].split(' ')[getAreaNum])
                    else:
                        sortData.append(data[0])  # 구 기준일 때. 전체 이름 넣어줌.

                    if dataNum != 0:
                        sortData_Num.append(dataNum)
                        dataNum = 0
                    else:
                        dataNum += int(data[2])
                else:
                    dataNum += int(data[2])

        if dataNum != 0:
            sortData_Num.append(dataNum)
            dataNum = 0

        for i in range(len(sortData)):
            DataList_sortData.append((sortData[i], "전체사고", int(sortData_Num[i])))

        DataList_sortData.sort(key=lambda x: -x[2])


    def sortFromIndividualAcc(self, DataList, areaKey, kindsKey): # 사고별로 나눴을 때, 도/군 기준으로 나눠 데이터를 분류하고, DataList_sortData에 넣은 후 소트.
        global sortData, sortData_Num, DataList_sortData
        DataList_sortData.clear()
        sortData.clear()
        sortData_Num.clear()
        areaName = ""
        dataNum = 0
        getAreaNum = 0
        getAcc = ""
        if areaKey == "d":
            getAreaNum = 0
        else:
            getAreaNum = 1
        if kindsKey == "o":
            getAcc = "노인사고"
        elif kindsKey == "w":
            getAcc = "보행자사고"
        elif kindsKey == "n":
            getAcc = "야간사고"
        elif kindsKey == "c":
            getAcc = "어린이사고"
        elif kindsKey == "b":
            getAcc = "자전거사고"

        for data in DataList:  # 뱅뱅 돌면서 '도'가 같으면 사고 수에 추가, 다르면 새로 appand
            if (len(data[0].split(' ')) == 2):
                if areaName != data[0].split(' ')[getAreaNum] and getAcc == data[1]:
                    areaName = data[0].split(' ')[getAreaNum]

                    if getAreaNum == 0:  # '도' 기준일 때는 도만, 아닐 때는 전부 넣어준다.
                        sortData.append(data[0].split(' ')[getAreaNum])
                    else:
                        sortData.append(data[0])
                        dataNum += int(data[2])

                    if dataNum != 0:  # '도' 기준일 때, 데이터 받아서 넣어주기
                        sortData_Num.append(dataNum)
                        dataNum = 0

                elif getAcc == data[1]:  # '도' 기준일 때, 다른 구의 사고 수를 더해주기
                    dataNum += int(data[2])
        if dataNum != 0:
            sortData_Num.append(dataNum)
            dataNum = 0

        for i in range(len(sortData)):
            DataList_sortData.append((sortData[i], getAcc ,sortData_Num[i]))

        DataList_sortData.sort(key=lambda x: -x[2]) # 사고 횟수를 기준으로 소트
        sortData_Num.clear()
        sortData.clear()

    def searchSortData(self, DataList, areaKey, totalKey, kindsKey): # 도/군 * 사고종류 기준으로 정렬할 기준 받고, 우선 사고 종류 기준으로 나눠서 함수 실행
        global DataList_sortData, sortData_Num, sortData

        DataList_sortData.clear()
        sortData_Num.clear()
        sortData.clear()

        if totalKey == "t":  # 전부 받을 때.
            self.sortFromAllAcc(DataList, areaKey)
        else:
            self.sortFromIndividualAcc(DataList, areaKey, kindsKey)

    def FindAccFrom_SiDo_GuGun(self, find_SidoName): # 검색한 도/군 기준으로 사고 찾아 Data_to_tkinter로 데이터 넣고 리턴
        global DataList, Data_to_tkinter, searchYearCd
        Data_to_tkinter.clear()

        print(self.comboBoxYear.get())
        if searchYearCd != self.comboBoxYear.get():
            self.GetAllAccDataFromSidoSgg(self.comboBoxYear.get())

        splitData = []
        for data in DataList:
            splitData = data[0].split(" ")

            for checker in splitData:
                if checker == find_SidoName:
                    Data_to_tkinter.append((data[0], data[1], int(data[2])))
        return Data_to_tkinter

    def sortByName(self, DataList):
        DataList.sort(key=lambda x: x[0])


    # 웹 브라우저로 지도 띄우기
    def Map_Pressed(self):
        global MapDataList, Data_to_tkinter

        allX = 0
        allY = 0
        count = 0
        for data in MapDataList:
            allX += float(data[1])
            allY += float(data[2])
            count += 1
        mapX = allX / count
        mapY = allY / count

        if len(Data_to_tkinter) > 6:
            zoom = 9
        else:
            zoom = 13

        # 위도 경도 지정
        map_osm = folium.Map(location=[mapY, mapX], zoom_start=zoom)
        # 마커 지정
        #folium.Marker([mapY, mapX], popup="").add_to(map_osm)
        # html 파일로 저장
        map_osm.save('osm.html')
        webbrowser.open_new('osm.html')


    def sendMessage(self, message): # 텔레그램 봇으로 메세지 보내기
        global chatBot, chatId
        chatBot.sendMessage(chatId, message)

    def DataSaveAndDataFree():
        global DataList, sortData_Num, sortData, DataList_sortData, searchYearCd, fileName

        file = open(fileName, 'w')  # 쓰기전용 파일 열기
        file.write(searchYearCd + "\n")
        for i in DataList:
            for j in i:
                file.write(j + " ")
            file.write("\n")
        file.close()

        DataList.clear()
        sortData.clear()
        sortData_Num.clear()
        DataList_sortData.clear()

    def LoadData(self):
        import os.path
        global DataList, searchYearCd, fileName

        try:
            file = open(fileName, 'r')  # 읽기전용 파일 열기
        except: # 파일 없음.
            return False

        tempList = file.readlines()

        check = 0
        for data in tempList:
            if check == 0:
                searchYearCd = data
                check += 1
            else:
                if data != '\n':
                    temp = data.split()
                    if temp[0] == "세종특별자치시":
                        DataList.append((temp[0], temp[1], temp[2]))
                    else:
                        DataList.append((temp[0] + " " + temp[1], temp[2], temp[3]))

        file.close()


    ###########         함수 부분 끝     ##########################################################
    #############################################################################################
    #############################################################################################
    #############################################################################################




    def __init__(self):
        self.window = Tk()
        self.window.title("교통사고 알리미")
        self.window.geometry("600x650")

        self.setupLayout()
        self.comboBoxYear = StringVar()
        self.yearSearchComboBox() #연도리스트박스

        ##self.info_map = InfoMap()
        self.canvas_height = 100
        self.result_search = None

        self.tab = None

        self.frame_search = None
        self.frame_sort = None
        self.frame_map = None
        self.frame_bookmark = None
        self.sort_list = []

        self.SearchEntry = None

        self.mapLabel = None
        self.mapSortList = None
        self.InfoSortList = None
        self.InfoNameList = None
        self.InfoTitleListBox = None
        self.InfoListBox = None

        fileCheck = self.LoadData()
        if fileCheck == False:
            self.GetAllAccDataFromSidoSgg(2018)
        chatBot.message_loop(self.handle)




        self.window.mainloop()


    def setupLayout(self):
        self.tab = ttk.Notebook()
        self.tab.pack()
        self.tab.place(x=25, y=80)
        self.frame_search = ttk.Frame(self.window, width=550, height=530, relief=SOLID)
        self.frame_bookmark = ttk.Frame(self.window, width=550, height=530, relief=SOLID)

        self.tab.add(self.frame_search, text='검색')
        self.tab.add(self.frame_bookmark, text='북마크')

        self.SearchLabel = Label(self.window, text="지역명 검색")
        self.SearchLabel.place(x=25, y=50)
        self.searchPlaceInput = StringVar()
        self.SearchEntry = Entry(self.window, textvariable=self.searchPlaceInput)
        self.SearchEntry.place(x=95, y=50)
        self.SearchButton = Button(self.window, text="확인", command=self.Search)
        self.SearchButton.place(x=240, y=46)



        ##로고그림추가
        self.logo=PhotoImage(file="교통사고알리미.gif")
        self.logo_label=Label(self.window, image=self.logo)
        self.logo_label.place(x=280, y=8)


        # 수정 : 2020/06/06, 김현식
        # 사유 : 라벨 대신 텍스트 박스를 만들어서 검색 결과를 받아온다.
        global RenderText
        RenderTextScrollbar = Scrollbar(self.frame_search)
        RenderTextScrollbar.pack()
        RenderTextScrollbar.place(x=375, y=200)

        #TempFont = font.Font(self.frame_search, size=10, family='Consolas')
        RenderText = Text(self.frame_search, width=70, height=25, borderwidth=12, relief='ridge',
                          yscrollcommand=RenderTextScrollbar.set)
        RenderText.pack()
        RenderText.place(x=10, y=10)
        RenderTextScrollbar.config(command=RenderText.yview)
        RenderTextScrollbar.pack(side=RIGHT, fill=BOTH)
        RenderText.configure(state='disabled')
        #################################
        #################################
        ##그래프부분
        global GraphCanvas
        GraphCanvas = Canvas(self.frame_search, bg="white", height=150, width=500, borderwidth=5, relief='ridge')
        GraphCanvas.pack()
        GraphCanvas.place(x=13, y=365)

        for i in range(5):
            tmp = Label(self.frame_search, text='')
            tmp.pack()
            tmp.place(x=0, y=0)
            graph_label1.append(tmp)

        for i in range(5):
            tmp = Label(self.frame_search, text='')
            tmp.pack()
            tmp.place(x=0, y=0)
            graph_label2.append(tmp)
        # 수정 : 2020/06/15, 김현식
        # 사유 : 지도 출력버튼 생성
        self.mapimg = PhotoImage(file="googlemap.gif")
        self.mapButton = Button(self.window,text = 'google map!', image=self.mapimg, command=self.Map_Pressed)
        self.mapButton.place(x=410, y=60)

        #이메일 출력버튼 생성
        self.mailimg = PhotoImage(file="googlemail.gif")
        self.mapButton = Button(self.window,text = 'google mail!', image=self.mailimg, command=self.googleLoginAndSendEmail)
        self.mapButton.place(x=460, y=60)

        #텔레그램 출력버튼생성
        self.telegramimg = PhotoImage(file="telegramlogo.gif")
        self.mapButton = Button(self.window, text='google mail!', image=self.telegramimg, command=self.sendMessageButtonPush)
        self.mapButton.place(x=510, y=60)


    def SelectSortData(event):
        pass

    def Search(self):
        global RenderText, Data_to_tkinter, DataList_sortData
        #locationName = Label(self.frame_search, text=self.result_search)
        #locationName.place(x=170, y=10) ##요런식

        RenderText.configure(state='normal')
        RenderText.delete(0.0, END)
        self.FindAccFrom_SiDo_GuGun(self.searchPlaceInput.get())
        self.GetAllMapDataFromSidoSgg(self.searchPlaceInput.get()) # 검색한 지역 좌표 받아오기.

        #self.googleLoginAndSendEmail() # 이메일이긴 한데 안될듯. 된다 시바

        for data in Data_to_tkinter:  # 입력받은 문자로 검색해서 출력한다.
            RenderText.insert(INSERT, '지역명 : ')
            RenderText.insert(INSERT, data[0])
            RenderText.insert(INSERT, '\n')
            RenderText.insert(INSERT, '사고 종류 : ')
            RenderText.insert(INSERT, data[1])
            RenderText.insert(INSERT, '\n')
            RenderText.insert(INSERT, '사고 횟수 : ')
            RenderText.insert(INSERT, data[2])
            RenderText.insert(INSERT, '\n\n\n\n')
        RenderText.configure(state='disabled')

        if len(Data_to_tkinter) <= 6: # 구 로 검색한 경우
            DataList_sortData.clear()
            Data_to_tkinter.sort(key=lambda x: -x[2])  # 5개밖에 안나오니까 그냥 횟수로 소트.
            DataList_sortData = copy.deepcopy(Data_to_tkinter)

        else: # 큰 지역으로 검색한 경우
                # 구 별로 사고의 총합끼리 비교해서 소트한다.
            self.sortFromAllAcc(Data_to_tkinter, "구별로구하기")  # 이렇게 넣어주면 검색한 지역 내의 구별 사고 횟수 소트가 나온다.
        self.UpdateGraph()

    def SortData(self):
        pass

    ##그래프부분
    def UpdateGraph(self):
        global GraphCanvas, graph_bar, DataList_sortData, RenderText, graph_label1, graph_label2, graph_title

        RenderText.configure(state='normal')
        RenderText.insert(INSERT, '함수들어왔다.')

        for bar in graph_bar:
            GraphCanvas.delete(bar)  # 초기화
        graph_bar.clear()
        count = 0
        bestRecod = DataList_sortData[0][2] / 110
        for i in DataList_sortData:

            if len(DataList_sortData) < 7:
                graph_label2[count].configure(text=i[1])
                startXName = 30
                startXCount = 50
            else:
                graph_label2[count].configure(text=i[0].split(' ')[1])
                startXName = 40
                startXCount = 45

            graph_label1[count].configure(text=i[2])
            graph_label1[count].pack()
            graph_label1[count].place(x=(startXCount + (count * 100)), y=482 - i[2] / bestRecod)


            graph_label2[count].pack()
            graph_label2[count].place(x=(startXName + (count * 100)), y=500)

            rect = (40 + (count * 100)), 140 - i[2] / bestRecod, (55 + (count * 100)), 140
            graph_bar.append(GraphCanvas.create_rectangle(rect, fill="blue"))

            count += 1
            if (count == 5):
                break

    ##연도콤보박스
    def yearSearchComboBox(self):
        self.YearLabel = Label(self.window, text="연도")
        self.YearLabel.place(x=60, y=20)
        # self.YearCombo = StringVar()
        self.YearCombo = ttk.Combobox(self.window, width=9, textvariable=self.comboBoxYear)
        self.YearCombo['values'] = (2012, 2013, 2014, 2015, 2016, 2017, 2018)  ##연도
        self.YearCombo.bind("<<ComboboxSelected>>", self.year_event)  ##연도
        self.YearCombo.place(x=95, y=20)

        self.YearCombo.current(6)

    def year_event(self, event): ##연도넣으면 그연도에 맞는 교통사고정보
        pass


MainGUI()


