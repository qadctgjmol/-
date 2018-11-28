# ！/usr/bin/env python3
# -*- coding: utf-8 -*-


'''
正则化模块
'''

import re


# 顿号字符切割


def split_text(text):
    split_text = re.split('、', text)

    return split_text


# 当事人


def get_Prosecutor(text):
    pattern = re.compile("公诉机关(.+?)。")
    Prosecutor = pattern.findall(text)
    return Prosecutor


def get_province(text):
    pattern = re.compile('北京市|天津市|上海市|重庆市|河北省|山西省|辽宁省|吉林省|'
                         '黑龙江省|江苏省|浙江省|安徽省|福建省|江西省|山东省|河南省|'
                         '湖北省|湖南省|广东省|海南省|四川省|贵州省|云南省|陕西省|'
                         '甘肃省|青海省|台湾省|内蒙古自治区|广西壮族自治区|西藏自治区|'
                         '宁夏回族自治区|新疆维吾尔自治区|香港特别行政区|澳门特别行政区')
    province = pattern.findall(text)
    return province


def get_reasons(text):
    pattern = re.compile('^为了感谢[\u4e00-\u9fa5"“”（）’‘]+(?=[,，。、；;])|'
                         '帮助[\u4e00-\u9fa5"“”（）’‘]+[,，。、；;]|'
                         '以[\u4e00-\u9fa5"“”（）’‘]+为[\u4e00-\u9fa5]+(?=[,，。、；;])|'
                         '为[\u4e00-\u9fa5"“”（）’‘]+(?=[,，。、；;])|'
                         '(?<=[,，。、；;])[\u4e00-\u9fa5"“”（）’‘]+提供帮助|'
                         '[\u4e00-\u9fa5"“”（）’‘]+提供帮助|'
                         '[\u4e00-\u9fa5"“”（）’‘]+给予帮助|'
                         '[\u4e00-\u9fa5"“”（）’‘]+关照|'
                         '[\u4e00-\u9fa5"“”（）’‘]+提供[\u4e00-\u9fa5"“”（）’‘]+帮助|'
                         '[\u4e00-\u9fa5"“”（）’‘]+给予[\u4e00-\u9fa5"“”（）’‘]+帮助')
    reasons = pattern.findall(text)
    return reasons


def get_accused_person(text):
    accused = re.search('被告人|上诉人|上诉者|（上诉者）', text, re.M | re.I)
    if accused:

        pattern = re.compile('(?<=被告人|上诉人)[\u4e00-\u9fa5]某+|'
                             '(?<=被告人|上诉人)[\u4e00-\u9fa5]{2,3}、[\u4e00-\u9fa5]{2,3}、[\u4e00-\u9fa5]{2,3}、[\u4e00-\u9fa5]{2,3}|'
                             '(?<=被告人|上诉人)[\u4e00-\u9fa5]{2,3}、[\u4e00-\u9fa5]{2,3}、[\u4e00-\u9fa5]{2,3}|'
                             '(?<=被告人|上诉人)[\u4e00-\u9fa5]{2,3}、[\u4e00-\u9fa5]{2,3}|'
                             '(?<=被告人|上诉人)[\u4e00-\u9fa5]{2,3}')
        accused_person = pattern.findall(text)
        temp = []
        for person in accused_person:
            flag = re.match('[赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严'
                            '华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花'
                            '方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时'
                            '傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明'
                            '臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄'
                            '危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢'
                            '莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢'
                            '滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴'
                            '弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符'
                            '刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲台从鄂索咸籍赖卓蔺屠'
                            '蒙池乔阴胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍却璩桑桂'
                            '濮牛寿通边扈燕冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容'
                            '向古易慎戈廖庚终暨居衡步都耿满弘匡国文寇广禄阙东殴殳沃利'
                            '蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰'
                            '巢关蒯相查后荆红游竺权逯盖益覃]', person, re.M | re.I)
            if flag:
                if len(person) < 4:
                    ex = 0
                    for p in temp:
                        if p == person:
                            ex = 1
                            break
                    if ex == 0:
                        temp.append(person)
                else:
                    person = str(person).split('、')
                    for per in person:
                        ex = 0
                        for p in temp:
                            if p == per:
                                ex = 1
                                break
                        if ex == 0:
                            temp.append(per)
        accused_person = temp
    else:
        accused_person = []
    return accused_person


def get_briber(text, accused_names, name_list):
    my_name_list = ''
    for s in name_list:
        my_name_list = my_name_list + str(s) + '|'
    my_name_list = my_name_list[0:my_name_list.__len__() - 1]
    send = re.compile('((?<!退还|退出|返还)(?<!退还所|退出所|返还所|退还其|退出其|返还其))'
                      '(贿送|送给|赠送|给予|拿给|收受|接受|交给|获得|转交|赠予|交付|存入|给|索要|索取|索求|收|收取)')
    # send_word = send.findall(text)
    # # left = ['贿送', '送给', '赠送', '给予', '拿给', '交给', '转交', '赠予', '交付', '存入', '给']
    # right = ['收受', '接受', '获得', '索要', '索取', '索求','收','收取']
    if send:
        pattern = re.compile('[\u4e00-\u9fa5]某[甲乙丙丁一二三123*]|'
                             '[\u4e00-\u9fa5]某{1,2}|' + my_name_list)
        bribers = pattern.findall(text)
        if bribers == []:
            pattern = re.compile('[\u4e00-\u9fa5]{2,3}(?=为了感谢)')
            bribers = pattern.findall(text)
    else:
        bribers = []
    briber = []
    for name in bribers:
        if name not in accused_names and name not in briber:
            if name.__len__() == 3:
                if re.compile('[\u4e00-\u9fa5]{3}'):
                    briber.append(name)
            elif name.__len__() == 4:
                if re.compile('[\u4e00-\u9fa5]{4}'):
                    briber.append(name)
            elif name.__len__() == 2:
                if re.compile('[\u4e00-\u9fa5]{2}'):
                    briber.append(name)
    return briber


def get_gender(text):
    # pattern = re.compile('，男，|，男。|,男,|，女，|，女。|,女,')
    pattern = re.compile('[男女]')
    gender = pattern.findall(text)
    return gender


def get_born_date(text):
    pattern = re.compile('([\d]{4}年[\d]+月[\d]+日)出生')
    born_date = pattern.findall(text)
    return born_date


def get_birth_place(text):
    pattern = re.compile(r'，([\u4e00-\u9fa5]{2,20})人，|生[于地](.+?)，|住([\u4e00-\u9fa5]{2,20})。、')
    birth_place = pattern.findall(text)
    for (x, y, z) in birth_place:
        return x + y + z


def get_people(text):
    pattern = re.compile('，(汉族|蒙古族|回族|藏族|维吾尔族|苗族|彝族|壮族|布依族'
                         '|朝鲜族|满族|侗族|瑶族|白族|土家族|哈尼族|哈萨克族'
                         '|傣族|黎族|僳僳族|佤族|畲族|高山族|拉祜族|水族|东乡族'
                         '|纳西族|景颇族|柯尔克孜族|土族|达斡尔族|仫佬族|羌族'
                         '|布朗族|撒拉族|毛南族|仡佬族|锡伯族|阿昌族|普米族'
                         '|塔吉克族|怒族|乌孜别克族|俄罗斯族|鄂温克族|德昂族'
                         '|保安族|裕固族|京族|塔塔尔族|独龙族|鄂伦春族|赫哲族'
                         '|门巴族|珞巴族|基诺族)，')

    people = pattern.findall(text)
    return people


def get_edu_level(text):
    pattern = re.compile('，(博士|研究生文化|硕士|大学文化|本科文化|文化程度大学|文化程度本科|'
                         '大学本科|大专文化|文化程度大专|中专文化|文化程度中专|专科文化|'
                         '高中文化|文化程度高中|初中文化|文化程度初中|小学文化|文化程度小学|农民)，')
    edu_level = pattern.findall(text)
    return edu_level


def get_lawyer(text):
    # pattern = re.compile('辩护人.{1,4}，|辩护人.{1,4}、.{0,4}，|辩护人.{1,4}、.{0,4}、.{0,4}，')
    pattern = re.compile('辩护人(.+?)，')

    lawyer = pattern.findall(text)
    return lawyer


def get_law_firm(text):
    pattern = re.compile('[\u4e00-\u9fa5]{1,20}律师事务所|[\u4e00-\u9fa5]{1,20}援助中心律师')
    law_firm = pattern.findall(text)

    return law_firm


# 庭审程序说明


def get_Court_proceedings_time(text):
    pattern = re.compile('于(.+?)[作向以]')
    Court_proceedings_time = pattern.findall(text)
    return Court_proceedings_time


# 庭审过程
def get_date(text):
    # pattern = re.compile('\d{4}年\d{1,2}月至\d{4}年\d{1,2}月|\d{4}年\d{1,2}月|\d{4}年\d{1,2}、\d{1,2}月|\d{4}年')
    pattern = re.compile(
        '''
        [0-9零一二三四五六七八九元]{4}年[0-9零一二三四五六七八九元]{1,2}月、{0,1}[0-9零一二三四五六七八九元]{0,2}月{0,1}至[0-9零一二三四五六七八九元]{4}年[0-9零一二三四五六七八九元]{1,2}月、{0,1}[0-9零一二三四五六七八九元]{0,2}月{0,1}|
        [0-9零一二三四五六七八九元]{4}年、[0-9零一二三四五六七八九元]{4}年|
        [0-9零一二三四五六七八九元]{4}年至[0-9零一二三四五六七八九元]{4}年|
        [0-9零一二三四五六七八九元]{4}年、[0-9零一二三四五六七八九元]{4}年、[0-9零一二三四五六七八九元]{4}年|
        [0-9零一二三四五六七八九元]{4}年[0-9零一二三四五六七八九元]{1,2}月至[0-9零一二三四五六七八九元]{4}年[0-9零一二三四五六七八九元]{1,2}月|  # year-month
        [0-9零一二三四五六七八九元]{4}年[0-9零一二三四五六七八九元]{0,2}月{0,1}至[0-9零一二三四五六七八九元]{4}年[0-9零一二三四五六七八九元]{0,2}月{0,1}|                    # year
        [0-9零一二三四五六七八九元]{4}年[0-9零一二三四五六七八九元]{0,2}月{0,1}[0-9零一二三四五六七八九元]{0,2}[号日]{0,1}
    
        ''',
        re.VERBOSE)
    '''
    pattern = re.compile(
     ([0-9零一二三四五六七八九元]+年)?([0-9零一二三四五六七八九元]+月)?([0-9零一二三四五六七八九元]+[号日])?|
     ([0-9零一二三四五六七八九元]+年)?([0-9零一二三四五六七八九元]+月)?([0-9零一二三四五六七八九元]+[号日])?至
     ([0-9零一二三四五六七八九元]+年)?([0-9零一二三四五六七八九元]+月)?([0-9零一二三四五六七八九元]+[号日])?
    )
    '''
    result = pattern.findall(text)
    return result


def get_money_number(text):
    pattern = re.compile(
        '\d{1,20}.{0,1}\d{0,5}万{0,1}元(?![\u4e00-\u9fa5]{0,20}退还|[\u4e00-\u9fa5]{0,20}还给|[\u4e00-\u9fa5]{0,20}返还|[\u4e00-\u9fa5]{0,20}退给)')
    result = pattern.findall(text)
    return result


# 法院意见
#
# def get_court_opinion(text):
#     pattern = re.compile('述(.+？)。')
#
#     court_opinion = pattern.findall(text)
#     return court_opinion


# 判决结果
def get_judgment_result(text):
    pattern = re.compile('判决如下.+|裁定如下:.+|判处如下.+|判决:.+|'
                         '如下判决:.+|判决书如下:.+|判决意见如下:.+|决定如下:.+')

    judgment_result = pattern.findall(text)

    return judgment_result


def get_legal_basis(text):
    pattern = re.compile(r'依照(.+?)[之的]规定')

    legal_basis = pattern.findall(text)

    return legal_basis


def get_is_surrendere(text):
    pattern = re.compile('认定自首|处理自首')

    legal_basis = pattern.findall(text)

    return legal_basis


def get_accusation(text):
    pattern = re.compile('贪污罪|挪用公款罪|受贿罪|单位受贿罪|行贿罪|对单位行贿罪|介绍贿赂罪|单位行贿罪|巨额财产来源不明罪|隐瞒境外存款罪|私分国有资产罪|私分罚没财物罪')
    accusation = pattern.findall(text)
    return accusation


def get_court_opinion(text):
    pattern = re.compile('原判决{0,1}(.+?)。')
    court_opinion = pattern.findall(text)
    return court_opinion


def exit(text):
    pattern = re.compile('触犯')
    exit = pattern.findall(text)
    return exit


if __name__ == '__main__':
    print('This is regex fuctions for openlaw!')

