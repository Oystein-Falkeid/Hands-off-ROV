################################################################################
# Copyright (C) 2012-2016 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

import Leap         #, sys, time
import serial
# import math
from tkinter import *
import customtkinter
import numpy as np
import struct
import time

# from PIL import ImageTk, Image
# from matplotlib.figure import Figure
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)





ser = serial.Serial('COM12', 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout = 1)
start = ("<").encode()


class HMI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #Deklarerer varriabler
        self.coords_unit = 50
        self.leap_connected = FALSE
        self.controller_enable = FALSE
        
        self.frame_width = 0
        self.frame_height = 0
        

        #Instillinger for HMI
        self.title('Hands-off ROV')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.state('zoomed')

        self.settings_frame = customtkinter.CTkFrame(self)

        self.controller_frame = customtkinter.CTkFrame(self)

        
        #settings page deffineres
        self.settings_lable = customtkinter.CTkLabel(self.settings_frame, text = "Hands-off ROV", font = ('Times', 50, 'bold'))
        self.settings_lable.grid(row=0, column=0, columnspan = 2, padx=20, pady=20)

        self.controller_button = customtkinter.CTkButton(self.settings_frame, text = "Controller", command = self.controller_button_event)
        self.controller_button.grid(row=1, column=0, columnspan = 2, padx=20, pady=20)

        #Left hand and right hand settings button
        self.first_hand = "Right hand"      #Right hand as standard first hand
        self.second_hand = "Left hand"

        self.left_hand_button = customtkinter.CTkButton(self.settings_frame, text = "Left hand", command = self.left_hand_event)
        self.left_hand_button.grid(row=2, column=0, padx=10, pady=0)
        
        self.right_hand_button = customtkinter.CTkButton(self.settings_frame, text = "Right hand", command = self.right_hand_event)
        self.right_hand_button.grid(row=2, column=1, padx=10, pady=0)

        self.hand_label = customtkinter.CTkLabel(self.settings_frame, text = "Right hand chosen as steering hand")
        self.hand_label.grid(row = 3, column = 0, columnspan = 2, padx = 20, pady = 0)

        #Slider and label:
        self.sensitivity = 50       #Sensitivity starts at 50%
        self.sensitivity_factor = self.sensitivity / 50
        self.sensitivity_slider = customtkinter.CTkSlider(self.settings_frame, from_ = 1, to = 100, command = self.slider_value)
        self.sensitivity_slider.grid(row=4, column=0, columnspan = 2, padx=20, pady=0)
        self.sensitivity_label = customtkinter.CTkLabel(self.settings_frame, text="Sensitivity: " + str(self.sensitivity) + "%")
        self.sensitivity_label.grid(row = 5, column = 0, columnspan = 2, padx=20, pady=0)

        
        self.use_secondhand_switchstate = customtkinter.BooleanVar(value=FALSE)
        self.use_secondhand = FALSE

        self.use_secondhand_text = customtkinter.CTkLabel(self.settings_frame, text=("Use " + self.second_hand + " for sensitivity"))
        self.use_secondhand_text.grid(row = 6, column = 0, columnspan=2, padx=5)
        self.use_secondhand_switch = customtkinter.CTkSwitch(self.settings_frame, text=" ", variable=self.use_secondhand_switchstate, onvalue=TRUE, offvalue=FALSE, command=self.use_secondhand_switch_event)
        self.use_secondhand_switch.grid(row = 6, column = 1, padx=5)

        self.leapstatus_text = customtkinter.CTkLabel(self.settings_frame, text ="", font = ('Times', 20))
        self.leapstatus_text.grid(row=7, column=0, columnspan = 2, padx=20, pady=10)

        self.connecterror_text = customtkinter.CTkLabel(self.settings_frame, text="", font = ('Times', 20, 'bold'), text_color="red")
        self.connecterror_text.grid(row=8, column=0, columnspan = 2, padx=5, pady=5)


        #Controller frame design
        self.canvas = customtkinter.CTkCanvas(self.controller_frame, bg='#EEE')
        self.canvas.grid(row=0, column=0, sticky="nsew")


        #Width = 140, height = 28
        self.settings_button = customtkinter.CTkButton(self.canvas, text = "Settings", command = self.settings_button_event)
        self.settings_button.configure(width = int(self.coords_unit * 6), height = int(self.coords_unit * 1.5), font = ('Times', int(self.coords_unit/2)))
        # self.resize_button = customtkinter.CTkButton(self.canvas, text = "Resize", command = self.resize_button_event)

        self.map_compass_vect = [
            [self.coords_unit*0, -self.coords_unit*0.5, self.coords_unit*0, self.coords_unit*0.5],
            [self.coords_unit*1.25, self.coords_unit*1.75, self.coords_unit*0.25, self.coords_unit*1.75]]


        # Bind the movement to the key press event
        self.bind("<Key>", self.on_keypress)

        #start on controller page
        self.select_frame_by_name("settings")

    #Kan brukes til å monitorere keyboards for hurtigtaster
    def on_keypress(self, event):
        print("Key stroke?")

    #Definerer handknapper og slider

    def left_hand_event(self):
        self.hand_label.configure(text = ("Left hand chosen as steering hand"))
        self.first_hand = "Left hand"
        self.second_hand = "Right hand"
        
    def right_hand_event(self):
        self.first_hand = "Right hand"
        self.second_hand = "Left hand"
        self.hand_label.configure(text = ("Right hand chosen as steering hand"))


    def slider_value(self, value):
        self.sensitivity = int(value)
        if(not(self.use_secondhand)):
            self.sensitivity_label.configure(text = ("Sensitivity: " + str(int(value)) + "%"))


    def use_secondhand_switch_event(self):
        # self.use_secondhand = self.use_secondhand_switch
        self.use_secondhand = self.use_secondhand_switchstate.get()

        if(self.use_secondhand):
            self.sensitivity_label.configure(text = "Sensitivity is hand decided. Slider is inactive.")
        else:
            self.sensitivity_label.configure(text = ("Sensitivity: " + str(int(self.sensitivity)) + "%"))





    #Tegner elementene i emnulatoren ved oppstart
    def Draw_canvas_elements(self,senter_x,senter_y):

        # Tegner skillelinje på midten
        self.centerline = self.canvas.create_line(
            senter_x, senter_y-self.coords_unit*14.5, senter_x, senter_y+self.coords_unit*14.5, dash=(4, 2))
        

        # Tegner bilen
        self.car_wheel1 = self.canvas.create_aa_circle(
            senter_x*1.5 + self.coords_unit, senter_y-self.coords_unit, int(self.coords_unit/3), fill = "black"
        )
        self.car_wheel2 = self.canvas.create_aa_circle(
            senter_x*1.5 - self.coords_unit, senter_y-self.coords_unit, int(self.coords_unit/3), fill = "black"
        )
        self.car_wheel3 = self.canvas.create_aa_circle(
            senter_x*1.5 - self.coords_unit, senter_y+self.coords_unit, int(self.coords_unit/3), fill = "black"
        )
        self.car_wheel4 = self.canvas.create_aa_circle(
            senter_x*1.5 + self.coords_unit, senter_y+self.coords_unit, int(self.coords_unit/3), fill = "black"
        )

        self.car_body = self.canvas.create_rectangle(
            senter_x*1.5 - self.coords_unit, senter_y - self.coords_unit, 
            senter_x*1.5 + self.coords_unit, senter_y + self.coords_unit, 
            fill="blue", outline="blue")

        self.car_front = self.canvas.create_oval(
            senter_x*1.5 - self.coords_unit, senter_y - self.coords_unit*2 , 
            senter_x*1.5 + self.coords_unit, senter_y + self.coords_unit*0, 
            fill = "blue", outline="blue")

        self.car_back = self.canvas.create_oval(
            senter_x*1.5 - self.coords_unit, senter_y - self.coords_unit*0 , 
            senter_x*1.5 + self.coords_unit, senter_y + self.coords_unit*2, 
            fill = "blue", outline="blue")
        
        self.arrow_left = self.canvas.create_polygon(
            0,0,
            0,0,
            0,0,
            0,0,
            0,0,
            0,0,
            fill="black"
        )

        self.arrow_right = self.canvas.create_polygon(
            0,0,
            0,0,
            0,0,
            0,0,
            0,0,
            0,0,
            fill="black"
        )

        self.left_stop = self.canvas.create_aa_circle(0, 0, 0, fill = "black")
        self.right_stop = self.canvas.create_aa_circle(0, 0, 0, fill = "black")
   
        
        # Tegner map og innhold på venstre side:
        self.firsthand_text = self.canvas.create_text(senter_x*0.5, self.coords_unit*4, font = ('Times', int(hmi.coords_unit), 'bold'))
        self.secondhand_text = self.canvas.create_text(senter_x*0.5, self.coords_unit*6, font = ('Times', int(hmi.coords_unit), 'bold'))
        self.handinfo_text = self.canvas.create_text(senter_x *0.5, self.coords_unit*8, font = ('Times', int(self.coords_unit*0.6)), text=(self.first_hand + " chosen as steering hand"))
        self.settings_button.place(x=self.coords_unit/2, y=self.coords_unit/2)
        # self.resize_button.place(x=0, y=30)
        
        #Tegner MAP

        self.map_rectangle = self.canvas.create_rectangle(
            self.coords_unit, senter_y - self.coords_unit*4, 
            senter_x - self.coords_unit, senter_y + self.coords_unit*14, 
            fill="white", outline="black")
        self.map_header = self.canvas.create_text(senter_x*0.5, senter_y - self.coords_unit*3, font = ('Times', int(self.coords_unit*0.6), 'bold'), text=" ")
        self.map_speed = self.canvas.create_text(self.coords_unit*4, senter_y + self.coords_unit*13, font = ('Times', int(self.coords_unit*0.6), 'bold'), text= "Speed: ", justify="left")
        self.map_distance = self.canvas.create_text(senter_x - self.coords_unit*6, senter_y + self.coords_unit*13, font = ('Times', int(self.coords_unit*0.6), 'bold'), text= "Distance: ", justify="left")
        
        self.drawline_x = [senter_x*0.5] 
        self.drawline_y = [senter_y + self.coords_unit*12] 
        self.drawline =  []
        self.map_start = self.canvas.create_aa_circle(self.drawline_x[0], self.drawline_y[0], int(self.coords_unit/5), fill = "black")
        


        self.map_compass_vect = [
            [self.coords_unit*0, -self.coords_unit*0.5, self.coords_unit*0, self.coords_unit*0.5],
            [self.coords_unit*0.25, self.coords_unit*0.75, -self.coords_unit*0.75, self.coords_unit*0.75]]
        
        
        
        self.map_compass =  self.canvas.create_polygon(
            senter_x - self.coords_unit*3 + self.map_compass_vect[0][0]  , senter_y - self.coords_unit*2.5 + self.map_compass_vect[1][0],
            senter_x - self.coords_unit*3 + self.map_compass_vect[0][1]  , senter_y - self.coords_unit*2.5 + self.map_compass_vect[1][1],
            senter_x - self.coords_unit*3 + self.map_compass_vect[0][2]  , senter_y - self.coords_unit*2.5 + self.map_compass_vect[1][2],
            senter_x - self.coords_unit*3 + self.map_compass_vect[0][3]  , senter_y - self.coords_unit*2.5 + self.map_compass_vect[1][3],
            outline="blue", fill="blue"
        )


        # Definerer sensitivitetstekst fra secondhand
        self.secondhand_sensitivity_text = self.canvas.create_text(senter_x*1.5, senter_y - self.coords_unit*13, font=('Times', int(self.coords_unit*0.7), 'bold'), text=" ")


        #Definerer first hand pointer
        self.firsthand_pointer_base = self.canvas.create_aa_circle(
            senter_x*1.5, senter_y, int(self.coords_unit/3), fill = "white"
        )
        self.firsthand_pointer = self.canvas.create_aa_circle(
            senter_x*1.5, senter_y, int(self.coords_unit/4), fill = "black"
        )

        # Definerer second hand pointer
        self.secondhand_pointer_base = self.canvas.create_aa_circle(
            senter_x*1.5, senter_y, int(self.coords_unit/3), fill = "white"
        )
        self.secondhand_pointer = self.canvas.create_aa_circle(
            senter_x*1.5, senter_y, int(self.coords_unit/4), fill = "black"
        )





        
    #endrer pilen fremmover
    def Draw_firsthand_movement(self,x_value, y_value):
        if (self.controller_enable):
            senter_x = (self.frame_width) * 0.75
            senter_y = (self.frame_height) / 2

            self.canvas.coords(self.firsthand_pointer_base, senter_x+x_value*self.coords_unit/20, senter_y+y_value*self.coords_unit/20)
            self.canvas.coords(self.firsthand_pointer, senter_x+x_value*self.coords_unit/20, senter_y+y_value*self.coords_unit/20)

    def Draw_secondhand_movement(self,x_value, y_value):
        if (self.controller_enable):
            senter_x = (self.frame_width) * 0.75
            senter_y = (self.frame_height) / 2

            self.canvas.coords(self.secondhand_pointer_base, senter_x+x_value*self.coords_unit/40, senter_y+y_value*self.coords_unit/40)
            self.canvas.coords(self.secondhand_pointer, senter_x+x_value*self.coords_unit/40, senter_y+y_value*self.coords_unit/40)


    def Rotate_CompassArrow(self):
        rotate = [[np.cos(rov.beta_tot), -np.sin(rov.beta_tot)],[np.sin(rov.beta_tot), np.cos(rov.beta_tot)]]
        self.map_compass_vect_rotate = np.dot(rotate, self.map_compass_vect)
        self.canvas.coords(self.map_compass,
            self.frame_senter_x - self.coords_unit*3 + self.map_compass_vect_rotate[0][0]  , self.frame_senter_y - self.coords_unit*2.5 + self.map_compass_vect_rotate[1][0],
            self.frame_senter_x - self.coords_unit*3 + self.map_compass_vect_rotate[0][1]  , self.frame_senter_y - self.coords_unit*2.5 + self.map_compass_vect_rotate[1][1],
            self.frame_senter_x - self.coords_unit*3 + self.map_compass_vect_rotate[0][2]  , self.frame_senter_y - self.coords_unit*2.5 + self.map_compass_vect_rotate[1][2],
            self.frame_senter_x - self.coords_unit*3 + self.map_compass_vect_rotate[0][3]  , self.frame_senter_y - self.coords_unit*2.5 + self.map_compass_vect_rotate[1][3])
        
        
        


    def Draw_arrows_movement(self, length_left, length_right):
        length_left = (length_left -100) * self.coords_unit/20
        length_right = (length_right -100) * self.coords_unit/20

        senter_x = (self.frame_width) * 0.75
        senter_y = (self.frame_height)/2

        if(length_left > 0):
            self.canvas.coords(
                self.arrow_left,
                senter_x - self.coords_unit*5, senter_y - self.coords_unit*0,
                senter_x - self.coords_unit*4, senter_y - self.coords_unit*0.75,
                senter_x - self.coords_unit*3, senter_y - self.coords_unit*0,
                senter_x - self.coords_unit*3, senter_y - self.coords_unit*0 - length_left,
                senter_x - self.coords_unit*4, senter_y - self.coords_unit*0.75 - length_left,
                senter_x - self.coords_unit*5, senter_y - self.coords_unit*0 - length_left,
                )
            self.canvas.coords(self.left_stop,0,0,0)
            
        elif(length_left < 0):
            self.canvas.coords(
                self.arrow_left,
                senter_x - self.coords_unit*5, senter_y - self.coords_unit*0,
                senter_x - self.coords_unit*4, senter_y + self.coords_unit*0.75,
                senter_x - self.coords_unit*3, senter_y - self.coords_unit*0,
                senter_x - self.coords_unit*3, senter_y - self.coords_unit*0 - length_left,
                senter_x - self.coords_unit*4, senter_y + self.coords_unit*0.75 - length_left,
                senter_x - self.coords_unit*5, senter_y - self.coords_unit*0 - length_left,
                )
            self.canvas.coords(self.left_stop,0,0,0)
        else:
            self.canvas.coords(
                self.arrow_left,
                0,0,
                0,0,
                0,0,
                0,0,
                0,0,
                0,0)
            self.canvas.coords(self.left_stop, senter_x - self.coords_unit*4, senter_y - self.coords_unit*0, int(self.coords_unit/2))
            
        #-----------------------
            
        if(length_right > 0):
            self.canvas.coords(
                self.arrow_right,
                senter_x + self.coords_unit*5, senter_y - self.coords_unit*0,
                senter_x + self.coords_unit*4, senter_y - self.coords_unit*0.75,
                senter_x + self.coords_unit*3, senter_y - self.coords_unit*0,
                senter_x + self.coords_unit*3, senter_y - self.coords_unit*0 - length_right,
                senter_x + self.coords_unit*4, senter_y - self.coords_unit*0.75 - length_right,
                senter_x + self.coords_unit*5, senter_y - self.coords_unit*0 - length_right,
                )
            self.canvas.coords(self.right_stop,0,0,0)
        elif(length_right < 0):
            self.canvas.coords(
                self.arrow_right,
                senter_x + self.coords_unit*5, senter_y - self.coords_unit*0,
                senter_x + self.coords_unit*4, senter_y + self.coords_unit*0.75,
                senter_x + self.coords_unit*3, senter_y - self.coords_unit*0,
                senter_x + self.coords_unit*3, senter_y - self.coords_unit*0 - length_right,
                senter_x + self.coords_unit*4, senter_y + self.coords_unit*0.75 - length_right,
                senter_x + self.coords_unit*5, senter_y - self.coords_unit*0 - length_right,
                )
            self.canvas.coords(self.right_stop,0,0,0)
        else:
            self.canvas.coords(
                self.arrow_right,
                0,0,
                0,0,
                0,0,
                0,0,
                0,0,
                0,0)
            self.canvas.coords(self.right_stop, senter_x + self.coords_unit*4, senter_y - self.coords_unit*0, int(self.coords_unit/2))
            






    #bestemmer hvilke fane som skal vises
    def select_frame_by_name(self, name):
        if name == "settings":
            self.settings_frame.grid(row=0, column=0, sticky=N)
        else:
            self.settings_frame.grid_forget()
        if name == "controller":
            self.controller_frame_init()
        else:
            self.controller_frame_forget()

    #Sletter alle elemntene i emulateron når fanen lukkes
    def controller_frame_forget(self):
        self.controller_enable = FALSE
        self.controller_frame.grid_forget()

        try:
            # Deleting arrows and info
            self.canvas.delete(self.centerline)
            self.canvas.delete(self.handinfo_text)
            self.canvas.delete(self.firsthand_text)
            self.canvas.delete(self.secondhand_text)
            self.canvas.delete(self.map_rectangle)
            self.canvas.delete(self.map_header)
            self.canvas.delete(self.map_speed)
            self.canvas.delete(self.map_distance)
            self.canvas.delete(self.map_start)
            self.canvas.delete(self.map_compass)
            self.canvas.delete(self.arrow_left)
            self.canvas.delete(self.arrow_right)
            self.canvas.delete(self.left_stop)
            self.canvas.delete(self.right_stop)
            self.canvas.delete(self.secondhand_sensitivity_text)

            #Deleting the car:
            self.canvas.delete(self.car_wheel1)
            self.canvas.delete(self.car_wheel2)
            self.canvas.delete(self.car_wheel3)
            self.canvas.delete(self.car_wheel4)
            self.canvas.delete(self.car_body)
            self.canvas.delete(self.car_front)
            self.canvas.delete(self.car_back)
            

            #firsthand og secondhand pointer
            self.canvas.delete(self.firsthand_pointer)
            self.canvas.delete(self.firsthand_pointer_base)
            self.canvas.delete(self.secondhand_pointer)
            self.canvas.delete(self.secondhand_pointer_base)
            
            #Map
            self.canvas.delete(self.map_start)
            for i in self.drawline:
                self.canvas.delete(self.drawline[i])
                
        except:
            i = 0 #Må ha noe her
    
    #Tegner alle elementene i emulatoren når fanen åpnes
    def controller_frame_init(self):
        self.controller_enable = TRUE
        self.controller_frame.grid(row=0, column=0, sticky="nsew")#row=0, column=0, sticky="nsew"
        self.controller_frame.update()
        self.frame_width = self.controller_frame.winfo_width()
        self.frame_height = self.controller_frame.winfo_height()
        self.coords_unit = self.frame_height/30
        self.canvas.configure(width=self.frame_width, height=self.frame_height)
        self.frame_senter_x = self.frame_width/2
        self.frame_senter_y = self.frame_height/2
        self.Draw_canvas_elements(self.frame_senter_x,self.frame_senter_y)
        self.sensitivity_factor = self.sensitivity / 50
        ROV.ROV_reset(rov)

        self.settings_button.configure(width = int(self.coords_unit * 8), height = int(self.coords_unit * 2), font = ('Times', int(self.coords_unit/2)))

    #Når hjem knappen i menyen trykkes
    def settings_button_event(self):
        self.select_frame_by_name("settings")

    #Resize button
    # def resize_button_event(self):
    #     self.controller_frame_forget()
    #     self.controller_frame_init()
    
    #Når controller knappen i menyen trykkes
    def controller_button_event(self):
        if(self.leap_connected):
            self.select_frame_by_name("controller")
        else:
            self.connecterror_text.configure(text = " ")

            self.connecterror_text.configure(text = "Connect Leap before entering the controller.")


    #Når det endres valg i nedtreksmenyen
    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)



#----------------------------------------------------------------------------------------------------------------------------------------------
# Fartøysklasse
class ROV():
    def __init__(self):
        super().__init__()
        self.index = 0
        self.width = 0.175
        self.distance_L = [0] 
        self.distance_R = [0] 
        self.distance_C = [0]
        self.speed_L = 0 
        self.speed_R = 0
        self.beta = 0
        self.beta_tot = 0
        self.pulsecount_L_tot = 0
        self.pulsecount_R_tot = 0
        
    def ROV_reset(self):
        self.index = 0
        self.distance_L = [0] 
        self.distance_R = [0] 
        self.distance_C = [0]
        self.speed_L = 0 
        self.speed_R = 0
        self.beta = 0
        self.beta_tot = 0
        self.pulsecount_L_tot = 0
        self.pulsecount_R_tot = 0
        





#----------------------------------------------------------------------------------------------------------------------------------------------



#Informasjon fra Leap Motion Controller sendes inn her
#Frame interrupten skjer hver gang det mottas en frame og det er derfor lurt å bruke denne som main fordi den kjører hver gang det mottas ny innformansjon
class SampleListener(Leap.Listener):
    
    def __init__(self):
        super().__init__()
        self.origon_x = 0
        self.origon_y = 0
        self.firsthand = 0
        self.firsthand_forward = 0
        self.firsthand_sideways = 0
        self.firsthand_pinch = 0
        self.secondhand = 0
        self.secondhand_forward = 0
        self.secondhand_sideways = 0
        self.secondhand_pinch = 0
        

    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']

    #Kjører når objektet startes
    def on_init(self, controller):
        print ('Leap init')
        hmi.leap_connected = FALSE
        hmi.leapstatus_text.configure(text = "Leap is disconnected :O")

    #Kjører hver gang Leap Motion Controller kobles til
    def on_connect(self, controller):
        print ('Leap connect')
        hmi.leap_connected = TRUE
        hmi.leapstatus_text.configure(text = "Leap is connected! :D")        
        hmi.connecterror_text.configure(text =" ")
        HMI.controller_button_event(hmi)

    
    #Kjører hver gang Leap Motion Controller kobles fra
    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print ('Leap disconnect')
        HMI.settings_button_event(hmi)
        hmi.leap_connected = FALSE
        hmi.leapstatus_text.configure(text = "Leap is disconnected :O")
        

    #Kjører hver når objektet avsluttes
    def on_exit(self, controller):
        print ('Leap exit')



    def ROV_drive(self, left_number, right_number):
        # Sending speed from 0-200 to xbee and drawing coresporonding arrows.
        left_control = struct.pack("B", int(left_number))
        right_control = struct.pack("B", int(right_number))
        ser.write(start + left_control + right_control)
        HMI.Draw_arrows_movement(hmi,left_number,right_number)
        






    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()


        #Checking and updating screensize
        hmi.controller_frame.update()
        if ((hmi.frame_width != hmi.controller_frame.winfo_width()) | (hmi.frame_height != hmi.controller_frame.winfo_height())):
            hmi.controller_frame_forget()
            hmi.controller_frame_init()
            # print(hmi.coords_unit)
        
        
        # TAR IMOT SERIALDATA
        # while(ser.in_waiting > 0):#ser.in_waiting > 0
        #     read_data = ser.read(1)
        #     # read_data = "b'<'"
        #     if(str(read_data) == "b'<'"):
        #         # print(read_data)
                
        #         speed_L = ser.read(1)
        #         if (str(speed_L) == "b''"):
        #             speed_L = 0
        #         else:
        #             speed_L = int(speed_L.hex(),16)
                    
        #         speed_R = ser.read(1)
        #         if (str(speed_R) == "b''"):
        #             speed_R = 0
        #         else:
        #             speed_R = int(speed_R.hex(),16)
                
        #         pulsecount_L = ser.read(1)
        #         if (str(pulsecount_L) == "b''"):
        #             pulsecount_L = 0
        #         else:
        #             pulsecount_L = int(pulsecount_L.hex(),16)
                
        #         pulsecount_R = ser.read(1)
        #         if (str(pulsecount_R) == "b''"):
        #             pulsecount_R = 0
        #         else:
        #             pulsecount_R = int(pulsecount_R.hex(),16)
                
        #         # rov.pulsecount_L_tot = rov.pulsecount_L_tot + pulsecount_L
        #         # rov.pulsecount_R_tot = rov.pulsecount_R_tot + pulsecount_R
                
        #         #endrer negative tall fra int8 til float
        #         if (pulsecount_L > 127): pulsecount_L = pulsecount_L-255
        #         # print("L" + str(pulsecount_L))
        #         if (pulsecount_R > 127): pulsecount_R = pulsecount_R-255
        #         # print(pulsecount_R)
                    
                    
        #         # print("Left pulsecount = " + str(pulsecount_L))
        #         # print("Right pulsecount = " + str(pulsecount_R))
                
                

        #         if(speed_L != 0): speed_L = (2*0.000575)/(speed_L*(0.0000005*256))
        #         # else: Do nothing, speed should be 0   
        #         if(speed_R != 0): speed_R = (2*0.000575)/(speed_R*(0.0000005*256))
        #         # else: Do nothing, speed should be 0


        #         # pulsecount_L = 2
        #         # pulsecount_R = 3
                

        #         if(pulsecount_L != 0 | pulsecount_R != 0):
        #           # Saving to vector if one of the speed is not null.
        #             rov.index = rov.index + 1
        #             # distance_L = pulsecount_L * math # Do math for distance
        #             # distance_R = pulsecount_R * math # Do math for distance
        #             distance_L = pulsecount_L*0.0005627161
        #             distance_R = pulsecount_R*0.0005627161
        #             distance_C = 0

                    
                    
        #             if(distance_L < distance_R): # Turning left
        #                 rov.beta = - np.arctan((distance_R-distance_L)/(np.sqrt(rov.width**2-((distance_R-distance_L)/2)**2)*2))*2*1.3
        #                 rov.beta_tot = rov.beta_tot + rov.beta
        #                 distance_C = (distance_R+distance_L)/2

        #                 HMI.Rotate_CompassArrow(hmi)

                        
                        
        #             elif(distance_L > distance_R): # Turning right
        #                 rov.beta = np.arctan((distance_L-distance_R)/(np.sqrt(rov.width**2-((distance_L-distance_R)/2)**2)*2))*2*1.3
        #                 rov.beta_tot = rov.beta_tot + rov.beta
        #                 distance_C = (distance_L+distance_R)/2

        #                 HMI.Rotate_CompassArrow(hmi)
                    

        #             else:
        #                 rov.beta = 0
        #                 distance_C = (distance_L+distance_R)/2
                        
        #             #print(rov.index)
        #             hmi.drawline_x.append(hmi.drawline_x[rov.index-1] + hmi.coords_unit*10*distance_C*np.sin(rov.beta_tot)) 
        #             hmi.drawline_y.append(hmi.drawline_y[rov.index-1] - hmi.coords_unit*10*distance_C*np.cos(rov.beta_tot))
        #             hmi.drawline.append(hmi.canvas.create_line(hmi.drawline_x[rov.index-1], hmi.drawline_y[rov.index-1], hmi.drawline_x[rov.index], hmi.drawline_y[rov.index]))
                        

        #             rov.distance_L.append(distance_L)
        #             rov.distance_R.append(distance_R)



        #         else:
        #             # Do not save to vector
        #             #rov.beta = 0
        #             i=0
                

            
            
            #     # print("IF-test")
            #     # print("SpeedL = " + str(speed_L))
            #     # print("SpeedR = " + str(speed_R))
            #     speed_total = (speed_L + speed_R) / 2                    
            #     hmi.canvas.itemconfig(hmi.map_speed, text=("Speed: " + str(int(speed_total*100)) + " cm/s"))

            # #Henger den seg opp? Fjern else før innlevering av koden
            # else:
            #     if(str(read_data) != "b'\\x01'"):
            #         print(read_data)





        # Get hands
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"
            
            if (handType == hmi.first_hand):
                self.firsthand = True
                self.firsthand_forward = int(hand.palm_position.z * hmi.sensitivity_factor)
                self.firsthand_sideways = int(hand.palm_position.x * hmi.sensitivity_factor)
                self.firsthand_pinch = int(hand.pinch_distance)

            elif(handType == hmi.second_hand):
                self.secondhand = True
                self.secondhand_forward = int(hand.palm_position.z*4 * hmi.sensitivity_factor)
                self.secondhand_sideways = int(hand.palm_position.x*4 * hmi.sensitivity_factor)
                self.secondhand_pinch = int(hand.pinch_distance)


        #Starter med firsthand
        if (self.firsthand):
            
            if((self.firsthand_pinch > 25) & (self.secondhand)):#& (self.secondhand)

                if(hmi.use_secondhand):
                    hmi.sensitivity = self.secondhand_pinch
                    hmi.sensitivity_factor = hmi.sensitivity / 50
                    hmi.canvas.itemconfig(hmi.secondhand_sensitivity_text, text=("Sensitivity: " + str(hmi.sensitivity) + "%"))
                    # hmi.secondhand_sensitivity_text.configure(text=("JA  " + str(hmi.sensitivity))
                else:
                    hmi.canvas.itemconfig(hmi.secondhand_sensitivity_text, text=" ")


                firsthand_forward = self.firsthand_forward - self.origon_y
                firsthand_sideways = self.firsthand_sideways - self.origon_x

                HMI.Draw_firsthand_movement(hmi,firsthand_sideways, firsthand_forward)
                hmi.canvas.itemconfig(hmi.firsthand_text,  text=( hmi.first_hand[0] + ": X = " + str(firsthand_sideways) + " Y = " + str(firsthand_forward) + " Pinch = " + str(self.firsthand_pinch)))


                firsthand_forward = int((self.firsthand_forward-self.origon_y)*(-1)+100)
                firsthand_sideways = int((self.firsthand_sideways-self.origon_x)*0.5)

                left_number = firsthand_forward + firsthand_sideways
                if(left_number < 0):
                    left_number = 0
                elif(left_number > 200):
                    left_number = 200

                right_number = firsthand_forward - firsthand_sideways
                if(right_number < 0):
                    right_number = 0
                elif(right_number > 200):
                    right_number = 200

                self.ROV_drive(left_number, right_number)
                
 

            elif(self.firsthand_pinch > 25):
                firsthand_forward = self.firsthand_forward - self.origon_y
                firsthand_sideways = self.firsthand_sideways - self.origon_x

                HMI.Draw_firsthand_movement(hmi,firsthand_sideways, firsthand_forward)
                hmi.canvas.itemconfig(hmi.firsthand_text,  text=( hmi.first_hand[0] + ": X = " + str(firsthand_sideways) + " Y = " + str(firsthand_forward) + " Pinch = " + str(self.firsthand_pinch)))
                hmi.canvas.itemconfig(hmi.secondhand_sensitivity_text, text=("Place both hands inside the sensor to start the controller"))

                self.ROV_drive(100, 100)

                

            else:
                hmi.canvas.itemconfig(hmi.firsthand_text, text=(hmi.first_hand + " detected but closed"))

                self.origon_x = self.firsthand_sideways
                self.origon_y = self.firsthand_forward               
                HMI.Draw_firsthand_movement(hmi, 0, 0)

                self.ROV_drive(100, 100)

                # if(self.secondhand):
                #     hmi.canvas.itemconfig(hmi.secondhand_sensitivity_text, text=("Open " + self.firsthand.lower() + " to start the controller"))
                # else:
                #     hmi.canvas.itemconfig(hmi.secondhand_sensitivity_text, text=("Place both hands inside the sensor to start the controller"))



        else: 
            self.ROV_drive(100, 100)
            HMI.Draw_firsthand_movement(hmi,0, 0)
            
            # Skriver til header at hånden ikke er funnet
            hmi.canvas.itemconfig(hmi.firsthand_text, text=(hmi.first_hand + " not detected"))
            hmi.canvas.itemconfig(hmi.secondhand_sensitivity_text, text=("Place both hands inside the sensor to start the controller"))
            
      
      
        #Fortsetter med second hand
        if (self.secondhand):
            
            HMI.Draw_secondhand_movement(hmi, self.secondhand_sideways, self.secondhand_forward)
            hmi.canvas.itemconfig(hmi.secondhand_text, text=(hmi.second_hand[0] + ": X = " + str(self.secondhand_sideways)) + " Y = " + str(self.secondhand_forward) + " Pinch = " + str(self.secondhand_pinch))

        else:
            hmi.canvas.itemconfig(hmi.secondhand_text, text=(hmi.second_hand + " not detected"))
            hmi.canvas.itemconfig(hmi.secondhand_sensitivity_text, text=("Place both hands inside the sensor to start the controller"))

            HMI.Draw_secondhand_movement(hmi, 0,0)
            # hmi.canvas.delete(hmi.secondhand_pointer)
            # hmi.canvas.delete(hmi.secondhand_pointer_base)

            

        if (frame.hands.is_empty):
            self.ROV_drive(100, 100)

            HMI.Draw_firsthand_movement(hmi, 0, 0)
            HMI.Draw_secondhand_movement(hmi, 0, 0)

            hmi.canvas.itemconfig(hmi.secondhand_sensitivity_text, text=("Place both hands inside the sensor to start the controller"))


            
        # Må vi ha denne if-testen?
        # if not frame.hands.is_empty:
        #     pass
        
        self.firsthand = False
        self.secondhand = False

def Test():
    left_control = struct.pack("B", int(100))
    right_control = struct.pack("B", int(100))
    ser.write(start + left_control + right_control)
    time.sleep(0.003)
    while(ser.in_waiting > 0):
        read_data = str(ser.read(1))
        # read_data = "b'<'"
        if((read_data[2] == "<")):
            speed_L = int(ser.read(1).hex(),16)
            speed_R = int(ser.read(1).hex(),16)
            
            pulsecount_L = int(ser.read(1).hex(),16)
            pulsecount_R = int(ser.read(1).hex(),16)
    
    while((rov.pulsecount_L_tot < 10) and (rov.pulsecount_R_tot < 10)):
        left_control = struct.pack("B", int(100))
        right_control = struct.pack("B", int(150))
        ser.write(start + left_control + right_control)
        time.sleep(0.01)
        while(ser.in_waiting > 0):
            read_data = str(ser.read(1))
            # read_data = "b'<'"
            if((read_data[2] == "<")):
                speed_L = int(ser.read(1).hex(),16)
                speed_R = int(ser.read(1).hex(),16)
                
                try:
                    read_L = ser.read(1)
                    # print(read_L)
                    Hex_L = read_L.hex()
                    pulsecount_L = int(Hex_L,16)
                    if(pulsecount_L > 30):
                        pulsecount_L = 0
                    rov.pulsecount_L_tot = rov.pulsecount_L_tot + pulsecount_L
                except:
                    pulsecount_L = 0    
                
                
                try:
                    read_R = ser.read(1)
                    # print(read_R)
                    Hex_R = read_R.hex()
                    pulsecount_R = int(Hex_R,16)
                    if(pulsecount_R > 30):
                        pulsecount_R = 0
                    rov.pulsecount_R_tot = rov.pulsecount_R_tot + pulsecount_R
                except:
                    pulsecount_R = 0
    while(TRUE):
        left_control = struct.pack("B", int(100))
        right_control = struct.pack("B", int(100))
        ser.write(start + left_control + right_control)
        print("L: " + str(rov.pulsecount_L_tot))
        print("R: " + str(rov.pulsecount_R_tot))
        time.sleep(0.003)
        while(ser.in_waiting > 0):
            read_data = str(ser.read(1))
            # print(read_data)
            # read_data = "b'<'"
            if((read_data[2] == "<")):
                speed_L = int(ser.read(1).hex(),16)
                # print(speed_L)
                speed_R = int(ser.read(1).hex(),16)
                # print(speed_R)
                
                try:
                    read_L = ser.read(1)
                    # print(read_L)
                    Hex_L = read_L.hex()
                    pulsecount_L = int(Hex_L,16)
                    if(pulsecount_L > 30):
                        pulsecount_L = 0
                    rov.pulsecount_L_tot = rov.pulsecount_L_tot + pulsecount_L
                except:
                    pulsecount_L = 0    
                
                
                try:
                    read_R = ser.read(1)
                    # print(read_R)
                    Hex_R = read_R.hex()
                    pulsecount_R = int(Hex_R,16)
                    if(pulsecount_R > 30):
                        pulsecount_R = 0
                    rov.pulsecount_R_tot = rov.pulsecount_R_tot + pulsecount_R
                except:
                    pulsecount_R = 0
    
        

def main():
    
    global rov
    rov = ROV() 
    global hmi
    hmi = HMI()
    
    # Create a sample listener and controller
    listener = SampleListener()
    leap_controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    leap_controller.add_listener(listener)
    
    hmi.mainloop()
    
    # Remove the sample listener when done
    leap_controller.remove_listener(listener)

if __name__ == "__main__":
    main()

