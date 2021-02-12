import os
import json
from pdf2words import document
import numpy as np
from sklearn.cluster import DBSCAN
import re
from operator import itemgetter
from collections import OrderedDict


class addr_scoring:
    def __init__(self):
        self.top_words = []
        self.clusters = []
        self.score = []
        self.flg = 0
        self.location = []
        self.position_x = 0
        self.position_y = 0

    def forming(self, obj):
        word_group = []

        d = document.Document()
        d.load(json_object=obj)
        wordpage = d._document['pages'][0]

        height = int(wordpage._height)
        width = int(wordpage._width)

        thresh_y = 0.008 * height

        half_h = height//2

        self.position_x = width//2
        self.position_y = half_h//2

        cnt = 0
        flag = 0

        #iterating through all words of 1st page
        for word in wordpage._words:
            x0 = word._x0
            x1 = word._x1
            y0 = word._y0
            y1 = word._y1

            # extracting words in top half of first page

            if(y1 <= half_h):

                if(flag > 1):

                    #visting minimum 2 words in a cluster

                    if(flag == 2):

                        diff1_x = word_group[1]._x0-word_group[0]._x1

                        diff1_y = word_group[1]._y1-word_group[0]._y1

                        #next line encountered at 2nd word

                        if(abs(diff1_y) > thresh_y):
                            val = word_group.pop()
                            self.clusters.append(word_group)
                            word_group = []
                            word_group.append(val)
                            word_group.append(word)

                            flag = 1

                    if(flag >= 2):

                        diff2_x = x0 - temp_x
                        diff2_y = y1 - temp_y1

                        #grouping words in particular cluster based on minimum difference

                        if(abs(diff2_y) <= thresh_y):
                            thresh_x = (((y1-y0) + (temp_y1-temp_y0))/2)*0.55
                            if(abs(diff1_x-diff2_x) <= thresh_x):
                                word_group.append(word)
                                diff1_x = diff2_x
                            elif(abs(diff1_x) > abs(diff2_x)):
                                val = word_group.pop()
                                self.clusters.append(word_group)
                                word_group = []
                                word_group.append(val)
                                word_group.append(word)
                                flag = 1
                            else:
                                self.clusters.append(word_group)
                                word_group = []
                                word_group.append(word)
                                flag = 0

                        #next line encountered at 3rd word

                        elif(abs(diff2_y) > thresh_y):
                            self.clusters.append(word_group)
                            word_group = []
                            word_group.append(word)
                            flag = 0
                else:
                    word_group.append(word)

                temp_x = x1
                temp_y1 = y1
                temp_y0 = y0
                self.top_words.append(word)

                flag += 1
        self.clusters.append(word_group)
        word_group = []

    def clean(self):
        new_clusters = []

        def splitbydelimeter(symbl, cluster, i):
            new_cluster = []
            if(len(cluster) > i+1):
                if(cluster[i]._text != symbl):
                    temp = cluster[:i]
                    if(temp != []):
                        new_cluster.append(temp)
                    temp = cluster[i:]
                    if(temp != []):
                        new_cluster.append(temp)
                else:
                    temp = cluster[:i]
                    if(temp != []):
                        new_cluster.append(temp)
                    temp = cluster[i+1:]
                    if(temp != []):
                        new_cluster.append(temp)
            else:
                if(cluster[i]._text != symbl):
                    temp = cluster[:i+1]
                    if(temp != []):
                        new_cluster.append(temp)
                else:
                    temp = cluster[:i]
                    if(temp != []):
                        new_cluster.append(temp)

            return new_cluster

        for cluster in self.clusters:
            temp = []
            flag = 0
            for i in range(len(cluster)):

                # removing words with special characters ' ; * ' and

                if(re.search('[;*]', cluster[i]._text) is not None):
                    temp = []
                    flag = 1
                    break

                # remove clusters with only numbers and some special characters of length > 6

                elif(re.search('^[^A-Za-z:&-\/]+$', cluster[i]._text) is not None):
                    if(len(cluster[i]._text) > 6):
                        temp = []
                        flag = 1
                        break

                # dealing with words having ' : '
                # every thing before colon in one cluster
                # every thing before colon in another cluster

                elif(':' in cluster[i]._text):
                    new_clusters += splitbydelimeter(':', cluster, i)
                    flag = 1
                    break

                # cluster remains as it is

                else:
                    temp.append(cluster[i])

            if(flag == 0):
                if(temp != []):
                    new_clusters.append(temp)

        self.clusters = new_clusters

    def read(self, path):
        with open(path, 'r') as f:
            l = f.readlines()

        l = [x.strip('\n') for x in l]
        return l

    def scoring(self):
        cluster_size = []
        for cluster in self.clusters:
            scr = 0

            cities = self.read('pdf2words/scoring_data/cities.txt')

            first_names = self.read('pdf2words/scoring_data/first_names.txt')

            last_names = self.read('pdf2words/scoring_data/last_names.txt')

            words = ''.join([x._text for x in cluster])
            l = [x._text.upper() for x in cluster]

            # checking for cluster length

            if(len(cluster) >= 3):
                scr += 3

            # position based scoring

            x_measure = 0
            y_measure = 0
            length = len(cluster)
            for i in range(len(cluster)):
                y_measure = y_measure+(cluster[i]._y0+cluster[i]._y1)//2
                if(i == 0):
                    x_measure += cluster[i]._x0
                elif(i == length-1):
                    x_measure += cluster[i]._x1
                    x_measure = x_measure//2
            y_measure = y_measure//length

            self.location.append(y_measure)

            #print(x_measure,y_measure,self.position_x,self.position_y,cluster[0]._text)

            if(self.position_x >= x_measure and self.position_y >= y_measure):
                scr += 2
            elif(self.position_x <= x_measure and self.position_y >= y_measure):
                scr += 2
            elif(self.position_x >= x_measure and self.position_y <= y_measure):
                scr += 2
            else:
                scr += 0

            # checking for cities

            flag = 0
            for i in cities:
                if(i.upper() in l):
                    flag = 1
                    break

            if(flag == 1):
                scr += 6

            # checking for firstnames

            flag = 0
            for i in first_names:
                if(i.upper() in l):
                    flag = 1
                    break

            if(flag == 1):
                scr -= 3

            # checking for lastnames

            flag = 0
            for i in last_names:
                if(i.upper() in l):
                    flag = 1
                    break

            if(flag == 1):
                scr -= 4

            # checking for commonly occuring bank words

            common = self.read('pdf2words/scoring_data/bank_terms.txt')
            flag = 0
            for i in common:
                if(len(i) >= 4 and i.upper() in l):
                    flag += 1
                else:
                    for x in l:
                        if(i.upper() == x):
                            flag += 1

            if(flag >= 1):
                scr -= (5*(flag))

            # checking for commonly occuring addr words

            common = self.read('pdf2words/scoring_data/addr_terms.txt')
            flag = 0
            for i in common:
                if(len(i) >= 4 and i.upper() in l):
                    flag += 1
                else:
                    for x in l:
                        if(i.upper() == x):
                            flag += 1
            if(flag >= 1):
                scr += (6*(flag))

            # checking for company suffix

            company = self.read('pdf2words/scoring_data/company_suffix.txt')

            flag = 0
            for i in company:
                if i.upper() in l:
                    flag += 1

            if(flag >= 1):
                scr -= 4

            # checking for numeric values

            for i in l:
                if(',' in i):
                    scr += 2
                    break
                if(re.search('[0-9/-]', i) is not None):
                    if(len(i) <= 6):
                        scr += 3
                    else:
                        scr += 2
                    break

                if(len(i) == 1):
                    scr += 5

            # checking clusters with only one word

            if(len(cluster) == 1):
                scr -= 3

            # checking for case sensitive

            if(words.isupper()):
                scr += 1

            # commonly occuring name prefix

            if(re.search('(MR\.|Mr\.|M\/S\.|Mrs\.|Miss.|Dr\.|messrs|Smt\.)', words) is not None):
                scr -= 4

            self.score.append(scr)

        # combining top 10 cluster to their address group

        index = np.argsort(np.asarray(self.score))
        index = index[::-1]
        index = [x for x in index if self.score[x] > 0][:10]

        # DBSCAN

        feature_vector = []
        for i in index:
            feature_vector.append(
                [self.clusters[i][0]._x0, self.clusters[i][0]._y0])

        db = DBSCAN(eps=30, min_samples=2,
                    metric='euclidean').fit(feature_vector)

        addr_cluster = {}

        for idx, i in enumerate(index):
            if(db.labels_[idx] != -1):
                if(db.labels_[idx] not in addr_cluster.keys()):
                    addr_cluster[db.labels_[idx]] = [self.clusters[i]]
                else:
                    addr_cluster[db.labels_[idx]] += [self.clusters[i]]

        self.clusters = []

        # sort the addr groups to obtain address in sequence

        for i in addr_cluster:
            def func1(x):
                return x[0]._y0
            addr_cluster[i] = sorted(addr_cluster[i], key=func1)

        # sort the individual addr groups to find topmost addr

        def func2(x):
            x=x[1]
            return x[0][0]._y0
        addr_cluster=OrderedDict(sorted(addr_cluster.items(),key=func2))

        for idx, i in enumerate(addr_cluster):
            self.clusters.append([])
            for j in addr_cluster[i]:
                self.clusters[idx] += j

    def print_c(self, clusters):
        for cluster in clusters:
            for words in cluster:
                print(words._text+' ', end='')
            print()

    def get_bbox(self, cluster):
        #bbox=[x1,x2,x3,x4]
        bbox = [0, 0, 0, 0]

        bbox[1] = cluster[0]._y0
        bbox[3] = cluster[-1]._y1

        for i in cluster:
            if(i._x0 > bbox[0]):
                bbox[0] = i._x0
            if(i._x1 > bbox[2]):
                bbox[2] = i._x1

        return bbox

    def get_addr(self):
        addr_list=[]
        if(self.clusters!=[]):
            for cluster in self.clusters:
                addr=''  
                for i in cluster:
                    addr+=i._text+' '
                addr_list.append(addr)
        return addr_list

    def check_acc(self, json_path):
        # reverse sorting clusters based on score
        Z = [[scr, cluster] for scr, cluster in zip(self.score, self.clusters)]
        Z = list(reversed(sorted(Z, key=itemgetter(0))))
        clusters = [i[1] for i in Z[:3]]

        # printing clusters and corresponding score
        '''cnt = 0
        for cluster in clusters:
            for words in cluster:
                print(words._text+' ', end='')
            print(Z[cnt][0])
            cnt += 1'''

        # comparing with original data
        answers = self.read('pdf2words/name_score/original.txt')

        dict = {}
        for i in answers:
            temp = i.split(' ')
            dict[temp[0]] = ' '.join(temp[1:])

        for cluster in clusters[:1]:
            words = ''
            for word in cluster:
                words += word._text+' '

            if(dict[json_path.split('.')[0]] != 'None'):
                self.flg = 1
                # original name is a substring of found words
                if(dict[json_path.split('.')[0]].upper() in words.upper()):
                    self.flg = 2
                    break
                # 2 or more found words occur in original
                if(sum([1 if(word._text.upper() in dict[json_path.split('.')[0]].upper()) else 0 for word in cluster]) >= 2):
                    self.flg = 2
                    break
