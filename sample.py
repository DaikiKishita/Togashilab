""""
D,V,N=map(int,input().split())
syuku=[0 for _ in range(D)]
for i in range(N):
    L,R,H=map(int,input().split())
    for i in range(L,R+1):
        if syuku[i-1]>=H or syuku[i-1]==0:
            syuku[i-1]=H

result=V-sum(syuku)
if result<=0:
    print(0)
else:
    print(result)
    """
A,B=map(int,input().split())

def prime(N):
    for i in range(2, int(N/2)+1):
        if (N % i) == 0:
            return False
    else:
        return True

def find(A,B):
    lst=[A,B]
    for i in range(2,min(lst)+1):
        if A%i==0 and B%i==0:
            if prime(i):
                return i
    return False

print(find(A,B))