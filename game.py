import time 
import os
import cv2
import autopy
import mediapipe as mp
import numpy as np
import random

from tkinter import BOTTOM, Tk,Button,CENTER, Toplevel,Label, mainloop, Text
from tkinter import messagebox



def manage_points(frame,data,point1,point2,score_1, history,color):

	""""A function to manage the finger's point and update the score

		:param frame: the main fram of the game
		:param data: the list of the ball's locations
		:param point1: the finger's locations of the first player
		:param point2: the finger's locations of the second player
		:param score_1: the score of this party
		:param history: 
		:param color: the given color (green | red | yellow | blue)
	
	:returns:  frame,data,score_1, history
	"""

	to_del = []
	for k in range(len(data)):
		dirt1 = np.zeros_like(frame, np.uint8)
		cv2.circle(dirt1, data[k], 26, (0, 255, 0), cv2.FILLED)
		dirt2 = np.zeros_like(frame, np.uint8)
		cv2.circle(dirt2, point1, 10, (0, 255, 0), cv2.FILLED)
		res = cv2.bitwise_and(dirt1, dirt2)

		dirt3 = np.zeros_like(frame, np.uint8)
		cv2.circle(dirt3, point2, 10, (0, 255, 0), cv2.FILLED)
		ress = cv2.bitwise_and(dirt1, dirt3)
		if(res.sum() > 0):
			score_1 += 5
			history.append(color)
		if(res.sum() > 0 or ress.sum() > 0):
			to_del.append(k)

	for k in to_del:
		try:
			del data[k]
		except KeyError:
			print("keyerror handling")
		except ValueError:
			print("valueerror handling")

	if(len(history) >= 4):
		if(history[-1] == history[-2] and history[-2] == history[-3] and history[-3] == history[-4]):
			score_1 += 50
			cv2.rectangle(frame, (0,0), (frame.shape[0],frame.shape[1]), (255,255,255))

		history = history[len(history) - 1 - 4:]

	return frame,data,score_1, history



def run_game():

	""""the main game's function
	
	:returns:  None
	"""

	try:
		periode = input_periode.get("1.0","2.0")
		nb_players = 2 #input_players.get("1.0","end")
		TIME_PARTY = int(periode) * 23
		mp_hands = mp.solutions.hands
		hands = mp_hands.Hands()
		# mp_draw = mp.solutions.drawing_utils
	except Exception as err:
		messagebox.askyesno("Error", "Please check the data \n {}".format(str(err)))
		return 0

	width = 1024
	height = 900
	cap = cv2.VideoCapture(0)
	cap.set(3, width)
	cap.set(4, height)

	t = 0
	score_1 = 0
	score_2 = 0

	greens = []
	reds = []
	blues = []
	yellows = []

	history_1 = []
	history_2 = []

	while True:
		_,frame = cap.read()
		frame = cv2.flip(frame, 1)

		if(t > TIME_PARTY):	
			if(score_1 > score_2):
				messagebox.askyesno("Score", "Player 1 WIN !")
				break
			if(score_2 > score_1):
				messagebox.askyesno("Score", "Player 2 WIN !")
				break
			if(score_1 == score_2):
				messagebox.askyesno("Score", "DRAW !")
				break
		else:

			frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			results = hands.process(frameRGB)

			if results.multi_hand_landmarks:
				if (len(results.multi_hand_landmarks) == 1):
					cv2.putText(frame, "Waiting for the second player", (0, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0))

				if(len(results.multi_hand_landmarks) == 2):
					cv2.putText(frame, "{}s:".format(int(t / 23)), (0,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0))
					cv2.putText(frame, " Player_1 = {}".format(score_1), (50, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255,0,0))
					cv2.putText(frame, "    VS", (300, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0))
					cv2.putText(frame, "    player2 = {}".format(score_2), (370, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255))
					
					t += 1

					player_1 = results.multi_hand_landmarks[0].landmark
					player_2 = results.multi_hand_landmarks[1].landmark
					height, width, channel = frame.shape

					finger_11 = player_1[8]
					finger_12 = player_1[12]
					finger_21 = player_2[8]
					finger_22 = player_2[12]

					pt1_1 = int(finger_11.x * width), int(finger_11.y * height)
					pt1_2 = int(finger_12.x * width), int(finger_12.y * height)
					pt2_1 = int(finger_21.x * width), int(finger_21.y * height)
					pt2_2 = int(finger_22.x * width), int(finger_22.y * height)

					cv2.circle(frame, pt1_1, 10, (255, 0, 0), cv2.FILLED)
					cv2.circle(frame, pt1_2, 10, (255, 0, 0), cv2.FILLED)
					cv2.circle(frame, pt2_1, 10, (0, 0, 255), cv2.FILLED)
					cv2.circle(frame, pt2_2, 10, (0, 0, 255), cv2.FILLED)

					
					if(t % 10 < random.randint(0,5)):
						wich = random.randint(1,4)
						if(wich == 1):
							greens.append([random.randint(20,width - 20), height])
						elif wich == 2:
							reds.append([random.randint(20,width - 20), height])
						elif wich ==3:
							blues.append([random.randint(20,width - 20), height])
						else:
							yellows.append([random.randint(20,width - 20), height])

					for iter,_ in enumerate(greens):
						greens[iter] = greens[iter][0],greens[iter][1] - 15
						cv2.circle(frame, greens[iter], 26, (0, 255, 255), cv2.FILLED)
					for iter,_ in enumerate(blues):
						blues[iter] = blues[iter][0],blues[iter][1] - 15
						cv2.circle(frame, blues[iter], 26, (255, 255, 0), cv2.FILLED)
					for iter,_ in enumerate(reds):
						reds[iter] = reds[iter][0],reds[iter][1] - 15
						cv2.circle(frame, reds[iter], 26, (255, 0, 255), cv2.FILLED)
					for iter,_ in enumerate(yellows):
						yellows[iter] = yellows[iter][0],yellows[iter][1] - 15
						cv2.circle(frame, yellows[iter], 26, (0, 255, 0), cv2.FILLED)

					frame, greens,score_1, history_1 = manage_points(frame,greens,pt1_1,pt1_2,score_1,history_1,"green")
					frame, reds,score_1, history_1 = manage_points(frame,reds,pt1_1,pt1_2,score_1,history_1,"red")
					frame, blues,score_1, history_1 = manage_points(frame,blues,pt1_1,pt1_2,score_1, history_1,"blue")
					frame, yellows,score_1, history_1 = manage_points(frame,yellows,pt1_1,pt1_2,score_1,history_1,"yellow")

					greens = list(filter(lambda x : x[1] > 5, greens))
					reds = list(filter(lambda x : x[1] > 5, reds))
					blues = list(filter(lambda x : x[1] > 5, blues))
					yellows = list(filter(lambda x : x[1] > 5, yellows))

					frame, greens,score_2, history_2 = manage_points(frame,greens,pt2_1,pt2_2,score_2, history_2,"green")
					frame, reds,score_2, history_2 = manage_points(frame,reds,pt2_1,pt2_2,score_2, history_2,"red")
					frame, blues,score_2, history_2 = manage_points(frame,blues,pt2_1,pt2_2,score_2, history_2, "blue")
					frame, yellows,score_2, history_2 = manage_points(frame,yellows,pt2_1,pt2_2,score_2, history_2, "yellow")

					greens = list(filter(lambda x : x[1] > 5, greens))
					reds = list(filter(lambda x : x[1] > 5, reds))
					blues = list(filter(lambda x : x[1] > 5, blues))
					yellows = list(filter(lambda x : x[1] > 5, yellows))

			else:
				cv2.putText(frame, "Waiting for the two players", (0, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0))
			
			cv2.imshow("Game", frame)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
			else:
				continue

	cap.release()
	cv2.destroyAllWindows()



fenetre = Tk()
fenetre.geometry('400x130')
fenetre.title('CV_game')
label_periode=Label(text="party time en seconds")
label_periode.pack()
input_periode = Text(fenetre,height=1,width=5)
input_periode.pack()

label1=Label(text="number of player")
label1.pack()
input_players = Text(fenetre,height=1,width=5)
input_players.insert("end", "2")
input_players.configure(state='disabled')
input_players.pack()

button=Button(text="Start_game", command=run_game)
button.pack()
button.place(relx=0.5, rely=0.9,anchor=CENTER)

fenetre.resizable(width=400, height=600)

mainloop()
