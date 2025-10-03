import numpy as np
import math
from scipy import linalg

def solve(joints, members, loads, supports):
    def unit_vector(a, b, joints):  # a is joint, b is member
        if a not in joints.keys() or b[0] not in joints.keys() or b[1] not in joints.keys():
            raise ValueError(f"Invalid joint names: {a}, {b[0]}, {b[1]}")

        x1, y1 = joints[a]  # Get (x, y) coordinates of joint 'a'
        
        # Identify the second joint of the member
        t2 = b[1] if b[0] == a else b[0]  
        x2, y2 = joints[t2]  # Get (x, y) coordinates of 't2'

        delx = x2 - x1
        dely = y2 - y1
        magnitude = (delx**2 + dely**2)**0.5

        if magnitude == 0:
            return [0, 0]  # Avoid division by zero

        return [delx / magnitude, dely / magnitude]

    matrix = []
    b = []
    for i in joints.keys():
        unknownx = [0] * (2 * len(joints.keys()))
        unknowny = [0] * (2 * len(joints.keys()))
        for j in members:
            if i in j:
                index = members.index(j)
                uv = unit_vector(i, j, joints)  # Function unit_vector to be defined
                unknownx[index] = uv[0]
                unknowny[index] = uv[1]

        for rxn in supports.keys():
            if rxn == i:

                if supports[rxn][0] == True:
                    
                    index = len(members) + list(supports.keys()).index(rxn)
                    
                        # Skip invalid supports
                    unknownx[index] = 1
                if(supports[rxn][1] == True):
                    
                    index = len(members) + list(supports.keys()).index(rxn)
                    unknowny[index+1] = 1
        
        matrix.append(unknownx)
        matrix.append(unknowny)
        
        compare = "Ext_" + i
        found = False
        
        for ext in loads.keys():  # Key, e.g., {Ext_A:[fx,fy]}
            if ext == compare:
                found = True
                b.append([loads[ext][0]])
                b.append([loads[ext][1]])
        
        if not found:
            b.append([0])
            b.append([0])
    
    x = members + list(supports.keys())  # Yes, in the exact order
   # for i in matrix:
   #     print(i)

    A = np.array(matrix)
    B = np.array(b)
    answer = linalg.solve(A, B)  # Let's goooo
    member_forces = {}
    support_reactions = {}
    for i in x:   
        if isinstance(i, tuple):
            ans = -round(answer[x.index(i), 0], 3)
            member_forces[i] = ans
        else:
            if supports[i][0]:
                ans = -round(answer[x.index(i), 0], 3)
                support_reactions[i] = (ans, support_reactions.get(i, (0, 0))[1])
            if supports[i][1]:
                ans = -round(answer[x.index(i) + 1, 0], 3)
                support_reactions[i] = (support_reactions.get(i, (0, 0))[0], ans)
    return member_forces, support_reactions
            
'''
joints={"A":(0,0),"B":(3,0),"C":(1.5,3)}
members = ["AB","BC","CA"]
loads = {"Ext_C":[0,-5]}
supports = {"A":[True,True],"B":[False,True]}
solve(joints,members,loads,supports)
'''