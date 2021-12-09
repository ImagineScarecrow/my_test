#--coding:utf-8--



from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import numpy as np
import os
# import sys, random, datetime, os, winreg, getpass, time, threading
import time


root_path = '/home/cxb/data/lanetype_dataset/'
# output_file1 = 'mark_labels_part.txt'
# output_file2 = 'mark_labels_whole.txt'

path_color = [
	[0,0,255],
	[0,255,0],
	[255,0,0],
	[255,255,0]
]
def get_laneData(filepath, lanes):
	labelpath=filepath.replace('jpg','lines.txt')
	img=None
	imgLable=None
	labelPos=[]
	if os.path.exists(filepath) and os.path.exists(labelpath) :
		img=cv2.imread(filepath)
		imgLable=img.copy()

		if os.path.getsize(labelpath):
			label_obj = open(labelpath)
			#遍历车道线编号标记,将标注的车道线像素与车道线标记进行关联
			for lane_idx in range(0, len(lanes)):
				if lanes[lane_idx] == '0':
					labelPos.append([])
				else:
					line =label_obj.readline()
					labelPos.append(line.strip('\n'))
			label_obj.close()

			for lpos in labelPos:
				if not lpos:
					continue
				#位置信息通过空格隔开
				labelC=lpos.split(' ')[:-1]
				xlist=labelC[::2]
				ylist=labelC[1::2]
				lane_hsv_roi = list([])
				for idx,ivalue in enumerate(xlist):
					pix_x = int(float(xlist[idx]))
					pix_y = int(float(ylist[idx]))
					cv2.circle(imgLable,(pix_x, pix_y),2,path_color[labelPos.index(lpos)],2)
					# cv2.rectangle(imgLable,(pix_x-kernel_size, pix_y-kernel_size),(pix_x+kernel_size, pix_y+kernel_size),path_color[labelPos.index(lpos)],2)
		else:
			return img,imgLable  
	else:
		print("Img or Label %s is not exist" %filepath)
	return img,imgLable 

# Main LPR surface
class LPRSurface(Tk):
	labelPicWidth  	= 1800
	labelPicHeight 	= 800
	buttonWidth 	= 150
	buttonHeight 	= 40
	textWidth 		= 80
	textHeight 		= 50
	tkWidth 		= labelPicWidth
	tkHeigth 		= labelPicHeight + 200
	isPicProcessing = False
	root 			= None
	# videoThreadRun	= False
	pic_index = 0
	file_lines = list([])
	# output_labels_dict = dict({})
	output_labels_list = list([])
	
	output_file1 = 'mark_labels_part.txt'
	output_file2 = 'mark_labels_whole.txt'

	def resizePicture(self, imgCV):
		if imgCV is None:
			print("Read Fail!")
			return None
		if self.output_labels_list[self.pic_index][0] + self.output_labels_list[self.pic_index][1] + self.output_labels_list[self.pic_index][2] + self.output_labels_list[self.pic_index][3] != 0:
			cv2.putText(imgCV, "Marked", (1300,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

		imgCVRGB = cv2.cvtColor(imgCV, cv2.COLOR_BGR2RGB)
		img = Image.fromarray(imgCVRGB)
		imgTK = ImageTk.PhotoImage(image=img)

		picWidth = imgTK.width()
		picHeight = imgTK.height()
		# print("Picture Size:", picWidth, picHeight)
		if picWidth <= self.labelPicWidth and picHeight <= self.labelPicHeight:
			return imgTK

		widthScale = 1.0*self.labelPicWidth/picWidth
		heightScale = 1.0*self.labelPicHeight/picHeight

		scale = min(widthScale, heightScale)

		resizeWidth = int(picWidth*scale)
		resizeHeight = int(picHeight*scale)



		img = img.resize((resizeWidth, resizeHeight), Image.ANTIALIAS)
		imgTK = ImageTk.PhotoImage(image=img)

		return imgTK

	# Load picture
	def loadPicture(self):
		# fileName = None
		# fileName = filedialog.askopenfilename(title='Load Picture', \
		# 									  filetypes=[('Picture File', '*.txt'), ('All Files', '*')], \
		# 									  initialdir=root_path)
		fileName = filedialog.askopenfilename(title='Load Picture', \
											  filetypes=[('Picture File', '*.txt'), ('All Files', '*')], \
											  initialdir=" ")
		basename = os.path.basename(fileName)
		basename = os.path.splitext(basename)[0]

		self.output_file1 = "%s-part.txt" %basename
		self.output_file2 = "%s-whole.txt" %basename

		f_obj = open(fileName)
		self.file_lines = f_obj.readlines()
		f_obj.close()
		if len(self.file_lines[0].strip('\n').split(' ')) == 10:
			tmp = [x.strip('\n').split(' ')[6:10] for x in self.file_lines]
			self.output_labels_list = list(map(lambda x:list(map(int, x)), tmp))
		else:
			self.output_labels_list = [[0]*4 for _ in range(len(self.file_lines))]
		self.showPic()

	def showPic(self):
		if  self.file_lines:
			line = self.file_lines[self.pic_index]
			line = line.strip('\n').split(' ')
			# print(line)
			filepath = os.path.join(root_path,line[0][:])   #line[0][1:]
			img_name = os.path.basename(filepath)
			lanes = line[2:6]
			img,imglabel=get_laneData(filepath, lanes)

			if not imglabel.any():
				self.nextPic()

			self.imgOri = self.resizePicture(imglabel)
			self.labelPic.configure(image = self.imgOri, bg="pink")

			self.pic_filename.set(line[0])
			self.process_value.set("%d/%d" %(self.pic_index+1, len(self.file_lines)))
			self.entry_picindex.set(self.pic_index)

			# if self.output_labels_list:
			if self.output_labels_list[self.pic_index][0] + self.output_labels_list[self.pic_index][1] + self.output_labels_list[self.pic_index][2] + self.output_labels_list[self.pic_index][3] != 0:
				self.typeclass_lane1.set(self.output_labels_list[self.pic_index][0])
				self.typeclass_lane2.set(self.output_labels_list[self.pic_index][1])
				self.typeclass_lane3.set(self.output_labels_list[self.pic_index][2])
				self.typeclass_lane4.set(self.output_labels_list[self.pic_index][3])

			# if self.pic_index in self.output_labels_dict:
			# 	self.typeclass_lane1.set(self.output_labels_dict[self.pic_index][0])
			# 	self.typeclass_lane2.set(self.output_labels_dict[self.pic_index][1])
			# 	self.typeclass_lane3.set(self.output_labels_dict[self.pic_index][2])
			# 	self.typeclass_lane4.set(self.output_labels_dict[self.pic_index][3])

	def nextPic(self):
		self.pic_index += 1
		self.showPic()

	def prvePic(self):
		self.pic_index -= 1
		self.showPic()
	
	def setLaneTypeClass(self):
		if  self.file_lines:
			line = self.file_lines[self.pic_index]
			# out_put_msg = "%s %s %s %s %s" %(line self.typeclass_lane1.get() self.typeclass_lane2.get() self.typeclass_lane3.get() self.typeclass_lane4.get())
			out_put_msg = "%s %d %d %d %d\n" %(" ".join(line.strip('\n').split(" ")[:6]), self.typeclass_lane1.get(), self.typeclass_lane2.get(),self.typeclass_lane3.get(), self.typeclass_lane4.get())
			# self.output_labels_dict[self.pic_index] = [self.typeclass_lane1.get(), self.typeclass_lane2.get(),self.typeclass_lane3.get(), self.typeclass_lane4.get()]
			self.output_labels_list[self.pic_index] = [self.typeclass_lane1.get(), self.typeclass_lane2.get(),self.typeclass_lane3.get(), self.typeclass_lane4.get()]
			f = open(self.output_file1,'a+')
			f.writelines(out_put_msg)
			f.close()
			# print("line", line)
			# print(out_put_msg)
			# print("%s %d %d %d %d" %(line self.typeclass_lane1.get() self.typeclass_lane2.get() self.typeclass_lane3.get() self.typeclass_lane4.get()))
			# print(line , self.typeclass_lane1.get(), self.typeclass_lane2.get() ,self.typeclass_lane3.get(), self.typeclass_lane4.get())
		self.showPic()

		#自动遍历到下一帧，减少鼠标点击
		# time.sleep(0.2)
		# self.nextPic()

	def setPicIndex(self):
		self.pic_index = self.entry_picindex.get()
		self.showPic()

	def savLabelsOutput(self):
		f = open(self.output_file2,'w')
		for index in range(0,len(self.file_lines)):
			# out_put_msg = self.file_lines[index].strip('\n') + str(self.output_labels_list[index]) +'\n'
			out_put_msg = " ".join(self.file_lines[index].strip('\n').split(" ")[:6]) + " %d %d %d %d\n"%(self.output_labels_list[index][0],self.output_labels_list[index][1],self.output_labels_list[index][2],self.output_labels_list[index][3])
			f.writelines(out_put_msg)
		f.close()
		messagebox.showinfo('Success','Save market lables, marked %d , total %d' %(self.pic_index+1, len(self.output_labels_list)))

	def __init__(self, *args, **kw):
		super().__init__()
		self.title("LPR Surface")
		self.geometry(str(self.tkWidth) + "x" + str(self.tkHeigth))
		self.resizable(0, 0)

		self.pic_filename = StringVar()
		self.pic_filename.set("Image file name")
		self.labelPicpath = Label(self, textvariable=self.pic_filename, anchor=SW)
		self.labelPicpath.place(x= 300 , y=10, width=400, height=30)

		self.buttonPic = Button(self, text="Open Picture", command=self.loadPicture)
		self.buttonPic.place(x=1300, y=5, width=self.buttonWidth, height=self.buttonHeight)

		self.process_value = StringVar()
		self.labelPicpath = Label(self, textvariable = self.process_value, font=("Arial", 12), anchor=SW)
		self.labelPicpath.place(x= 700 , y=10, width=100, height=30)

		# Picture Label:
		self.labelPic = Label(self, text="Show Picture Area", font=("Arial", 24), bg="sky blue")
		self.labelPic.place(x=0, y=50, width=self.labelPicWidth, height=self.labelPicHeight)


		# prve Button
		self.buttonPic = Button(self, text="Prve", command=self.prvePic)
		self.buttonPic.place(x=500,
							 y=self.labelPicHeight + self.buttonHeight / 2 + 50, \
							 width=self.buttonWidth//2, height=self.buttonHeight)
		# next Button
		self.buttonPic = Button(self, text="Next", command=self.nextPic)
		self.buttonPic.place(x=800,
							 y=self.labelPicHeight + self.buttonHeight / 2 + 50, \
							 width=self.buttonWidth//2, height=self.buttonHeight)

		self.typeclass_lane1 = IntVar()
		self.typeclass_lane2 = IntVar()
		self.typeclass_lane3 = IntVar()
		self.typeclass_lane4 = IntVar()
		# self.typeclass_lane1.set(-1)
		# self.typeclass_lane2.set(-1)
		# self.typeclass_lane3.set(-1)
		# self.typeclass_lane4.set(-1)

		self.entryPlateNum1 = Entry(self,textvariable= self.typeclass_lane1)
		self.entryPlateNum1.place(x= 50 + 0 * 80, y=self.labelPicHeight + 130, \
								width=60 , height=self.textHeight)
		self.entryPlateNum2 = Entry(self,textvariable= self.typeclass_lane2)
		self.entryPlateNum2.place(x= 50 + 1 * 80, y=self.labelPicHeight + 130, \
								width=60 , height=self.textHeight)
		self.entryPlateNum3 = Entry(self,textvariable= self.typeclass_lane3)
		self.entryPlateNum3.place(x= 50 + 2 * 80, y=self.labelPicHeight + 130, \
								width=60 , height=self.textHeight)
		self.entryPlateNum4 = Entry(self,textvariable= self.typeclass_lane4)
		self.entryPlateNum4.place(x= 50 + 3 * 80, y=self.labelPicHeight + 130, \
								width=60 , height=self.textHeight)
		for index in range(4):

			# Vehicle Colour Label:
			self.labellane = Label(self, text="Lane %d" %index, anchor=SW)
			self.labellane.place(x= 50 + index * 80, y=self.labelPicHeight + 105,
									 width=self.textWidth, height=20)



		# set Button
		self.buttonPic = Button(self, text="Set", command=self.setLaneTypeClass)
		self.buttonPic.place(x=400,
							 y=self.labelPicHeight + 130, \
							 width=self.buttonWidth//2, height=self.buttonHeight)

		# set Button
		self.entry_picindex = IntVar()
		self.entry_picindex.set(self.pic_index)
		self.entryPlateNum1 = Entry(self,textvariable= self.entry_picindex)
		self.entryPlateNum1.place(x= 500+250, y=self.labelPicHeight + 130,  width=self.buttonWidth//2, height=self.buttonHeight)


		self.buttonPic = Button(self, text="Set Pic index", command=self.setPicIndex)
		self.buttonPic.place(x=600, y=self.labelPicHeight + 130, width=self.buttonWidth, height=self.buttonHeight)

		self.buttonPic = Button(self, text="Sav Labels", command=self.savLabelsOutput)
		self.buttonPic.place(x=850, y=self.labelPicHeight + 130, width=self.buttonWidth, height=self.buttonHeight)

		self.mainloop()


if __name__ == '__main__':
	LS = LPRSurface()
	print("Finish")
