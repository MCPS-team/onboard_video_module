import os
import numpy as np
import threading
import time
import cv2

class FrameBuffer():
	"""docstring for FrameBuffer"""
	def __init__(self, size, path=""):
		super().__init__()
		self.buffer = []
		self.size = size
		self.path = path
		self.condition = threading.Condition()

	def __push(self, frame):
		self.buffer.append(frame)

	def __pop(self):
		self.buffer.pop(0)

	def add(self, frame):
		with self.condition:
			if not self.condition.acquire():
				self.condition.wait()
			if len(self.buffer) > self.size:
				self.__pop()
			self.__push(frame)
			self.condition.release()
			self.condition.notifyAll()

	def __flush(self):
		self.buffer.clear()

	def poth_hole_detected(self):
		global potHoleID
		pid = potHoleID
		potHoleID += 1
		with self.condition:
			if not self.condition.acquire():
				self.condition.wait()
			print("swapping buffer ...")
			tmp_buffer = self.buffer
			self.tmp_buffer = []
			self.condition.release()
			self.condition.notifyAll()

		path =("{}/{}/".format(self.path, pid))
		
		if not os.path.exists(path):
			os.makedirs(path)
		for f in self.buffer:
			cv2.imwrite("{}{}.png".format(path,"{}-{}".format(pid, time.time())), f)
		self.__flush()
		
def read_video():
	cap = cv2.VideoCapture('prova.mp4')
	print("acquiring resource...")
	print(cap.isOpened())
	while(cap.isOpened()):
		ret, frame = cap.read()
		print ("frame red...")
		if ret==True:
			gray = cv2.cvtColor(frame, 0)

			video_buffer.add(frame)

			cv2.imshow('frame',gray)

			time.sleep(0.1)
		else:
			print("no frame read")
			break

	# Release everything if job is finished
	cap.release()
	cv2.destroyAllWindows()

def detect_pothole():
	print("pothole detected!")
	video_buffer.poth_hole_detected()


video_buffer = FrameBuffer(20,"./frames/")
potHoleID = 0

print("preparing t1...")
t1 = threading.Thread(name="reader", target = read_video)
print("reader started...")
t2 = threading.Thread(name="detector1", target = detect_pothole)
print("preparing detector...")
t1.start()
time.sleep(10)
print("starting detector..")
t2.start()
print("detector started")
time.sleep(10)
t3 = threading.Thread(name="detector2", target = detect_pothole)
t3.start()


#while True:
#	if cv2.waitKey(1) & 0xFF == ord('p'):
#		t2.start()
#
#	if cv2.waitKey(1) & 0xFF == ord('q'):
#		t1.exit()
