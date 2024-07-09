
from multiprocessing import Process, Queue 
  
q = Queue()


for i in range(25):
	print("added")
	q.put("hello")