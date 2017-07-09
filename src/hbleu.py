import os
import sys
from collections import Counter
import math

def readfile(fileName):
    with open(fileName,'r',encoding='utf-8') as fp:
        lines=fp.readlines()
    plines=[]
    for line in lines:
        if line in ['\n','\r\n']:
            pass
        else:
            plines.append(line.strip())
    return plines

def readdata(cand_path,ref_path):
    candidates=readfile(cand_path)
    references=[]
    if os.path.isfile(ref_path):
        ref_file=ref_path
        ref_lines=readfile(ref_path)
        references.append(ref_lines)
    else:
        references=[]
        ref_files=os.listdir(ref_path)
        for file in ref_files:
            ref_file_path=ref_path+'/'+file
            ref_lines=readfile(ref_file_path)
            references.append(ref_lines)
    return candidates,references

def tokenize(sentences):
    sent_list=[]
    for line in sentences:
        tokens=line.split()
        for token in tokens:
            token=token.strip().lower()
        sent_list.append(tokens)
    return sent_list

def tokenize_data(candidates,references):
    candidates=tokenize(candidates)
    for i in range(len(references)):
        references[i]=tokenize(references[i])
    return candidates,references

def ngrams(n,sentl):
    end=len(sentl)-(n-1)
    sent_grams=[]
    for i in range(end):
        grams=''
        for j in range(i,i+n):
            grams=grams+sentl[j]+' '
        sent_grams.append(grams.strip())
    return sent_grams

def find_ngrams(candidates, references,n):
    cand_grams=[]
    ref_grams=[None]*len(references)
    for cand in candidates:
        cgrams=ngrams(n,cand)
        cand_grams.append(cgrams)
    for i in range(len(references)):
        ref_grams[i]=[]
        for ref in references[i]:
            rgrams=ngrams(n,ref)
            ref_grams[i].append(rgrams)
    return cand_grams,ref_grams

def count_ngrams(candidates,references):
    for i in range(len(candidates)):
        candidates[i]=Counter(candidates[i])
    for i in range(len(references)):
        for j in range(len(references[i])):
            references[i][j]=Counter(references[i][j])
    return candidates,references

def modified_precision(candidates,references,n):
    candidates, references = find_ngrams(candidates, references, n)
    cand_count_ngrams, ref_count_ngrams = count_ngrams(candidates, references)
    n_cand=len(cand_count_ngrams)
    clip_count=[None]*n_cand
    for i in range(n_cand):
        clip_count[i]={}
        for key in cand_count_ngrams[i]:
            cand_count=cand_count_ngrams[i][key]
            max_ref_count=0
            for ref in ref_count_ngrams:
                if key in ref[i]:
                    max_ref_count=max(ref[i][key],max_ref_count)
            clip_count[i][key]=min(cand_count,max_ref_count)


    total_count=0.0
    total_clip_count=0.0
    for i in range(n_cand):
        total_count+=sum(cand_count_ngrams[i].values())
        total_clip_count+=sum(clip_count[i].values())
    mp=total_clip_count/total_count
    print(total_clip_count,total_count,mp)
    return mp

def brevity_penalty(candidates,references):
    length = len(candidates)
    c=0.0
    r=0.0
    for i in range(length):
        cl=len(candidates[i])
        temp_ref=[]
        minref=abs(len(references[0][i])-cl)
        best=len(references[0][i])
        for ref in references:
            if(abs(len(ref[i])-cl)<minref):
                best=len(ref[i])
                minref=abs(len(ref[i])-cl)
        r=r+best
        c=c+cl

    if(c>r):
        bp=1
    else:
        bp=math.exp(1-r/c)
    print(r,c)
    return bp

def calculate_bleu(candidates, references,BP,max_n):
    w = 1/max_n
    bsum=0.0
    for i in range(1,max_n+1):
        mp=modified_precision(candidates, references, i)
        bsum=bsum+w*math.log(mp)
    bleu=BP*math.exp(bsum)
    return bleu



def main():
    #Read candidates and references data
    candidates,references=readdata(sys.argv[1],sys.argv[2])

    candidates, references = tokenize_data(candidates, references)
    sum = 0
    for cand in candidates:
        sum = sum + len(cand)

    BP=brevity_penalty(candidates, references)
    print(BP)
    bleu_score=calculate_bleu(candidates, references,BP,4)
    print(bleu_score)
    with open('bleu_out.txt','w') as fw:
        fw.write(str(bleu_score))
    #modified_precision(candidates, references, 4)




'''
    #Debugging
    print(len(candidates))
    print(len(references))
    for ref in references:
        print(len(ref))

    

    #Debugging
    print('-------------------------------')
    print(len(candidates))
    print(len(references))
    for ref in references:
        print(len(ref))
    print('-------------------------------')
    for can in candidates:
        print(len(can))
    print('-------------------------------')
    for ref in references:
        for r in ref:
            print(len(r))
    
    sent='We propose a method of automatic machine translation evaluation'
    #sent='automatic machine translation evaluation'
    sprint(ngrams(4,sent.split()))
    
    for cand in candidates:
        print(cand)

    for ref in references[0]:
        print(ref)
        #for r in ref:
            #print(r)
'''










if __name__=='__main__':
    main()
