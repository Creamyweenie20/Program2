import re




def singleStaticAssign(path):
    last_value = {}
    seen = set()
    n = 0
    SSA = ""

    # Consider throwing an error whenever there is a variable both on the lhs and rhs on the same line 

    # Only works for inputs that are single letters and single numbers

    with open(path) as f: 
        for line in f:
            left_new = None
            line = line.replace(" ", "")

            left, right = line.split("=")


            def rename(m):
                name = m.group(0)  
                seen.add(name)            
                if name in last_value:         
                    return last_value[name][-1]
                else:
                    return name 
            
            right = re.sub(r"[A-Za-z][0-9_]*", rename, right)
            right = re.sub(r"([+\-*])", r" \1 ", right)

            if left in seen: 
                left_new = f'foo_{n}'
                if left not in last_value:
                    last_value.update({left: [left_new]})
                else: 
                    last_value[left].append(left_new)
                seen.add(left_new)
                n += 1 
            seen.add(left)



            line = f"{left_new if left_new else left}" + " = " + right 
                    
            SSA += line
            SSA += "\n"

    with open("SSA.txt", "w") as f: 
        f.write(SSA)

    return SSA
