def validate_username(username):
    l = len(username)
    if ' ' in username or l < 6 or l > 20 or not username or not username.isalnum():
        return False
    else:
        return True

def validate_password(password):
    l = len(password)
    if ' ' in password or l < 8 or l > 20 or not password:
        return False
    
    alpha = False
    digits = False
    spchar = False
    for c in password:
        if not alpha and c.isalpha():
            alpha = True
        if not digits and c.isdigit():
            digits = True
        if not spchar and not c.isalnum():
            spchar = True
    
    if alpha and digits and spchar:
        return True
    return False

def validate_email(emailaddress):
    pos_AT = 0
    count_AT = 0
    count_DT = 0
    if emailaddress[0] == '@' or emailaddress[-1] == '@':
        return False
    if emailaddress[0] == '.' or emailaddress[-1] == '.':
        return False
    for c in range(len(emailaddress)):
        if emailaddress[c] == '@':
            pos_AT = c
            count_AT = count_AT + 1
    if count_AT != 1:
        return False
        
    username = emailaddress[0:pos_AT]
    if not username[0].isalnum() or not username[-1].isalnum():
        return False
    for d in range(len(emailaddress)):
        if emailaddress[d] == '.':
            if d == (pos_AT+1):
                return False
            if d > pos_AT:
                word = emailaddress[(pos_AT+1):d]
                if not word.isalnum():
                    return False
                pos_AT = d
                count_DT = count_DT + 1
    if count_DT < 1 or count_DT > 2:
        return False
        
    return True


def encryptemail(email):
    try:
        e = email.split("@")
        a = e[0][0] + ('*'*(len(e[0])-2)) + e[0][-1]
        b = e[1][0] + ('*'*(len(e[1])-2)) + e[1][-1]
        c = a + '@' + b
    except IndexError:
        return None
    else:
        return c