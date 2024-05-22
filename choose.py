import requests
import re
import time
import json
import base64

class test:
    def __init__(self):
        self.lessonlist = []
        with open('test.txt', 'r', encoding='utf-8') as f:
            data = f.readlines()
            print(data, type(data))
            for Data in data:
                self.lessonlist.append(Data.strip('\n').split(','))
            print(data)
            print(self.lessonlist[0])

        for lesson in self.lessonlist:
            print(int(lesson[0]), int(lesson[1]))


if __name__ == '__main__':
    test = test()


