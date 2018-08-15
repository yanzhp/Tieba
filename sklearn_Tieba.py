#coding=utf-8
from sklearn.cross_validation import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
# from BaseUltils import loadData  #自己写的一个工具包，用来加载文件地址

# 随机抽取80%的数据作为训练集，20%的数据作为测试集
def get_train_test_data():
    file_site = 'merge.txt'
    f = open(file_site, encoding='UTF-8')
    data_X = []
    data_y = []
    for line in f:
        row = line.strip('\n').split('\t')
        if len(row) < 2:
            continue
        feature = ' '.join(row[0].split(','))
        data_X.append(feature)
        data_y.append(row[1])
    f.close()
    # 80%作为训练集，20%作为测试集
    X_train, X_test, y_train, y_test = train_test_split(data_X, data_y, test_size=0.2)
    return X_train, X_test, y_train, y_test

# 训练并测试模型-NB
def train_model_NB():
    X_train, X_test, y_train, y_test = get_train_test_data()
    tv = TfidfVectorizer()
    train_data = tv.fit_transform(X_train)
    test_data = tv.transform(X_test)

    clf = MultinomialNB(alpha=0.01)
    clf.fit(train_data, y_train)
    # y_predict = clf.predict(test_data)
    print(clf.score(test_data, y_test))

# 训练并测试模型-logisticRegression
def train_model_LR():
    X_train, X_test, y_train, y_test = get_train_test_data()
    tv = TfidfVectorizer()
    train_data = tv.fit_transform(X_train)
    test_data = tv.transform(X_test)

    lr = LogisticRegression(C=1000)
    lr.fit(train_data, y_train)
    print(lr.score(test_data, y_test))

# 训练并测试模型-svm
def train_model_SVM():
    X_train, X_test, y_train, y_test = get_train_test_data()
    tv = TfidfVectorizer()
    train_data = tv.fit_transform(X_train)
    test_data = tv.transform(X_test)

    clf = SVC(C=1000.0)
    clf.fit(train_data, y_train)
    print(clf.score(test_data, y_test))
if __name__=="__main__":
    train_model_NB()
    train_model_LR()
    train_model_SVM()