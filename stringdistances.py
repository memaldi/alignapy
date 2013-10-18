def substring_distance(string1, string2):
    if string1 == None or string2 == None:
        return 1.0
    
    len1 = len(string1)
    len2 = len(string2)
    
    if len1 == 0 and len2 == 0:
        return 0.0
    if len1 == 0 or len2 == 0:
        return 1.0
    best = 0
    i = 0
    while i < len1 and len1 - 1 > best:
        j = 0
        while len2 - j > best:
            k = i;   
            while j < len2 and string1[k] != string2[j]:
                j += 1
            if j != len2:
                j += 1
                k += 1
                while j < len2 and k < len1 and string1[k] == string2[j]:  
                    j += 1 
                    k += 1
                best = max(best, k-i)
        i += 1
    return 1.0 - (float(2 * best) / float(len1 + len2))
    

def equal_distance(string1, string2):
    if string1 == None or string2 == None:
        return 1.0
    if string1 == string2:
        return 0.0
    else:
        return 1.0
        
def needlemanwunsch_distance(string1, string2, gap):
    if string1 == None or string2 == None:
        return 1.0
    
    n = len(string1)
    m = len(string2)
    
    if n == 0 or m == 0:
        return 1.0
    
    p = []
    d = []
    
    for i in xrange(n+1):
        p.append(i * gap)
    for j in xrange(1, m+1):
        t_j = string2[j-1]
        d.append(j * gap)
        
        for i in xrange(1, n+1):
            if string1[i-1] == t_j:
                cost = 0
            else:
                cost = 1
            d.append(min(min(d[i-1] + gap, p[i] + gap), p[i-1] + cost))
        d_temp = p
        p = d
        d = d_temp
        d = []
    min_value = min(n, m)
    diff = max(n, m) - min_value
    return float(p[n]) / float(min_value + diff * gap)
    
def levenshtein_distance(string1, string2):
    return needlemanwunsch_distance(string1, string2, 1)
    
def _normalize(string):
    string = string.replace('.', '')
    string = string.replace('_', '')
    string = string.replace(' ', '')
    return string
    
def _score(string1, string2):
    if string1 == None or string2 == None:
        return -1
    
    string1 = string1.lower()
    string2 = string2.lower()
    string1 = _normalize(string1)
    string2 = _normalize(string2)
    
def smoa_distance(string1, string2):
    if string1 == None or string2 == None:
        return 1.0
    
