# ！/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
---------------------
 author:zhang xiyu
---------------------
"""

import tensorflow as tf
import os, argparse, time
from utils import str2bool, get_logger, get_entity
from model import BiLSTM_CRF
from data import read_dictionary, tag2label, random_embedding
import numpy as np
import re

pos_name = "理事长|理事|总干事|总监|董事长|执行董事|总裁|总经理|经理|财务主管|公关部经理|营业部经理|销售部经理|推销员" \
         "|采购员|售货员|领班|经纪人|高级经济师|高级会计师|注册会计师|出纳员|审计署审计长|审计师|审计员|统计师|统计员" \
         "|厂长|车间主任|工段长|作业班长|仓库管理员|教授级高级工程师|高级工程师|技师|院长|庭长|审判长|审判员|法医" \
         "|法警|检察长|监狱长|律师|公证员|总警监|警监|警督|警司|警员|政治局常委|政治局委员|书记处书记|中央委员|候补委员" \
         "|党组书记|会长|主席|名誉顾问|乡镇长|秘书长|办公厅主任|部委办主任|处长副处长|科长股长|科员|发言人|顾问|参事|" \
         "巡视员|特派员|特命全权大使|公使|代办|临时代办|参赞|政务参赞|商务参赞|经济参赞|新闻文化参赞|公使衔参赞|商务专员" \
         "|经济专员|文化专员|商务代表|一等秘书|武官|档案秘书|专员|随员|总领事|领事|主任委员|委员|地方人大主任|人大代表" \
         "|国务院总理|国务委员|主任|部长助理|部长|司长|副局长|局长|副省长|省长|常务副省长|地区专员|行政长官|市长|副市长|区长|副县长|县长" \
         "|副委员长|委员长|副秘书长|全国人民代表大会|委员会主任委员|副主任委员|副主席|常务委员|副院长"\
         "|助理审判员|书记员|副检察长|检察委员会委员|检察员|助理检察员|副总理|总理|副部长|副主任|行长|副行长|审计长" \
         "|副审计长|署长|副署长|副会长|社长|副社长|组长|厅长|副厅长|副司长|处长|副处长|科长|副科长|主任科员" \
         "|副主任科员|助理巡视员|调研员|助理调研员|法定代表人|副经理|经理|副书记|书记|队长"\
         "|站长|负责人|副总经理|科长|业务员|行长|法定代表人|法人代表|理事长|审计|董事|总指挥|股东|老总|校长|企业法人|老板"\
         "|经营者|主任助理|保安|保洁主管|职工|销售员|接警员|秘书|法人|常务副主任|办公室主任|主管|教师|员工|教授|承包人" \
         "|办员|工作人员" \



class lstm_server():
    def __init__(self):
        self.model, self.saver,self.ckpt_file = self.get_model()
        self.config = tf.ConfigProto()
        self.sess = tf.Session(config=self.config)
        self.saver.restore(self.sess, self.ckpt_file)

    def sess_close(self):
        self.sess.close()

    def get_model(self):
        config = tf.ConfigProto()

        parser = argparse.ArgumentParser(description='BiLSTM-CRF for Chinese NER task')
        parser.add_argument('--train_data', type=str, default='data_path', help='train data source')
        parser.add_argument('--test_data', type=str, default='data_path', help='test data source')
        parser.add_argument('--batch_size', type=int, default=64, help='#sample of each minibatch')
        parser.add_argument('--epoch', type=int, default=40, help='#epoch of training')
        parser.add_argument('--hidden_dim', type=int, default=300, help='#dim of hidden state')
        parser.add_argument('--optimizer', type=str, default='Adam', help='Adam/Adadelta/Adagrad/RMSProp/Momentum/SGD')
        parser.add_argument('--CRF', type=str2bool, default=True,
                            help='use CRF at the top layer. if False, use Softmax')
        parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
        parser.add_argument('--clip', type=float, default=5.0, help='gradient clipping')
        parser.add_argument('--dropout', type=float, default=0.5, help='dropout keep_prob')
        parser.add_argument('--update_embedding', type=str2bool, default=True, help='update embedding during training')
        parser.add_argument('--pretrain_embedding', type=str, default='random',
                            help='use pretrained char embedding or init it randomly')
        parser.add_argument('--embedding_dim', type=int, default=300, help='random init char embedding_dim')
        parser.add_argument('--shuffle', type=str2bool, default=True, help='shuffle training data before each epoch')
        parser.add_argument('--mode', type=str, default='demo', help='train/test/demo')
        parser.add_argument('--demo_model', type=str, default='1521112368', help='model for test and demo')
        args = parser.parse_args()

        ## get char embeddings
        word2id = read_dictionary(os.path.join('.', args.train_data, 'word2id.pkl'))
        if args.pretrain_embedding == 'random':
            embeddings = random_embedding(word2id, args.embedding_dim)
        else:
            embedding_path = 'pretrain_embedding.npy'
            embeddings = np.array(np.load(embedding_path), dtype='float32')

        paths = {}
        timestamp = str(int(time.time())) if args.mode == 'train' else args.demo_model
        output_path = os.path.join('.', args.train_data + "_save", timestamp)
        if not os.path.exists(output_path): os.makedirs(output_path)
        summary_path = os.path.join(output_path, "summaries")
        paths['summary_path'] = summary_path
        if not os.path.exists(summary_path): os.makedirs(summary_path)
        model_path = os.path.join(output_path, "checkpoints/")
        if not os.path.exists(model_path): os.makedirs(model_path)
        ckpt_prefix = os.path.join(model_path, "model")
        paths['model_path'] = ckpt_prefix
        result_path = os.path.join(output_path, "results")
        paths['result_path'] = result_path
        if not os.path.exists(result_path): os.makedirs(result_path)
        log_path = os.path.join(result_path, "log.txt")
        paths['log_path'] = log_path
        get_logger(log_path).info(str(args))

        ckpt_file = tf.train.latest_checkpoint(model_path)
        print(ckpt_file)
        paths['model_path'] = ckpt_file
        model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
        model.build_graph()
        saver = tf.train.Saver()
        return model, saver, ckpt_file

    def get_name(self, text):
        demo_sent = text
        demo_sent = list(demo_sent.strip())
        demo_data = [(demo_sent, ['O'] * len(demo_sent))]
        tag = self.model.demo_one(self.sess, demo_data)
        per, pos, loc = get_entity(tag, demo_sent)
        return set(per)

    def get_org(self, text):
        demo_sent = text
        demo_sent = list(demo_sent.strip())
        demo_data = [(demo_sent, ['O'] * len(demo_sent))]
        tag = self.model.demo_one(self.sess, demo_data)
        per, pos, org = get_entity(tag, demo_sent)
        return set(org)

    def get_regex_lstm_name(self, regex_name, text):
        per = self.get_name(text)
        for index in range(0, len(regex_name)):
            # print(regex_name[index])
            for t_name in per:
                if len(regex_name[index]) > len(t_name) > 1 and t_name in regex_name[index]:
                    regex_name[index] = t_name
                    break
                elif len(regex_name[index]) <= len(t_name) and regex_name[index] in t_name:
                    regex_name[index] = t_name
                    break
        return regex_name

    def get_postion(self, text):
        org = self.get_org(text)
        organization = []
        # print("loc:{}".format(org))
        for pos_item in org:
            # print(pos_item)
            first = '{}{}(?:{}){}、{}(?:{}){}|'.format(pos_item, '[的]{0,1}[总正副大中小原]{0,1}', pos_name,"(?:助理|助手|秘书){0,1}", '[总正副大中小原]{0,1}', pos_name, "(?:助理|助手|秘书){0,1}")
            second = '{}{}(?:{}){}'.format(pos_item, '[的]{0,1}[总正副大中小原]{0,1}', pos_name, "(?:助理|助手|秘书){0,1}")
            pattern = re.compile(first + second)
            content = pattern.findall(text)
            # print("pos_name{}".format(content))
            for item in content:
                organization.append(item)
        # 给org按长度从小到大拍个序
        organization = list(set(organization))
        order_list = []
        for org_item in organization:
            order_list.append(len(org_item))
        sort_index = np.argsort(order_list)
        new_organization = []
        for index in sort_index[::-1]:
            new_organization.append(organization[index])
        return new_organization

    def match_per_postion(self, name_list,text):
        pos_list = self.get_postion(text)
        # print(text)
        # print(name_list)
        # print(pos_list)
        name_pos_lists = {}
        for name_temp in name_list:
            # print(name_temp)
            name_pos_list = []
            for pos_temp in pos_list:
                pattern = re.compile("{}[\u4e00-\u9fa5]*(?:担任|任)[\u4e00-\u9fa5]*{}|"
                                     "{}[\u4e00-\u9fa5]*(?:担任|任)[\u4e00-\u9fa5]*、[\u4e00-\u9fa5]*{}|"
                                     "{}[\u4e00-\u9fa5]*(?:担任|任)[\u4e00-\u9fa5]*、[\u4e00-\u9fa5]*、[\u4e00-\u9fa5]*{}"
                                     "".format(name_temp, pos_temp,name_temp, pos_temp,name_temp, pos_temp))
                name_pos = pattern.findall(text)
                if not name_pos:
                    pattern = re.compile("{}{}{}".format(pos_temp, "[的]{0,1}", name_temp))
                    name_pos = pattern.findall(text)
                if not name_pos:
                    pattern = re.compile("(?:{}){}{}".format(pos_name, "[的]{0,1}", name_temp))
                    name_pos = pattern.findall(text)
                if name_pos:
                    # 去除包含关系， 如'广州市方欣科技有限公司总裁助理' 包含'总裁助理'
                    add_mark = True
                    for item in name_pos_list:
                        if pos_temp in item[1]:
                            add_mark = False
                            break
                    if add_mark:
                        name_pos_list.append((name_temp, pos_temp))

            for item in name_pos_list:
                name_pos_lists[name_temp] = item[1]
            if not name_pos_list:
                name_pos_lists[name_temp] = ''
        return name_pos_lists  # 返回格式[(name, pos),(name, pos)]


if __name__ == '__main__':
    temp_str = '公诉机关广西壮族自治区天峨县人民检察院。、被告人陈毓焕，男。、因涉嫌贪污罪，于2013年3月25日被刑事拘留，同年4月8日被逮捕，同年6月21日天峨县人民检察院对其取保候审。、现住天峨县六排镇城东路275号。、辩护人班华进，男，天峨县法律援助中心律师。、被告人姚胜军，男。、因涉嫌贪污罪于2013年3月25日被刑事拘留，同年4月8日被逮捕，同年6月4日天峨县人民检察院对其取保候审。、现住天峨县政府大院。、被告人梁保成，男。、因涉嫌贪污罪于2013年3月29日被刑事拘留，同年4月8日被逮捕，同年5月3日天峨县人民检察院对其取保候审，现住大化县岩滩镇东杠村先下屯24号。、被告人曾运进，男。、因涉嫌贪污罪于2013年3月29日被刑事拘留，同月11日天峨县人民检察院对其取保候审。、现住天峨县更新乡更新街。'
    temp_str1 = '本院依法组成合议庭，公开开庭审理了本案。、广州市越秀区人民检察院指派检察员隆霞出庭支持公诉，被告人张某及其辩护人郑锋、蔡方华到庭参加诉讼。、现已审理终结。、广州市越秀区人民检察院指控，2003年至2013年间，被告人张某在担任广州市科技局高新技术及产业化处处长、广州市科技和信息化局高新技术及产业化处处长、广州市科技和信息化局软件和信息服务业处处长期间，利用其负责广州市高新技术科研项目申报、评比、验收，广州市科技与信息化扶持项目申请审批工作的职务便利，为他人谋取利益，多次收受了罗某某、倪某某、孟某某、明某、罗某某、曾某某、唐某某贿送的款项合计679788元并占为己有。、具体犯罪事实分述如下:一、2005年、2006年春节期间，被告人张某在中山大学教授罗某某（另案处理）申报数字家庭研发中心等相关科研项目过程中提供帮助，分两次共收受了罗某某贿送的20000元。、二、2007年、2008年春节期间，被告人张某在广州市赛百威电脑有限公司申报广州市相关科研项目过程中提供帮助，分两次共收受了广州市赛百威电脑有限公司总经理倪某某（另案处理）贿送的50000元。、三、2009年7月，被告人张某在中山大学教授孟某某申报科研项目以及组建“广州市纳米环境与能源材料工程研究中心”过程中提供帮助，收受孟某某贿送的钱款239788元，用于购买小轿车。、四、2010年底，被告人张某在广州日滨科技发展有限公司申报广州市相关科研项目过程中提供帮助，收受广州日滨科技发展有限公司企业发展部部长明某（另案处理）贿送的80000元。、五、2011年、2012年、2013年春节期间，被告人张某在广州市杰赛科技有限公司申报广州市重点软件企业以及享受相关税收奖励政策过程中提供帮助，分三次共收受了广州市杰赛科技有限公司总裁助理罗某某（另案处理）贿送的钱款共计40000元。、六、2012年初，被告人张某在曾某某即将辞职经营公司，且公司经营范围涉及其本人职权的情况下，分两次共收受了曾某某贿送的200000元。、七、2012年6月，被告人张某在广州市方欣科技有限公司申报广州市相关科研项目过程中提供帮助，收受广州市方欣科技有限公司总裁助理唐某某贿送的50000元。、2013年4月26日，被告人张某向广州市人民检察院投案自首。、公诉机关随案提供了相关的证据，认定被告人张某身为国家工作人员，利用职务便利，非法收受他人财物，为他人谋取利益，其行为触犯了《中华人民共和国刑法》第三百八十五条第一款之规定，构成受贿罪。、被告人张某犯罪后能自动投案，如实供述犯罪事实，是自首，根据《中华人民共和国刑法》第六十七条第一款之规定，可以从轻或者减轻处罚。、提请本院依法判处。、被告人张某对公诉机关指控的事实及罪名不持异议。、被告人张某的辩护人对公诉机关指控被告人张某构成受贿罪不持异议，辩称被告人张某是自首，全额退赃，初犯，犯罪情节较轻，请求法庭对其减轻处罚。；经审理查明，2005年至2013年间，被告人张某在担任广州市科学技术局高新技术及产业化处处长、广州市科技和信息化局高新技术及产业化处处长、广州市科技和信息化局软件和信息服务业处处长期间，利用其负责广州市高新技术科研项目申报、评比、验收，广州市科技与信息化扶持项目申请审批工作等的职务便利，为他人谋取利益，多次收受了向广州市科技和信息化局申报高新技术科研项目，并通过审批获得资金等各方面支持的罗某某、倪某某、孟某某、明某、罗某某、唐某某及曾某某贿送的贿款合计679788元。、具体事实分述如下:一、2005年、2006年春节期间，被告人张某在中山大学罗某某教授（另案处理）申报数字家庭研发中心等相关科研项目过程中提供帮助，分两次共收受罗某某贿送的20000元。、二、2007年、2008年春节期间，被告人张某在广州市赛百威电脑有限公司申报广州市相关科研项目过程中提供帮助，分两次共收受广州市赛百威电脑有限公司总经理倪某某（另案处理）贿送的50000元。、三、2009年7月，被告人张某在中山大学孟某某教授（另案处理）申报科研项目以及组建“广州市纳米环境与能源材料工程研究中心”过程中提供帮助，收受孟某某贿送的239788元，用于购买小轿车。、四、2010年底，被告人张某在广州日滨科技发展有限公司申报广州市相关科研项目过程中提供帮助，收受广州日滨科技发展有限公司企业发展部部长明某（另案处理）贿送的80000元。、五、2011年、2012年、2013年春节期间，被告人张某在广州市杰赛科技有限公司申报广州市重点软件企业以及享受相关税收奖励政策过程中提供帮助，分三次共收受了广州市杰赛科技有限公司总裁助理罗某某（另案处理）贿送的40000元。、六、2012年初，被告人张某在其单位属下员工曾某某即将辞职经营公司，且公司经营范围涉及其本人职权的情况下，分两次共收受了曾某某（另案处理）贿送的200000元。、七、2012年6月，被告人张某在广州市方欣科技有限公司申报广州市相关科研项目过程中提供帮助，收受广州市方欣科技有限公司总裁助理唐某某贿送的50000元。、2013年4月26日，被告人张某向广州市人民检察院投案自首，并先后退出全部赃款。、上述事实，被告人张某在开庭审理过程中亦无异议，且有孟某某作为项目负责人与广州市科学技术局签订的广州市科技计划项目任务书、，广州日滨科技发展有限公司与广州市科学技术局签订的广州市科技计划项目任务书、、广州日滨科技发展有限公司与广州市科技和信息化局签订的广州市软件和动漫产业发展资金项目任务书、，广州市方欣科技有限公司与广州市科学技术局签订的广州市科技计划项目任务书、，广州市杰赛科技股份有限公司与广州市科学技术局签订的广州市科技计划项目任务书、、广州市科技计划项目合同书、、广州市创新型企业专项资金任务书、，广州市赛百威电脑有限公司与广州市科学技术局签订的广州市科技计划项目任务书、，广州金睿企业管理顾问有限公司的企业注册基本资料，孟某某为被告人张某购车的刷卡银联单、账户明细及涉案汽车发票及相关资料，广州市特种证件制作中心出具的被告人张某的人口信息材料，广州市科技与信息化局出具的被告人张某的任免通知、国家公务员登记表、简历、干部履历表、职能说明，广州市人民检察院反贪污贿赂局出具的破案报告，广州市越秀区人民检察院出具的暂扣财物收据及本院代管款物收据，证人孟某某、倪某某、罗某某、明某、曾某某、唐某某、罗某某、刘某、杨某的证言，被告人张某的供述等证据证实，足以认定。；'
    temp_str2 ='广州市越秀区人民检察院指控，2003年至2013年间，被告人张某在担任广州市科技局高新技术及产业化处处长、广州市科技和信息化局高新技术及产业化处处长、广州市科技和信息化局软件和信息服务业处处长期间，利用其负责广州市高新技术科研项目申报、评比、验收，广州市科技与信息化扶持项目申请审批工作的职务便利，为他人谋取利益，多次收受了罗某某、倪某某、孟某某、明某、罗某某、曾某某、唐某某贿送的款项合计679788元并占为己有。'
    temp_str3 = '具体犯罪事实分述如下:一、2005年、2006年春节期间，被告人张某在中山大学教授罗某某（另案处理）申报数字家庭研发中心等相关科研项目过程中提供帮助，分两次共收受了罗某某贿送的20000元。、二、2007年、2008年春节期间，被告人张某在广州市赛百威电脑有限公司申报广州市相关科研项目过程中提供帮助，分两次共收受了广州市赛百威电脑有限公司总经理倪某某（另案处理）贿送的50000元。、三、2009年7月，被告人张某在中山大学教授孟某某申报科研项目以及组建“广州市纳米环境与能源材料工程研究中心”过程中提供帮助，收受孟某某贿送的钱款239788元，用于购买小轿车。、四、2010年底，被告人张某在广州日滨科技发展有限公司申报广州市相关科研项目过程中提供帮助，收受广州日滨科技发展有限公司企业发展部部长明某（另案处理）贿送的80000元。、五、2011年、2012年、2013年春节期间，被告人张某在广州市杰赛科技有限公司申报广州市重点软件企业以及享受相关税收奖励政策过程中提供帮助，分三次共收受了广州市杰赛科技有限公司总裁助理罗某某（另案处理）贿送的钱款共计40000元。、六、2012年初，被告人张某在曾某某即将辞职经营公司，且公司经营范围涉及其本人职权的情况下，分两次共收受了曾某某贿送的200000元。、七、2012年6月，被告人张某在广州市方欣科技有限公司申报广州市相关科研项目过程中提供帮助，收受广州市方欣科技有限公司总裁助理唐某某贿送的50000元。'
    # lstm_server initialize
    my_lstm_server = lstm_server()
    # 检测名字的抽取优化
    # name_set = ['陈毓', '班华', '姚胜', '小明', '梁保成']  # in fact, the name_set should be ['陈毓焕', '班华', '姚胜军', '梁保成']
    # print(my_lstm_server.get_regex_lstm_name(name_set, temp_str))

    # 检测职位名的抽取
    # print(my_lstm_server.get_postion(temp_str1))

    # 检测职位名与相应人名的匹配
    name_list = my_lstm_server.get_name(temp_str3)
    print(name_list)
    pos_list = my_lstm_server.get_postion(temp_str3)
    print(my_lstm_server. match_per_postion(name_list, temp_str3))
