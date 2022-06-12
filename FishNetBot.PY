# -*- coding : utf-8 -*-

r'''
                                           必看
FishNetBot 作者: Flysmallfish

FishNetBot是一个整合了（基本都是自己做的）很多站内爬虫的机器人
你们可以自己看看函数。


注意 ： r.mcModBot.mcModSearch 跟 r.mcModBot.itemParse 的返回值不大一样，
r.mcModBot.mcModSearch 返回的是二维列表，示例：

    items = r.mcModBot.mcModSearch("枪械",class_ = 0 , mold = 0 , page = 1 , getNums = 10 , logo = True)
    for i in items:
        print(i[0]+"\n链接 : "+i[1] + " \n介绍 : "+i[2] + " \nlogo : "+i[3]+"\n\n")

r.mcModBot.itemParse 返回的是字典套列表如：
    {'state': ['活跃', '开源'], 'shortName': '[AoA3]', 'zhName': '虚无世界3', 'enName': 'Advent of Ascension 3', 'classes': ['资源', '世界', '群落', '结构', '生物', '存储', '道具', '红石', '食物', '模型', '关卡', '指南', '破坏', '西式', '恐怖', '建材', '生存', '指令'], 'tags': '暂时没有做'}


'''
import requests
import time

from concurrent.futures import ThreadPoolExecutor  #这个跟下载有关哦！ 
import os
from lxml import etree     #导库！s
import urllib.parse
from threading import Thread #多线程
import json #json处理

#======================================
global myHeader,us_proxy

myHeader = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
           'Accept': '*/*', 'Accept-Encoding': 'gzip', 'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,mt;q=0.6'}                                #模拟人类信息

#--------------------------代理----------------------------
us_proxy = {
    'http:':'154.7.7.214:80'
}
#--------------------------嘿嘿----------------------------
print("[FishNetBot] 加载完毕!  -  作者: FlySmallFish  -  许可证: GPLv3.0  -  开源地址: qwq\n")
#----------------------------------------------------------

class downloader:
    def __init__(self, url, num, name):
        self.url = url
        self.num = num
        self.name = name
        self.getsize = 0
        r = requests.head(self.url, allow_redirects=True)
        self.size = int(r.headers['Content-Length'])

    def down(self, start, end, chunk_size=10240):
        headers = {'range': f'bytes={start}-{end}'}
        r = requests.get(self.url, headers=headers, stream=True)
        with open(self.name, "rb+") as f:
            f.seek(start)
            for chunk in r.iter_content(chunk_size):
                f.write(chunk)
                self.getsize += chunk_size

    def main(self):
        start_time = time.time()
        f = open(self.name, 'wb')
        f.truncate(self.size)
        f.close()
        tp = ThreadPoolExecutor(max_workers=self.num)
        futures = []
        start = 0
        for i in range(self.num):
            end = int((i+1)/self.num*self.size)
            future = tp.submit(self.down, start, end)
            futures.append(future)
            start = end+1
        while True:
            process = self.getsize/self.size*100
            last = self.getsize
            time.sleep(1)
            curr = self.getsize
            down = (curr-last)/1024
            if down > 1024:
                speed = f'{down/1024:6.2f}MB/s'
            else:
                speed = f'{down:6.2f}KB/s'
            print(f'process: {process:6.2f}% | speed: {speed}', end='\r')
            if process >= 100:
                print(f'process: {100.00:6}% | speed:  00.00KB/s', end=' | ')
                break
        tp.shutdown()
        end_time = time.time()
        total_time = end_time-start_time
        average_speed = self.size/total_time/1024/1024
        print(f'total-time: {total_time:.0f}s | average-speed: {average_speed:.2f}MB/s')



class r():
    def easyGet (url) :
        global myHeader
        try:
           StrHtml=requests.get(url, headers=myHeader);
           return StrHtml                                   #简单获取网页源代码

        except Exception as error:
           raise Exception("NoNetwork")

    def fx (url):
        ym = urllib.parse.urlparse(url).hostname
        yms = {"www.curseforge.com":"Curseforge", "www.spigotmc.org" : "spigot",
               "github.com":"github" , "www.planetminecraft.com":"planetminecraft",
               "www.mcbbs.net":"mcbbs" , "gitee.com" : "gitee" , 
               "discord.gg":"discord" , "www.minecraftforum.net":"minecraftforum"}

        try:
            return yms[ym]
        except:
            return "other"


    class mcModBot () :
        def mcModSearch(key,class_=None , mold = None , page = None , getNums = None , logo = None):
            """class_(分类，注意值是整数) 全部:0 模组:1  整合包:2 资料:3 教程:4 作者:5 用户:6 社群:7 (← 找作者/用户/社群干嘛呀，直接用网页不好吗) !!!服务器暂不收录!!!
               mold (搜索模式) 简单搜索:0 复杂搜索:1
               page (搜索的页数) 从1开始                         """

            #这是URL的拼接
            su="https://search.mcmod.cn/s?key="+key

            class_ = str(class_); mold = str(mold); page = str(page)
            if class_ == 'None':
                class_ = "0"
            if mold == 'None':
                mold = "0"
            if page == 'None':
                page = "0"                  #这几个是转换
            if getNums == None:
                getNums = 1;    #前面几个是拼接需要的，而这个是解析需要的

            su=su+"&site=&filter="+class_+"&mold="+mold+"&page="+page  #正式拼接网址

            print("[FishNetBot|INFO] mcModBot . mcModSearch: 解析 "+su+" 中ing\n")
            #===================解析===================================

            searchHtmlStr=r.easyGet(su).text.replace("<em>",'').replace("</em>",'')  
            #在mcmod的搜索中，搜索的关键词会被em标红，导致我们爬虫时爬不到em标签里面的内容，所以这里我们去掉em标签
            searchHtml=etree.HTML(searchHtmlStr) 


            itemsJd='/html/body/div/div/div[2]/div/div[4]/div'  #节点 示例：节点里面 /html/body/div/div/div[2]/div/div[4]/div/div[1]  节点标题/html/body/div/div/div[2]/div/div[4]/div/div[哪个]/div[1]/a
            
            itemsList=[]
            #---------------------Logo多线程预处理-----------------

            if logo == True:

                urls = []

                for i in range(1,getNums+1):
                    try:

                        item=itemsJd+"/div["+str(i)+"]"
                        itemUrl=item+"/div[1]/a/@href" ; itemUrl=searchHtml.xpath(itemUrl)[0]
                        urls.append(itemUrl)
                    except:

                        break

                logo_xc = Thread(target=r.mcModBot.superLogo, args= (urls,) ) #建立 获取logo的主函数 线程
                logo_xc . start()

            #-----------------------------------------------------

            i2 = 0
            
            for i in range(1,getNums+1):

                try:

                    now=[]

                    item=itemsJd+"/div["+str(i)+"]"

                    itemTitle=item+"/div[1]/a/text()" ; itemTitle=searchHtml.xpath(itemTitle)[0] #反正就是xpath 浏览器可以生成很简单
                    
                    itemJs=item+"/div[2]/text()" ; itemJs=searchHtml.xpath(itemJs)[0]

                    itemUrl=item+"/div[1]/a/@href" ; itemUrl=searchHtml.xpath(itemUrl)[0]

                    now.append(itemTitle)
                    now.append(itemUrl)
                    now.append(itemJs)


                    if logo == None or logo == False:
                        now.append("[FishNetBot] 你没有启用获取Logo功能。")
                    elif logo == True:
                        logo_xc.join()
                        if ilogos[i-1] != '':
                            now.append( "https:"+ilogos[i-1] )
                        now.append('[FishNetBot] "'+itemTitle+'" 的Logo没有被找到。' )

                    itemsList.append(now)


                except Exception as error:
                    if str(error) != "list index out of range":
                        print("[FishNetBot|ERROR] 错误！请将一下信息向作者报告！"+str(error)+"\n")

                    break

            return itemsList

        def superLogo(urls):
            '''URLS 为放置URL的LIST'''

            global ilogos
            ilogos = ["","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""] #放置 Logo 的列表 
            xcs = []     #放置 多线程的列表
            n=0

            for i in urls:                         #首先全部线程开始处理
                nxc=Thread(target=r.mcModBot.SuperLogoGet, args=(i,"ilogos",n,))
                xcs.append(nxc)
                xcs[n].start()
                n = n+1

            for i in xcs:
                i.join()

            return ilogos


        def itemLogoGet (url):
            itemHtml=etree.HTML(r.easyGet(url).text) 
            itemLogoUrl=itemHtml.xpath("/html/body/div[2]/div/div[2]/div[1]/div[1]/img/@src")[0]
            return itemLogoUrl

        def SuperLogoGet (url,g,num):
            '''num可以是STR或者数字'''

            exec("global "+g)
            try:
                itemHtml=etree.HTML(r.easyGet(url).text) 
                itemLogoUrl=itemHtml.xpath("/html/body/div[2]/div/div[2]/div[1]/div[1]/img/@src")[0]
                exec(g+"["+str(num)+"] = "+'"'+itemLogoUrl+'"')
            except:
                pass
            


        def itemParse (url):
            print("[FishNetBot|INFO] mcModBot . itemParse: 解析 "+url+" 中ing\n")

            strhtml = r.easyGet ( url ) . text

            itemHtml=etree.HTML ( strhtml )

            #-------------------获取  状态----------------------
            itemStatesPath = '/html/body/div[2]/div/div[2]/div[2]/div[1]/div[1]/div'
            itemStatesList = []

            '''因为MCMOD.CN的原因，一个状态和两个状态的模组，它们的xpath是不同的，所以
            我们这里如果第一次没有检测到，那它应该只有一个状态，然后我们再试着解析，应该就行了。
                                     ↓↓↓↓↓↓↓↓↓↓↓↓↓                                    '''

            for i in range(1,4):            
                NowStatePath = itemStatesPath + "/div["+str(i)+"]/text()"
                NowState= itemHtml . xpath (NowStatePath) 
          
                if NowState != [] :
                    itemStatesList . append ( NowState[0] )                

                elif i == 1:
                    #           第二次尝试解析
                    State2 = itemHtml . xpath ("/html/body/div[2]/div/div[2]/div[2]/div[1]/div[1]/div/text()") 
                    
                    if State2 != [] :
                        itemStatesList . append ( State2[0] )
                    #=========================================================================================

                else:
                    break

            #--------------------获取短名如 [TF]、[IC2]等-------
            try:
                itemShortName = itemHtml . xpath ("/html/body/div[2]/div/div[2]/div[2]/div[1]/div[1]/span/text()")[0]
            except:
                itemShortName = "(NoShortName)"                  #若没有短名就设为 (NoShortName) (没有短名)     

            #-------------------获取中文名----------------------
            itemZhName = itemHtml . xpath ("/html/body/div[2]/div/div[2]/div[2]/div[1]/div[1]/h3/text()") [0]

            #-------------------获取英文名----------------------
            itemEnName = itemHtml . xpath ("/html/body/div[2]/div/div[2]/div[2]/div[1]/div[1]/h4/text()") [0]

            #-------------------获取  分类----------------------
            itemClassesList = []
            itemClassesPath = "/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[1]/ul"

            for i in range(2,30):            
                NowClassPath = itemClassesPath+"/li["+str(i)+"]/a/text()"
                NowClass= itemHtml . xpath (NowClassPath)   #一直爬取下一个分类，如果这个分类不是空的，就加进分类
                                                            #的列表(itemClassesList)如果是空的，那就不爬了(break)
                if NowClass != [] :
                    itemClassesList . append ( NowClass[0] ) 
                else:
                    break               

            #-------------------较重要信息收集------------------ (如支持平台、运作方式等)
            itemOthInfo = [itemHtml . xpath ('/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/ul/li[1]/a/text()') [0],                #支持平台
                           itemHtml . xpath ('/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/ul/li[2]/a/text()') [0],                #运作方式
                           itemHtml . xpath ('/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/ul/li[3]/text()')   [0],                #运行环境
                           itemHtml . xpath ('/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/div/div[1]/div[1]/p[1]/text()')[0]]     #热度指数
            itemLogoUrl=itemHtml.xpath("/html/body/div[2]/div/div[2]/div[1]/div[1]/img/@src")[0] 

            #-------------------相关链接获取---------------------  
            itemLinks = []

            itemLinksName = []

            itemLinksPath = "/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/ul/div/div[2]/ul"
                                #/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/ul/div/div[2]/ul/li[1]/script/text()

            for i in range(1,9999999999):
                try:
                    NowDownLinkName = itemHtml . xpath (itemLinksPath+"/li["+str(i)+"]/a/@data-original-title") [0]

                    NowDownLinkPath = itemLinksPath+"/li["+str(i)+"]/script/text()"  #下载链接藏在一个JS里面 
                                        
                    NowLink = itemHtml . xpath (NowDownLinkPath) [0] [94:]   #截取

                    wz=NowLink.find('</strong></p><br/>')

                    itemLinks.append(NowLink.replace(NowLink[wz:],''))
                    itemLinksName . append (NowDownLinkName)
                except:
                    break
            
            #-------------------简介 获取----------------------
            synopsis = itemHtml.xpath('//li[@class="text-area common-text font14"]') 
            synopsisList = []
            for e in synopsis:
                synopsisList.append(str(e.xpath('string(.)')).replace('\n','').strip())


            synopsisTxt=''.join(synopsisList)

            #-------------------下载  检测----------------------

            downText = itemHtml .xpath ("//text()[contains(., 'Mod下载')]/parent::*/span/text()")[0] 
            print("MCMOD文件数量 ： " + downText)
            if downText == "(0)":
                downInMcMod = False  #//text()[contains(., 'Mod下载')]是查找文本 Mod下载 的节点 /parent::*是查找父节点
            else:                    #/span/text()获取父节点下span文本信息（下载文件数量）
                downInMcMod = True
            #-------------------相关链接分析--------------------
            CurseforgeLinks = []

            for l in itemLinks:
                if r.fx(l) == "Curseforge":
                    CurseforgeLinks . append (l)

            #-------------------返回获取值----------------------
            return {"state" : itemStatesList ,                                                                      #模组的状态
                 "shortName" : itemShortName , "zhName" : itemZhName , "enName" : itemEnName , "logo" : itemLogoUrl,#模组的一些名字，logo
                  "classes" : itemClassesList , "tags" : "暂时没有做",                                               #分类之类的
                  "othInfo" : itemOthInfo , "links" : itemLinks , "linksName" : itemLinksName,                      #其他信息+链接
                  "synopsis": synopsisTxt [0:363],
                  "mcModDown": downInMcMod,
                  "CurseLinks":CurseforgeLinks}

            #return [itemStatesList,itemShortName,itemZhName,itemEnName,itemClassesList,"暂时没有做"]


            #做完咯！！！！！！！！！！！！！！！！！！！！芜湖！！！！！5.26 20:14！！！！！！！！！！！！！！！！

        def downFilenameGet (url):
            url = url .replace("class","download")

            try:
                downHtml=etree.HTML ( r.easyGet ( url ) . text)
            except:
                raise Exception("Error: (该页面可能没有下载部分！)")


            form = "/html/body/div[2]/div/div[2]/div[3]/table/tbody"

            lists = []

            for i in range(1,114514):
                now = form + "/tr[" + str(i) +"]"

                filename = downHtml . xpath(now+"/td[2]/text()")
                if filename == []:
                    break
                else:
                    filename = filename[0]

                api = downHtml . xpath (now + "/td[1]/span[2]/text()")[0]

                try:
                    level = downHtml . xpath (now + "/td[1]/span[3]/text()")[0]
                except:
                    level = "正式版"

                mcversion = downHtml .xpath (now+"/td[3]/text()") [0]
                time = downHtml . xpath (now+"/td[7]/text()")[0]
                
                lists.append([filename,api,level,mcversion,time])

            return lists

#-----------------------------芜湖 McMod爬虫做完了 --------------------------------
    class curseAPI():
        '''这个类我都是用curseforge官方API的，网址:https://docs.curseforge.com/'''

        def __init__(self, apiKey):
            self . apiKey = apiKey                  #转为类内的变量
            self . headers = {                      #设置请求头
                'Accept': 'application/json',
                'x-api-key': self.apiKey
                }

        def searchMods(self, gameId, classId=None, categoryId=None, gameVersion=None, keyWords=None, sortField=None, sortOrder=None, modLoaderType=None, gameVersionTypeId=None, slug=None, index=None, pageSize=None):
            '''
            Curse官方文档URL: https://docs.curseforge.com/
            Curse官方原文:
            Name                In      Type                Required    Description
            gameId              query   integer(int32)      true        Filter by game id.
            classId             query   integer(int32)      false       Filter by section id (discoverable via Categories)
            categoryId          query   integer(int32)      false       Filter by category id
            gameVersion         query   string              false       Filter by game version string
            searchFilter        query   string              false       Filter by free text search in the mod name and author
            sortField           query   ModsSearchSortField false       Filter by ModsSearchSortField enumeration
            sortOrder           query   SortOrder           false       'asc' if sort is in ascending order, 'desc' if sort is in descending order
            modLoaderType       query   ModLoaderType       false       Filter only mods associated to a given modloader (Forge, Fabric ...). Must be coupled with gameVersion.
            gameVersionTypeId   query   integer(int32)      false       Filter only mods that contain files tagged with versions of the given gameVersionTypeId
            slug                query   string              false       Filter by slug (coupled with classId will result in a unique result).
            index               query   integer(int32)      false       A zero based index of the first item to include in the response,
            pageSize            query   integer(int32)      false       The number of items to include in the response,
    
            注意了！！！！！！！！！！！！！！！！
            keyWords在官方api中为 searchFilter'''
            par = {'gameId': str(gameId)}                  #创建默认的 get 参数字典
            if classId != None:
                par['classId'] = str(classId)              #将亿些参数追加到字典par
            if categoryId != None:
                par['categoryId'] = str(categoryId)
            if gameVersion != None:
                par['gameVersion'] = gameVersion
            if keyWords != None:
                par['searchFilter'] = keyWords        #这里比较特殊,因为我把'searchFilter'改了个名儿
            if sortField != None:
                par['sortField'] = str(sortField)
            if sortOrder != None:
                par['sortOrder'] = sortOrder
            if modLoaderType != None:
                par['modLoaderType'] = str(modLoaderType)
            if gameVersionTypeId != None:
                par['gameVersionTypeId'] = str(gameVersionTypeId)
            if slug != None:
                par['slug'] = slug
            if index != None:
                par['index'] = str(index)
            if pageSize != None:
                par['pageSize'] = str(pageSize)
            #--------完成追加------------------------------
            
            r = requests.get('https://api.curseforge.com/v1/mods/search', params=par,headers = self.headers)

            #-------json解析-------------------------------
            searchInfos = json.loads(r.text)
            searchInfos_data = searchInfos['data']
            myInfo = []

            for i in searchInfos_data:
                nowItem = {}
                nowItem['id'] = i['id']         #Curse id
                nowItem['gameId'] = i['gameId'] #游戏ID
                nowItem['name'] = i['name']     #名称
                nowItem['slug'] = i['slug']     #SLUG(不知道是啥)
                nowItem['links'] = i['links']   #很多相关链接
                nowItem['summary'] = i['summary']#简介
                nowItem['status'] = i['status'] #地位(机翻，大概就是这么个意思)
                nowItem['downloadNum'] = i['downloadCount'] #下载数
                nowItem['hot'] = i['isFeatured'] #精选/热门
                nowItem['primaryCategoryId'] = i['primaryCategoryId'] #主要类别ID(机翻)
                nowItem['like'] = []

                for j in i['categories']:                       #类似的MOD，步骤跟之前一样~
                    nls = {}
                    nls['id'] = j['id']         #Curse id
                    nls['gameId'] = j['gameId'] #游戏ID
                    nls['name'] = j['name']     #名称
                    nls['slug'] = j['slug']     #SLUG(不知道是啥)

                    nowItem['like'] . append(nls)

                nowItem['classId'] = i['classId'] #类标识
                nowItem['authors'] = i['authors'] #作者id，名字，链接
                nowItem['logo'] = [i['logo']['thumbnailUrl'],i['logo']['url']] #LOGO 缩略图 + 原图
                nowItem['screenshots'] = i['screenshots'] #截图

                #接下来，我们来到了文件方面
                nowItem['mainFileId'] = i['mainFileId']  #主文件ID
                nowItem['latestFiles'] = i['latestFiles']      #最新文件
                #接下来是时间方面
                nowItem['creatTime'] = i['dateCreated']    #创建时间
                nowItem['dateModified'] = i['dateModified']#修改时间
                nowItem['dateReleased'] = i['dateReleased']#发布日期
                nowItem['fenFa'] = i['allowModDistribution']#是否允许分发
                nowItem['canUse'] = i['isAvailable']       #可用
                #ok完成了
                myInfo.append(nowItem)

        
            #返回~~~~
            return myInfo

        def modDescription(self,modId):
            html = etree.HTML(json.loads(requests.get('https://api.curseforge.com/v1/mods/'+str(modId)+'/description',headers = self.headers).text)['data'])
            Description = html.xpath('//li') 
            DescriptionList = []
            for e in Description:
                DescriptionList.append(str(e.xpath('string(.)')).replace('\n','').strip())

            DescriptionTxt=''.join(DescriptionList)

            return DescriptionTxt

        



if __name__ == "__main__":
    '''items = r.mcModBot.mcModSearch("枪械",class_ = 0 , mold = 0 , page = 1 , getNums = 10 , logo = True)

    for i in items:
        print(i[0]+"\n链接 : "+i[1] + " \n介绍 : "+i[2] + " \nlogo : "+i[3]+"\n\n")'''
    
    '''url = 'http://us-file.sikomc.xyz/Play_V1.0.0.zip'
    down = downloader(url, 16, 'Nb.jpg')
    down.main()'''