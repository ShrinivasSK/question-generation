import sys
import argparse
from question_generator import QuestionGenerator
import os
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
import spacy
import random
from word2number import w2n
# from spacy.language import EntityRecognizer


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


def get_noun_list(text):
    sentences = sent_tokenize(text)
    nouns = []
    for sentence in sentences:
        for word, pos in pos_tag(word_tokenize(str(sentence))):
            if (pos == 'NNP' or pos == 'NNPS'):
                nouns.append(word)
    return nouns

def ner(text,nlp):
    doc=nlp(text)
    categories={}
    for ent in doc.ents:
        # print(ent.text, ent.start_char, ent.end_char, ent.label_)
        if(ent.label_ in categories):
            categories[ent.label_].add(ent.text)
        else:
            categories[ent.label_]={ent.text}
    # print(categories)
    return categories

def generate_options(question_list,categories,nlp):
    #If Present in Question don't put in option
    questions_with_options=[]
    # questions_with_options.extend(question_list)
    for i,q in enumerate(question_list):
        question={'Q': q['Q'],'A':q['A'],'score': q['score']}
        doc=nlp(q['A'])
        if(len(doc.ents)==0):
            # question["options"]=set([q['A']])
            continue
        label=doc.ents[0].label_
        rep_word=doc.ents[0].text
        options=set([q['A']])
        num_options=1
        if(label not in categories or len(categories[label])<4):
            continue
        # if(label in num_cat):
        #     words=word_tokenize(q['A'])
        #     tags=pos_tag(words)
        #     for word,tag in tags:
        #         if(tag=='CD'):
        #             try:
        #                 if(label=="PERCENT"):
        #                     number=int(word[:-1])
        #                 else:
        #                     number=int(word)
        #             except:
        #                 number=w2n.word_to_num(word)
        #             numWord=word
        #     if(label=="DATE"):
        #         while num_options<4:
        #             num=str((number+int(random.random()*number))%30)
        #             options.update([q['A'].replace(numWord,num)])
        #             num_options=len(options)
        #     elif(label=="PERCENT"):
        #         while num_options<4:
        #             num=str((number+int(random.random()*number))%100)
        #             options.update([q['A'].replace(numWord,num+"%")])
        #             num_options=len(options)
        #     elif(label=="TIME"):
        #         while num_options<4:
        #             num=str((number+int(random.random()*number))%24)
        #             options.update([q['A'].replace(numWord,num)])
        #             num_options=len(options)
        #     else:
        #         while num_options<4:
        #             num=str(int(number+int(random.random()*number)))
        #             options.update([q['A'].replace(numWord,num)])
        #             num_options=len(options)
            # print(questions_with_options[i])
            # options.update([q['A'].replace(rep_word,key) for key in categories[label] if (key not in q['Q'])])
            # # print(options)
            # num_options=len(options)

            # num_distractors=len(categories[label])

        options.update([q['A'].replace(rep_word,key) for key in categories[label] if (key not in q['Q'])])
            # if(num_options<4):
            #     for similar_label in similar_categories[label]:
            #         # print(similar_label)
            #         options.update([q['A'].replace(rep_word,key) for key in categories[similar_label] if (key not in q['Q'])])
            #         num_options=len(options)
            #         if(num_options>=4):
            #             break
        question["options"]=options
        questions_with_options.append(question)

    return questions_with_options


def cleanQuestions(question_list):
    cleanQs = []
    for q in question_list:
        found = False
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
        # print(pos_tag(["100%"]))
        print(ent.text, ent.start_char, ent.end_char, ent.label_)


if __name__ == '__main__':
    args = add_arguments()
    if not args.file:
        sys.stdout.write('No input given\n')
        sys.exit()
    q = QuestionGenerator()
    readFile = open(
        "/home/shrinivas/KGP/DHYAN/question-generation/"+args.file, 'r+')
    # readFile = open(r"./{}".format(args.file), 'r')
    sentence = readFile.read()
    # print(sentence)
    question_list = q.generate_question(sentence)
    # print(question_list)
    question_list = cleanQuestions(question_list)
    # printQuestions(question_list)
    nlp=spacy.load('en_core_web_sm')
    # print(get_noun_list(sentence))
    # print(pos_tag(["9"]))
    categories=ner(sentence,nlp)
    # print(ner(sentence,nlp))
    # print(EntityRecognizer())

    # test()

    # similar_categories={
    #     "PERSON": [],
    #     "NORP": ["GPE","ORG"],
    #     "FAC": ["ORG","EVENT","PRODUCT"],
    #     "ORG": ["NORP","GPE"],
    #     "GPE": ["ORG","NORP"],
    #     "LOC": ["GPE","NORP","EVENT"],
    #     "PRODUCT": ["WORK_OF_ART","EVENT","ORG","LAW"],
    #     "LAW": ["PRODUCT","WORK_OF_ART"],
    #     "LANGUAGE": ["WORK_OF_ART","EVENT","ORG"],
    # }

    # number_categories=["DATE","TIME","PERCENT","MONEY","CARDINAL","ORDINAL"]
    # SEPARATE FOR DATE, TIME, PERCENT, MONEY, CARDINAL, ORDINAL
    # print(categories)
    q_with_options=generate_options(question_list,categories,nlp)
    # print(q_with_options)
    print_q_with_options(q_with_options)

    # test(nlp)
