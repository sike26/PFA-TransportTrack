from Detection import *
import os.path

file_test = ['./test/Panne.test',
             './test/Reprise.test',
             './test/Ralentissement.test',
             './test/NonPertinant.test']


file_test_2 = ['./test2/jeu_test_1', 
               './test2/jeu_test_2']


def set_testing(s, d):
    for k in d.keys():
        if k == s:
            d[k] = True
        else:
            d[k] = False
    return d
    

def test_class(s):
    Clf = Classifier()

    if s == 'SVM':
        tweet_clf = Clf.learn_SVM()
    elif s == 'bayes':
        tweet_clf = Clf.learn_bayes()

    current_test = {'panne': False,
                    'reprise': False,
                    'ralentissement': False,
                    'nonpertinant': False}

    count = [0, 0, 0, 0]
    success = [0, 0, 0, 0]
    error = [0, 0, 0, 0]
    past = ['PANNE\n', 'REPRISE\n', 'RALENTISSEMENT\n', 'NONPERTINANT\n']
    test = dict()
    for Test in file_test:
        path_learn_dirname = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(path_learn_dirname, Test), 'rb') as f:
            lines = f.readlines()
            test[Test] = lines

    for k in test.keys():

        t = test[k]

        if t[0] == 'PANNE\n':
            curent_test = set_testing('panne', current_test)
        elif t[0] == 'REPRISE\n':
            curent_test = set_testing('reprise', current_test)
        elif t[0] == 'RALENTISSEMENT\n':
            curent_test = set_testing('ralentissement', current_test)
        elif t[0] == 'NONPERTINANT\n':
            curent_test = set_testing('nonpertinant', current_test)
            
        for l in t:
            class_tweet = Clf.get_class(l, tweet_clf)
            
            if current_test['panne'] and (not l in past):
                count[0] += 1
                if class_tweet == 'PANNE':
                    success[0] += 1
                else:
                    error[0] += 1
                    print "PANNE erreur : {} {}".format(l, class_tweet)

            elif current_test['reprise'] and (not l in past):
                count[1] += 1
                if class_tweet == 'REPRISE':
                    success[1] += 1
                else:
                    error[1] += 1
                    print "REPRISE erreur : {} {}".format(l, class_tweet)

            elif current_test['ralentissement'] and (not l in past):
                count[2] += 1
                if class_tweet == 'RALENTISSEMENT':
                    success[2] += 1
                else:
                    error[2] += 1
                    print "RALENTISSEMENT erreur : {} {}".format(l, class_tweet)
            elif current_test['nonpertinant'] and (not l in past):
                count[3] += 1
                if class_tweet == 'NONPERTINANT':
                    success[3] += 1
                else:
                    error[3] += 1
                    print "NP erreur : {} {}".format(l, class_tweet)
            

        
    print("Fin du test")
    print 'PANNE ({}): erreurs: {}, {}  || succes : {}, {}'.format(count[0], error[0], float(error[0])/(count[0]), success[0], float(success[0])/(count[0]))
    print 'REPRISE ({}): erreurs: {}, {}  || succes : {}, {}'.format(count[1], error[1], float(error[1])/count[1], success[1], float(success[1])/count[1])
    print 'RALENTISSEMENT ({}): erreurs: {}, {}  || succes : {}, {}'.format(count[2], error[2], float(error[2])/(count[2]), success[2], float(success[2])/(count[2]))
    print 'NON PERTINANT ({}): erreurs: {}, {}  || succes : {}, {}'.format(count[3], error[3], float(error[3])/(count[3]), success[3], float(success[3])/(count[3]))

    tot_err = 0
    for i in error:
        tot_err += i
        
    tot_sus = 0
    for i in success:
        tot_sus += i
        
    tot_count = 0
    for i in count:
        tot_count += i

    print 'TOTAL (sur {} tweets) erreurs: {}, {}  || succes : {}, {}'.format(tot_count, tot_err, float(tot_err)/tot_count, tot_sus, float(tot_sus)/tot_count)

 

    

def suppr_ret_char(s):
    if s[len(s)-1] == '\n':
        return s[:len(s)-1]
    else:
        return s
    

def test_class_2(filename, transport='TRAM', predict=False):
    
    class_find = 0
    class_to_find = 0
    class_fail = 0

    tweet_ok = 0
    source = ''

    if transport == 'TRAM':
        source = 'TBC TramA'
    elif transport == 'BUS':
        source = 'TBC Lianes1'

    path_learn_dirname = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(path_learn_dirname, filename), 'rb') as f:
        lines = f.readlines()

    test = []
    result = []
    for l in lines:
        test.append(l.split('|')[0])
        result.append(l.split('|')[1].split(','))

    for i in range(0,len(test)):
        t = test[i]
        tweet = Tweet("", source, "", t, 42)
        TW = TweetTreatment(tweet, predict)
        find = TW.classes

        tmp_find = 0
        for j in range(0, len(result[i])):
            r = result[i][j]
            class_to_find += 1
            r = suppr_ret_char(r)
            if find[j] == r:
                tmp_find += 1
                class_find += 1
            else:
                class_fail += 1
                print(TW.contents[j], r, find[j])
        if tmp_find == len(result[i]):
            tweet_ok += 1
        

    tweet_tested = len(lines)
    print 'TOTAL (sur {} tweets) succes : {}, {}, taux d\'erreur {}'.format(tweet_tested, tweet_ok, float(tweet_ok)/tweet_tested, float(tweet_tested - tweet_ok)/tweet_tested)
    print 'Soit {} classement correct sur {}, succes : {}, erreur {}'.format(class_find, class_to_find, float(class_find)/class_to_find, float(class_fail)/class_to_find)
