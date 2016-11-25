from Traitement.extract import Extract, suppr_ret_char
import Traitement.timex as tx
import os.path

test_file = "./test/test"

def read_test_file():
    path_learn_dirname = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(path_learn_dirname, test_file), 'rb') as f:
        lines = f.readlines()

    line_test = []
    result = []

    for l in lines:
        s = l.split('|')
        line_test.append(s[0])
        r = s[1].split(',')
        r[len(r)-1] = suppr_ret_char(r[len(r)-1])
        result.append(r)

    return line_test, result


# ambiguite restantes : 
# Cenon gare / mairie de cenon
# 
def test_extract():
    
    test = read_test_file()
    l_test = test[0]
    r_test = test[1]
    
    tot_find_arrets = 0
    tweet_ok = 0

    arret_to_find = 0
    tweets = len(l_test)
    for r in r_test:
        if r != ['']:
            arret_to_find += len(r)
    
    for i in range(0, len(l_test)):
        l = l_test[i]
        r = r_test[i]

        extractor = Extract(unicode(l))
        
        arrets = extractor.get_arrets()
        print arrets
        find_arrets = 0
        for a in arrets:
            if r != ['']:
                if a in r:
                    find_arrets += 1
        tot_find_arrets += find_arrets
        tweet_is_ok = False

        if find_arrets == len(r) and len(arrets) == len(r):
            tweet_ok += 1
            tweet_is_ok = True
        elif r == [''] and len(arrets) == 0:
            tweet_ok += 1
            tweet_is_ok = True
        else:
            print "test numero {}".format(i+1)
            print l
            print(arrets, r, tweet_is_ok)

    print 
    print "Fin des Tests"
    print
    print "Resultats :"
    print
    print "ARRETS TROUVE : {} sur {} soit {}".format(tot_find_arrets, arret_to_find, float(tot_find_arrets)/arret_to_find)
    print "Au total, {} de tweets sont correctemnt extrait sur {}, soit {}".format(tweet_ok, len(l_test), float(tweet_ok)/tweets)



def test_timex():
    
    path_learn_dirname = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(path_learn_dirname, "test/test_timex.txt"), 'rb') as f:
        lines = f.readlines()

    tests = []
    for l in lines:
        tests.append(unicode(l))

    i = 0
    for l in tests:
        i += 1
        print "_____________________________________________"
        print "test", i
        print
        print l
        ex_t = tx.ExtractTime()
        ex = Extract(l)
        print
        print ex_t.tag(l)
        print
        print ex.get_datetime()
        print
        print "_____________________________________________"

    print "FIN DES TESTS"
