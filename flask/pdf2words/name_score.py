import os
import json
from pdf2words import document
import re
from operator import itemgetter

class name_scoring:
    def __init__(self):
        self.top_words = []
        self.clusters = []
        self.score = []
        self.flg = 0
        self.position_x = 0
        self.position_y = 0

    def forming(self,obj):
        word_group = []

        d = document.Document()
        d.load(json_object=obj)
        wordpage = d._document['pages'][0]

        height = int(wordpage._height)
        width = int(wordpage._width)

        thresh_y = 0.009 * height

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
                        diff2_y = y1 - temp_y

                        #grouping words in particular cluster based on minimum difference

                        if(abs(diff2_y) <= thresh_y):
                            thresh_x= ((y1 + temp_y)/2)*0.3
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
                temp_y = y1
                self.top_words.append(word)

                flag += 1
        self.clusters.append(word_group)
        word_group = []

    def clean(self):
        new_clusters = []
        for cluster in self.clusters:
            temp = []
            flag = 0
            for i in range(len(cluster)):

                # 1.) removing all clusters with only one word

                if(len(cluster) == 1):
                    flag = 1
                    break

                # 1.) keep the cluster that have words with substrings (MR.|Mr.|M/S.|Mrs.)

                if(re.search('(MR.|Mr.|M/S.|Mrs.|Miss.)', cluster[i]._text) is not None):
                    temp = cluster
                    break

                # 1.) removing words with special characters ' / , ; - ' and
                
                elif(re.search('[\/;*,]', cluster[i]._text) is not None):
                    temp = []
                    flag = 1
                    break
                    
                # 1.) remove clusters with words consisting of only numbers of length <= 3
                # 2.) any word without alphabet (clusters having ' : & -' have been ignored)

                elif(re.search('^[^A-Za-z:&-]+$',cluster[i]._text) is not None):
                    if(len(cluster[i]._text)<=3):
                        temp = []
                        flag = 1
                        break
                    continue

                # 1.) dealing with words having ' : '
                #   -- removing every thing before colon from cluster
                #   -- keeping in cluster words that occur left of colon

                elif(':' in cluster[i]._text):
                    cluster[i]._text = cluster[i]._text.replace(':', '')
                    if(len(cluster) > i+1):
                        if(cluster[i]._text != ''):
                            temp = cluster[i:]
                            new_clusters.append(temp)
                        else:
                            temp = cluster[i+1:]
                            new_clusters.append(temp)
                    flag = 1
                    break
                else:
                    temp.append(cluster[i])
            if(flag == 0):
                if(temp!=[]):
                    new_clusters.append(temp)

        self.clusters = new_clusters

    def read(self, path):
        with open(path, 'r') as f:
            l = f.readlines()

        l = [x.strip('\n') for x in l]
        return l

    def scoring(self):
        for cluster in self.clusters:
            scr = 0

            cities = self.read('pdf2words/name_score/cities.txt')

            first_names = self.read('pdf2words/name_score/first_names.txt')

            last_names = self.read('pdf2words/name_score/last_names.txt')

            # checking for cluster length

            if(len(cluster) >= 3):
                scr += 3

            words = ''.join([x._text for x in cluster])
            l = [x._text.upper() for x in cluster]

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

            if(self.position_x >= x_measure and self.position_y >= y_measure):
                scr += 5
            elif(self.position_x <= x_measure and self.position_y >= y_measure):
                scr += 1
            elif(self.position_x >= x_measure and self.position_y <= y_measure):
                scr += 1
            else:
                scr += 0

            # checking for cities

            flag = 0
            for i in cities:
                if(i.upper() in l):
                    flag = 1
                    break

            if(flag == 1):
                scr -= 1

            # checking for firstnames

            flag = 0
            for i in first_names:
                if(i.upper() in l):
                    flag = 1
                    break

            if(flag == 1):
                scr += 2

            # checking for lastnames

            flag = 0
            for i in last_names:
                if(i.upper() in l):
                    flag = 1
                    break

            if(flag == 1):
                scr += 3

            # checking for commonly occuring words

            common=self.read('pdf2words/name_score/bank_addr_terms.txt')

            flag = 0
            for i in common:
                flag += sum([1 if i.upper() in x and len(i) >=
                             4 else 1 if i.upper() == x and len(i) < 4 else 0 for x in l])

            if(flag >= 1):
                scr -= (5*(flag))

            # checking for company suffix

            company=self.read('pdf2words/name_score/company_suffix.txt')

            flag = 0
            for i in company:
                if i.upper() in l:
                    flag += 1

            if(flag >= 1):
                scr += (1.5*(flag))

            # checking for numeric values

            if(re.search('[0-9]', words) is not None):
                scr -= 5

            # checking for case sensitive

            if(words.isupper()):
                scr += 1

            if(re.search('(MR.|Mr.|M/S.|Mrs.)', words) is not None):
                scr += 3

            self.score.append(scr)

    def print_c(self,clusters):
        for cluster in clusters:
            for words in cluster:
                print(words._text+' ', end='')
            print()

    def get_name(self):
        Z = [[scr, cluster] for scr, cluster in zip(self.score, self.clusters)]
        Z = list(reversed(sorted(Z, key=itemgetter(0))))
        clusters = [i[1] for i in Z[:1]]
        name=''
        for words in clusters[0]:
            name+=words._text+' '

        return name

    def check_acc(self,json_path):
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
                if(dict[json_path.split('.')[0]].upper() in words.upper()):
                    self.flg = 2
                    break
