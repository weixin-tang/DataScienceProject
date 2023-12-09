


import sys
import re
import json
import math
import numpy as np
import time
import getopt

def loadTransactions(  filePath  ):
    file = open( filePath , "r")
    content = file.read()
    contentArr = content.split("\n")
    myArr = []
    for data in contentArr:
        data = re.sub(r"^\s+|\s+$", "", data)
        if (len(data) != 0):
            dataArr = re.sub(r"^T\d{2}\s+", "", data)
            myArr.append( json.loads(dataArr ) )
    return myArr
def loadMeanings( filePath ):
    file = open( filePath , "r" )
    content = file.read()
    contentArr = content.split("\n")
    metaDict = dict()
    for data in contentArr:
        data = re.sub(r"^\s+|\s+$", "", data)
        if( len(data ) != 0 ):
              dataArr = data.split(" ")
              index = int( dataArr[0] )
              metaDict[ index ] = dataArr[1]
    return metaDict

def transforDataSet( myTransactionData ):
    def fun(x):
        x.sort()
        return frozenset(x)
    return list( map( fun , myTransactionData ) )

def getBaseItemSet(  myDataSet  ):
    itemSet = set()
    for i in myDataSet :
        itemSet = itemSet.union( i)
    itemSet = list( itemSet )
    itemSet.sort()
    baseItemList = list(itemSet)
    baseItemSet  = list( map( lambda x: frozenset([x]) , itemSet ) )
    return  baseItemList , baseItemSet


def combinations( myArr ,  size ):
    myPool = tuple( myArr )
    myArrLen = len( myPool)
    if size > myArrLen:
        return
    indices = list(range(size))
    yield tuple(myPool[i] for i in indices)
    while True:
        for i in reversed(range(size)):
            if indices[i] != i + myArrLen - size:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, size):
            indices[j] = indices[j-1] + 1
        yield tuple( myPool[i] for i in indices )

def scanMyDataSet( myDataSet , candidateArraySet , minSupportRate ):
    rawDict = dict()
    for myArr in candidateArraySet :
        rawDict[ myArr ] = 0
        for myData in myDataSet:
            if myArr.issubset( myData ) :
                rawDict[ myArr ]  += 1
    myDataSetSize = len( myDataSet )
    supportDict = dict()
    for myArr in rawDict.keys():
        support = rawDict[ myArr ]
        supportRate = support / myDataSetSize
        if( supportRate >= minSupportRate  ):
            supportDict[  myArr ] = support
    return supportDict

def getRules(  supportDictArr ,  minConfidenceRate ):
    ruleArr = []
    myLen = len(supportDictArr.keys())
    for arrIndex in range(2, myLen + 1):
        supportDict = supportDictArr[arrIndex]
        for myKey in supportDict.keys():
            supportNum = supportDict[myKey]
            myKeyLen   = len(myKey)
            for size in range(1, myKeyLen):
                combArr = list(combinations(myKey, size))
                for leftSide in combArr:
                    # comb this will be left side point to rest will be right side
                    rightSide      = myKey.difference(set(leftSide))
                    leftNum        = supportDictArr[size][frozenset(leftSide)]
                    confidenceRate = supportNum / leftNum
                    if (confidenceRate >= minConfidenceRate):
                        ruleArr.append( [ leftSide, rightSide, supportNum, leftNum ] )
    return ruleArr

def getMaxLen(arrSet):
    maxNum = 0
    for arr in arrSet:
        if (maxNum < len(arr)):
            maxNum = len(arr)
    return maxNum

def printRules(  myDataSetSize , rules  ):
    for rule in rules:
        print( "{} -> {} \t support rate: {:.2f} confidence rate : {:.2f}".format( list(rule[0]) , list(rule[1])  , rule[2]/myDataSetSize , rule[2]/rule[3] ) )

def printRulesWithMeanings(  rules , myDataSetSize   , myMetaData  ):
    for rule in rules:
        leftArr  = list( map( lambda x :  myMetaData[x] , list(rule[0]) ) )
        rightArr = list( map( lambda x :  myMetaData[x] , list(rule[1]) ) )
        print( "{} -> {} \t support rate: {:.2f} confidence rate : {:.2f}".format( leftArr , rightArr  , rule[2]/myDataSetSize , rule[2]/rule[3] ) )


def printSupport(  supportDictArr  ):
    for supportDictKey in supportDictArr.keys() :
        supportDict = supportDictArr[supportDictKey]
        for supportKey in supportDict.keys():
            print( "{} {}".format(  list(supportKey) , supportDict[supportKey] ) )

def brutalForceSupport( myDataSet , minSupportRate ):
    maxlen                      =  getMaxLen( arrSet = myDataSet )
    baseItemList , baseItemSet  =  getBaseItemSet(  myDataSet = myDataSet  )
    size = 1
    supportDictArr = dict()
    while( size <= maxlen ):
         candidateArraySet  =  list( map( lambda x: frozenset(x) , list( combinations( baseItemList , size ) ) ) )
         supportDict        =  scanMyDataSet( myDataSet , candidateArraySet , minSupportRate )
         myLen              =  len( supportDict.keys() )
         if( myLen == 0 ):
            break
         supportDictArr[ size ] = supportDict
         size = size + 1
    return supportDictArr

def myBrutalForce(  myDataSet , myMetaData ,  minSupportRate , minConfidenceRate ):
    supportDictArr = brutalForceSupport( myDataSet = myDataSet , minSupportRate = minSupportRate )
    print( "_____ itemsets above minimum support rate _____" )
    printSupport(  supportDictArr  )
    rules = getRules(  supportDictArr = supportDictArr  ,  minConfidenceRate = minConfidenceRate )
    #print( "_____ raw rules _____" )
    #printRules(  myDataSetSize = len(myDataSet) , rules = rules )
    print( "_____ rules with meaning _____" )
    printRulesWithMeanings(  rules = rules , myDataSetSize = len(myDataSet)  , myMetaData = myMetaData )

def getInput(  inputText , defaultValue  ):
    value = re.sub(r"^\s+|\s+$", "",  input( inputText ) )
    if (len(value) == 0 ):
        return defaultValue
    return value

def myFileInput():
    transactionFilePath = getInput(
        inputText="please enter the transaction file path(default 1.txt): ",
        defaultValue="1.txt")
    try:
        myTransactionData = loadTransactions(transactionFilePath)
        myDataSet = transforDataSet(myTransactionData)
        print("The transaction file path is {}".format(transactionFilePath))
    except:
        sys.exit()
    metaDataFilePath = getInput(
        inputText="please enter the meta data file path(default metaData.txt): ",
        defaultValue="metaData.txt")
    try:
        myMetaData = loadMeanings(metaDataFilePath)
        print("The meta data file path is {}".format(metaDataFilePath))
    except:
        sys.exit()

    minSupportRate = input("please enter the minimum support rate (eg. 0.15) :")
    try:
        minSupportRate = float(minSupportRate)
    except:
        sys.exit()
    minConfidenceRate = input("please enter the minimum confidence rate (eg. 0.5) :")
    try:
        minConfidenceRate = float(minConfidenceRate)
    except:
        sys.exit()

    return myDataSet , myMetaData , minSupportRate , minConfidenceRate

def removeSpace(input):
    return re.sub(r"^\s+|\s+$", "", input)


def getInput():
    transactionDataPath = None
    metaDataPath = None
    minSupportRate = None
    minConfidenceRate = None

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            argv, "d:m:s:f",
            ["data=", "meta=", "support=", "confidence="]
        )

        for opt, arg in opts:
            if opt in ['-d', '--data']:
                transactionDataPath = removeSpace(arg)
            elif opt in ['-m', '--meta']:
                metaDataPath = removeSpace(arg)
            elif opt in ['-s', '--support']:
                minSupportRate = float(removeSpace(arg))
            elif opt in ['-f', '--confidence']:
                minConfidenceRate = float(removeSpace(arg))

    except:
        print("Error")
        sys.exit()

    if (transactionDataPath == None):
        print("Error")
        sys.exit()
    else:
        try:
            myTransactionData = loadTransactions(transactionDataPath)
            myDataSet = transforDataSet(myTransactionData)
            print("The transaction file path is {}".format(transactionDataPath))
        except:
            print("Error")
            sys.exit()

    if (metaDataPath == None):
        print("Error")
        sys.exit()
    else:
        try:
            myMetaData = loadMeanings(metaDataPath)
            print("The meta data file path is {}".format(metaDataPath))
        except:
            print("Error")
            sys.exit()

    if (minSupportRate == None):
        print("Error")
        sys.exit()
    if (minConfidenceRate == None):
        print("Error")
        sys.exit()

    return myDataSet , myMetaData , minSupportRate, minConfidenceRate


def main():
    myDataSet , myMetaData , minSupportRate , minConfidenceRate =  getInput() #myFileInput()
    start_time = time.time()
    myBrutalForce(myDataSet=myDataSet, myMetaData=myMetaData, minSupportRate= minSupportRate , minConfidenceRate= minConfidenceRate )
    print("--- run time %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()


# myBrutalForce(  myDataSet = myDataSet , myMetaData = myMetaData ,  minSupportRate = 0.14 , minConfidenceRate = 0.6 )










































