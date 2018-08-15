words = []
counts = []
for line in open('词频统计(去停用词).txt',encoding='utf-8'):
        line.strip('\n')
        # print(len(line.split()))
        if len(line.split()) > 1:
                print(line.split(' ')[0])
                print(int(line.split(' ')[1].strip('\n')))