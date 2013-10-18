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
    
def _winkler_improvement(string1, string2, commonality):
    n = min(len(string), len(string2))
    for i in xrange(n):
        if string1[i] != string2[i]:
            break
    common_prefix_length = min(4, i)
    winkler = common_prefix_length * 0.1 * (1 - commonality)
    return winkler
    
def _score(string1, string2):
    if string1 == None or string2 == None:
        return -1
    
    s1 = string1.lower()
    s2 = string2.lower()
    s1 = _normalize(s1)
    s2 = _normalize(s2)
    
    l1 = len(s1)
    l2 = len(s2)
    
    L1 = l1
    L2 = l2
    
    if l1 == 0 and l2 == 0:
        return 1.0
    if l1 == 0 or l2 == 0:
        return 0.0
    
    common = 0.0
    best = 2
    max_value = min(l1, l2)
    
    while len(s1) > 0 and len(s2) > 0 and best != 0:
        best = 0
        
        l1 = len(s1)
        l2 = len(s2)
        
        i = 0
        while i < l1 and l1 - i > best:
            j = 0
            while l2 - j > best:
                k = i
                while j < l2 and s1[k] != s2[j]:
                    j += 1
                
                if j != l2:
                    p = j
                    j += 1
                    k += 1
                    while j < l2 and k < l1 and s1[k] == s2[j]:
                        j += 1
                        k += 1
                    if k - i > best:
                        start_s1 = i
                        end_s1 = k;
                        start_s2 = p;
                        end_s2 = j;
        
        new_string = ''
    
        for i in xrange(len(s1)):
            if i >= start_s1 and i < end_s1:
                continue
            new_string += s1[i]
            
        s1 = new_string
        new_string = ''
        
        for i in xrange(len(s2)):
            if i >= start_s2 and i < end_s2:
                continue
            new_string += s2[i]        
        
        s2 = new_string
        
        if best > 2:
            common += best
        else:
            best = 0
    
    commonality = (2 * common) / (l1 + l2)
    
    wi = winkler_improvement(string1, string2, commonality)
    rest1 = L1 - common
    rest2 = L2 - common
    
    #unmatched_s1 = max(rest1, 0)
    #unmatched_s2 = max(rest2, 0)
    unmatched_s1 = rest1/L1
    unmatched_s2 = rest2/L2
    
    suma = unmatched_s1 + unmatched_s2
    product = unmatched_s1 * unmatched_s2
    
    p = 0.6
    
    if suma - product == 0:
        dissimilarity = 0
    else:
        dissimilarity = float(product) / float(p + (1 - p) * (suma - product))
        
    result = commonality - dissimilarity + wi
    return (result + 1) / 2
              
def smoa_distance(string1, string2):
    if string1 == None or string2 == None:
        return 1.0
    
