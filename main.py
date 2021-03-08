import sys
import argparse
from question_generator import QuestionGenerator
import os
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.lancaster import LancasterStemmer
from nltk.tag import pos_tag
import spacy
import random
from word2number import w2n
# from spacy.language import EntityRecognizer

# f=open("output1.txt",'w')
# sys.stdout=f

def add_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str,
                        help="The file with the text.")
    # parser.add_argument('-t', '--question_type', type=str, default=['Wh', 'Are', 'Who', 'Do'], choices=['Wh', 'Are', 'Who', 'Do', 'All'], help='The types of questions to be generated.')
    return parser.parse_args()


def printQuestions(question_list):
    for i, q in enumerate(question_list):
        # +"\tScore: "+str(round(float(q['score']),2)))
        print("Q"+str(i+1)+": "+q['Q'])
        print("A: "+q['A']+"\n")

def print_q_with_options(question_list):
    for i, q in enumerate(question_list):
        if(len(q["options"])==1):
            continue
        # +"\tScore: "+str(round(float(q['score']),2)))
        print("Q"+str(i+1)+": "+q['Q'])
        for j,opt in enumerate(q["options"]):
            print(str(j+1)+": "+opt)
        print("Ans: "+q['A']+"\n")

def ner(text,nlp,ps):
    doc=nlp(text)
    categories={}
    for ent in doc.ents:
        # print(ent.text, ent.start_char, ent.end_char, ent.label_)
        if(len(str(ent.text).split())>4):
            continue
        if(ent.label_ in categories):
            categories[ent.label_].add(ent.text)
        else:
            categories[ent.label_]={ent.text}
    # print(categories)
    return categories

def isValidOptionSet(distractor,ans):
    optionsCpy=distractor.copy()
    optionsCpy.append(ans)
    for i,op1 in enumerate(optionsCpy):
        for j,op2 in enumerate(optionsCpy):
            if(i!=j):
                op1=str(op1).lower()
                op2=str(op2).lower()
                if(op1==op2):
                    return False
                if(len(op1.split())==1 and len(op2.split())==1):
                    if(op1[:-1]==op2 or op1==op2[:-1]):
                        return False
    return True

def generate_options(question_list,categories,nlp):
    # discardedQuestions=[]
    questions_with_options=[]
    for q in question_list:
        doc=nlp(q['A'])

        if(len(doc.ents)==0):
            continue
        
        label=doc.ents[0].label_
        rep_word=doc.ents[0].text
        
        if(label not in categories or len(categories[label])<4):
            continue

        posReplacements=set([key for key in categories[label] if (key not in q['Q'] and key != rep_word)])

        # possible_options=set([q['A'].replace(rep_word,key) for key in categories[label] if (key not in q['Q'] and key != rep_word)])
        
        # options=random.sample(possible_options,3)
        distractors=random.sample(posReplacements,3)
        # print(distractors)
        tries=0
        while(not isValidOptionSet(distractors,rep_word)):
            tries=tries+1
            # print(distractors)
            distractors=random.sample(posReplacements,3)
            if(tries>=5):
                break

        if(tries>=5):
            continue

        options=[q['A'].replace(rep_word,key) for key in distractors]
        
        options.append(q['A'])

        random.shuffle(options)

        # print(options)

        question={'Q': q['Q'],'A':q['A'],'score': q['score'],'options':options}
        questions_with_options.append(question)
    # printQuestions(discardedQuestions)
    return questions_with_options


def cleanQuestions(question_list):
    cleanQs = []
    for q in question_list:
        found = False
        if(float(q["score"])<1.5):
            continue
        if(len(q['A'].split()) > 5):
            found = True
        words = word_tokenize(q['Q'])
        for w in words:
            if(pos_tag([w])[0][1]) == 'PRP':
                found = True
        if(not found):
            cleanQs.append(q)

    return cleanQs


def test(nlp):
    doc=nlp("The earth is a round planet. It does not have a flat surface. It revolves around the sun. Moon revolves around the Earth")
    # print(str(int("100%"[:-1])))
    for ent in doc.ents:
        print(pos_tag(["it's"]))
        print(ent.text, ent.start_char, ent.end_char, ent.label_)


if __name__ == '__main__':
    args = add_arguments()
    if not args.file:
        sys.stdout.write('No input given\n')
        sys.exit()
    q = QuestionGenerator()
    readFile = open(
        "/home/shrinivas/KGP/DHYAN/question-generation/"+args.file, 'r',encoding="utf-8")
    # readFile = open(r"./{}".format(args.file), 'r')
    text = readFile.read()
    # print(text)
    question_list = q.generate_question(text)
    print(len(question_list))
    question_list = cleanQuestions(question_list)
    print(len(question_list))
    nlp=spacy.load('en_core_web_sm')
    # print(get_noun_list(text))
    # print(pos_tag(["9"]))
    ps=LancasterStemmer()
    categories=ner(text,nlp,ps)
    # for cat in categories:
    #     print(cat)
    # print(ner(text,nlp))
    # print(EntityRecognizer())

    # test()

    # print(categories)
    # for category,words in categories.items():
    #     print(category)
    #     print(words)
    q_with_options=generate_options(question_list,categories,nlp)
    print(len(q_with_options))
    # print_q_with_options(q_with_options)

    # test(nlp)
