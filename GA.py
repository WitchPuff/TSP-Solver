from cmath import log
import matplotlib.pyplot as plt
import random
import numpy as np
import time
import math

from soupsieve import select


#读取城市的x，y坐标
def load(txt):
    f = open(txt)
    map=[]
    flag = 0
    for line in f:
        line = line.strip()
        if line == "NODE_COORD_SECTION":
            flag = 1
            continue
        if line == "EOF":
            break
        if flag:
            a = line.split()
            map.append((float(a[1]),float(a[2])))
    return tuple(map)

#获取两个城市间的二维欧几里得距离
def getDist():
    global map,size
    dist = np.zeros((size,size))
    for i in range(0,size):
        for j in range(0,size):
            dist[i][j] = ((map[i][0]-map[j][0])**2 + (map[i][1]-map[j][1])**2)**0.5
    return dist

txt = "C:\\Users\\Cecilia\\Desktop\\TSP\\ch130.txt"
map = load(txt)
size = len(map)
visited = {}
solutions = []
DIST = getDist()
count = 0
M = 30 #种群大小


#根据路径获取该路径总代价
def getCost(path):
    cost = 0
    former = path[0]
    for city in path:
        cost += DIST[former][city]
        former = city
    cost += DIST[path[0]][path[-1]]
    return cost

#Partial-Mapped crossover
def PMX(i,j):
    global size
    s,t = sorted(random.sample(range(1,size),2))
    next_i = list(i[:s] + j[s:t] + i[t:])
    next_j = list(j[:s] + i[s:t] + j[t:])
    #建立映射表
    mapped_i = {next_i[k]:next_j[k] for k in range(s,t)}
    mapped_j = {next_j[k]:next_i[k] for k in range(s,t)}
    #判断是否满足解的条件（每个城市皆访问一次）
    while len(set(next_i)) != len(next_i): 
        for k in range(size):
            if k < t and k >= s:
                continue
            while next_i[k] in j[s:t]:
                next_i[k] = mapped_i[next_i[k]]
    while len(set(next_j)) != len(next_j):
        for k in range(size):
            if k < t and k >= s:
                continue
            while next_j[k] in i[s:t]:
                next_j[k] = mapped_j[next_j[k]]
    next_i = tuple(next_i)
    next_j = tuple(next_j)
    if next_i not in visited:
        visited.update({next_i:getCost(next_i)})
    if next_j not in visited:
        visited.update({next_j:getCost(next_j)})
    return next_i,next_j
        
    
    

#反转一段区间，获取新邻域
def reverse(path):
    global size
    min = 1000000000
    for cnt in range(100):
        i,j = sorted(random.sample(range(1,size-1),2))
        path_ = path[:i] + path[i:j+1][::-1] + path[j+1:]
        if path_ not in visited:
            cost = getCost(path_)
            visited.update({path_:cost})
        else:
            cost = visited[path_]
        if cost < visited[path]:
            min = cost
            p = path_
            break
        if cost < min:
            min = cost
            p = path_
    return p


#交换两个城市，获取新邻域
def exchange(path):
    global size
    min = 1000000000
    for cnt in range(100):
        i,j = sorted(random.sample(range(1,size-1),2))
        path_ = path[:i] + path[j:j+1] + path[i+1:j] + path[i:i+1] + path[j+1:]
        if path_ not in visited:
            cost = getCost(path_)
            visited.update({path_:cost})
        else:
            cost = visited[path_]
        if cost < visited[path]:
            min = cost
            p = path_
            break
        if cost < min:
            min = cost
            p = path_
    return p
    
#随机挑选两个城市插入序列头部，获取新邻域
def insert(path):
    global size,solutions
    min = 1000000000
    for cnt in range(100):
        i,j = sorted(random.sample(range(1,size-1),2))
        path_ = path[i:i+1] + path[j:j+1] + path[:i] + path[i+1:j] + path[j+1:]
        if path_ not in visited:
            cost = getCost(path_)
            visited.update({path_:cost})
        else:
            cost = visited[path_]
        if cost < visited[path]:
            min = cost
            p = path_
            break
        if cost < min:
            min = cost
            p = path_
    return p
         

#遗传算法
def GA(paths,kmax):
    global M,solutions
    temp = paths
    for k in range(kmax):
        count = 0
        flag = 0
        children = [] #存储此代交叉、变异产生的子种群
        #加入当前种群中的最优解，使得下一代种群的最优解一定不会劣于当前种群最优解
        children.append(temp[0]) 
        for l in range(M):
            while True:
                cur = sorted(temp[:], key=lambda x:visited[x])[0]
                i = random.randrange(M)
                count+=1
                if temp[i] != cur:
                    break
                if count > 100000:
                    flag = 1
                    break
            if flag == 0:
                a,b = PMX(temp[i],cur) #使用PMX交叉操作
                children.append(a)
                children.append(b)
        for l in range(M):
            i = random.randrange(M)
            children.append(reverse(temp[i])) #使用反转作为变异操作
        temp = sorted(children[:], key=lambda x:visited[x])[:M] #选取子代中最优的前M个解
        solutions.append(visited[temp[0]]) #记录此次迭代产生的下一代的最优解
        #print(k,visited[temp[0]])
    return temp[0]
    


def main():
    global visited,size,map,M,solutions
    kmax = 1300
    for i in range(8):
        time_start = time.time()
        start = [tuple(random.sample(range(size),size)) for m in range(M)]
        visited = {key:getCost(key) for key in start}
        path = GA(start,kmax)
        cost = visited[path]
        path = path[:] + path[:1]
        time_end = time.time()
        print()
        #print('Algorithm GA iterated',kmax,'times!\n',sep=' ')
        best = 6110
        print(time_end-time_start,cost,(cost-best)/best,sep=" ") #此处单位为秒
        '''print('You got the best solution:',cost,sep='\n')
        print(path)
        
        print("误差为：",(cost-best)/best)'''
    
    '''x = np.array([map[i][0] for i in path])
    y = np.array([map[i][1] for i in path])
    i = np.arange(0,len(solutions))
    solutions = np.array(solutions)
    plt.subplot(121)
    plt.plot(x,y)
    plt.subplot(122)
    plt.plot(i,solutions)
    plt.show()'''


main()
    
    
    