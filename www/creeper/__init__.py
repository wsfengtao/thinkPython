#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import logging
import pymongo
import threading
from bs4 import BeautifulSoup
from ..config import app_config
from ..models import *

__author__ = 'Geek_Feng'

logging.getLogger("requests").setLevel(logging.WARNING)

# Mongodb 客户端
db = pymongo.MongoClient(**app_config.db.db_settings)


def start_creeper(city, cycle_type):
    """开始爬虫
    :param city: 城市
    :param cycle_type: 车型
    """
    _url = "http://www.jiakaobaodian.com/tiku/%s-%s.html" % (cycle_type, city)
    html = requests.get(_url)
    bsobj = BeautifulSoup(html.text, "html.parser")
    thread_pool = []
    try:
        ul_id = 1
        pc_id = 1
        ul_list = bsobj.find("div", {'class': {'jkbd-main-main'}}).find("div", {'class': "chapter-list"}).findAll("ul")
        for ul in ul_list:
            li_id = 1
            li_list = ul.findAll("li")
            for li in li_list:
                kemu = 4 if ul_id == 2 else ul_id
                _url = "http://www.jiakaobaodian.com" + li.a.attrs['href']
                t = threading.Thread(target=_multi_creeper_jktm, args=(_url, city, kemu, cycle_type, li_id, pc_id))
                thread_pool.append(t)
                pc_id += 1
                li_id += 1
            ul_id += 1
        for thread in thread_pool:
            thread.start()
        logging.info("所有爬虫已经启动!共有%s只小爬虫正在努力爬取中......" % str(len(thread_pool)))
        for thread in thread_pool:
            thread.join()
        logging.info("所有的小爬虫都已经完成了它们的任务!")
    except Exception as e:
        logging.exception('获取%s城市%s车型信息失败' % (city, cycle_type) + str(e))
        return False
    end = time.time()


def _multi_creeper_jktm(url, city, kemu, cycle_type, zhangjie, pc_id):
    qid = 1
    html = requests.get(url)
    bsobj = BeautifulSoup(html.text, "html.parser")
    res = bsobj.find('div', {'class': {'jkbd-main-main'}}).find('div', {'class': 'paging-inner'}).findAll('a')
    if res[len(res) - 1].text == '下一页':
        allpage = int(res[len(res) - 2].text)
    else:
        allpage = int(res[len(res) - 1].text)
    for page in range(1, allpage + 1):
        qid = _creeper_jktm(url=url, page=page, city=city, kemu=kemu, qid=qid, cycle_type=cycle_type, zhangjie=zhangjie)
    logging.info("%s号小爬虫已经顺利完成任务!" % str(pc_id))


def _creeper_jktm(url, page, city, kemu, qid, cycle_type, zhangjie):
    html = requests.get(url + '?page=' + str(page))
    bsobj = BeautifulSoup(html.text, "html.parser")
    # 获取题目列表
    try:
        questions = bsobj.findAll("li", {"class": {"ques-li", "clearfix", "jkbd-border"}})
    except Exception as e:
        logging.exception('获取第%s页,城市%s,科目%s出现异常' % (str(page), city, str(kemu)) + str(e))
        return qid
    for question in questions:
        error_str = "题号: %s,页数: %s,城市: %s,科目: %s,章节: %s" % (str(qid), str(page), city, str(kemu), str(zhangjie))
        qid += 1
        # 获取题目类型
        try:
            is_single_selection = question.a.div.h4.b.text
        except Exception as e:
            logging.exception('获取题目类型时出现异常: ' + error_str + str(e))
            continue
        try:
            img_src = None
            mp4_src = None
            is_pic_or_mp4 = question.a.find("div", {"class": {"media-wapper"}})
            try:
                img = is_pic_or_mp4.find("img")
                img_src = img.attrs['src']
            except Exception:
                pass
            try:
                mp4 = is_pic_or_mp4.find("video")
                mp4_src = mp4.attrs['src']
            except Exception:
                pass
        except Exception as e:
            logging.exception('获取题目是否存在图片或者mp4时出现异常: ' + error_str + str(e))
            continue
        # 单选题
        if is_single_selection == "单" or is_single_selection == "判" or is_single_selection == "多":
            # 获取题目内容
            try:
                title = question.a.div.h4.text[2:]
            except Exception as e:
                logging.exception("获取题目内容时出现异常: " + error_str + str(e))
                continue
            # 获取答案组
            if is_single_selection == "单" or is_single_selection == "多":
                try:
                    answers = question.a.div.findAll("p")
                except Exception as e:
                    logging.exception("获取答案时出现异常: " + error_str + str(e))
                    continue
            # 获取正确答案
            try:
                if is_single_selection == "多":
                    right_answer = question.a.div.find("div", {"class": {"answer"}}).text
                    right_answer = right_answer[6:(len(right_answer) - 5)]
                else:
                    right_answer = question.a.div.find("div", {"class": {"answer"}}).text[6:7]
            except Exception as e:
                logging.exception("获取正确答案时出现异常: " + error_str + str(e))
                continue
            # 接下来爬取答案分析
            try:
                html2 = requests.get(question.a.attrs['href'])
                bsobj2 = BeautifulSoup(html2.text, "html.parser")
                try:
                    parse_answer = bsobj2.find("div", {"class": {"ef-content"}})
                    try:
                        reason = parse_answer.find("p", {"class": {"wapper"}}).text
                        if reason == '':
                            try:
                                reason = parse_answer.findAll("p")[2].text
                            except Exception:
                                reason = ""
                        if is_single_selection == "单" or is_single_selection == "多":
                            answer = {"A": answers[0].text[2:], "B": answers[1].text[2:],
                                      "C": answers[2].text[2:], "D": answers[3].text[2:]}
                        else:
                            answer = ''
                        timu = {"city": city, "title": title, "cycle_type": cycle_type, "kemu_type": kemu,
                                "zhangjie": zhangjie, "tihao": qid - 1, "is_single_selection": is_single_selection,
                                "answers": answer, "img_src": img_src, "mp4_src": mp4_src, "right_answer": right_answer,
                                "reason": reason}
                        drv = DrivingTestSubject(**timu)
                        res = drv.insert_one(db=db)
                        if res:
                            # 如果插入成功
                            continue
                        else:
                            logging.exception("存入数据库失败: " + error_str)
                            continue
                    except Exception as e:
                        logging.exception("获取解析时出现异常: " + error_str + str(e))
                        continue
                except Exception as e:
                    logging.exception("获取答案解析网页时出现异常: " + error_str + str(e))
                    continue
            except Exception as e:
                logging.exception("获取答案解析链接时出现异常: " + error_str + str(e))
                continue
        else:
            logging.exception("未识别的题型" + error_str)
            continue
    return qid
