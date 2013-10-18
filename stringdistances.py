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
