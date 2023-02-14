################################################################################
# Copyright (C) 2012-2016 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

import Leap, sys, time
import serial
import math
from tkinter import *
import customtkinter
import numpy as np
import struct



#ser = serial.Serial('COM12', 9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout = 1)

class HMI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #Deklarerer varriabler
        self.coords_unit = 50
        self.controller_enable = FALSE
        

        #Instillinger for HMI
        self.title("Hands-off ROV")

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
        self.first_hand = "Right hand"
        self.second_hand = "Left hand"

        self.left_hand_button = customtkinter.CTkButton(self.settings_frame, text = "Left hand", command = self.left_hand_event)
        self.left_hand_button.grid(row=2, column=0, padx=10, pady=0)
        
        self.right_hand_button = customtkinter.CTkButton(self.settings_frame, text = "Right hand", command = self.right_hand_event)
        self.right_hand_button.grid(row=2, column=1, padx=10, pady=0)

        self.hand_label = customtkinter.CTkLabel(self.settings_frame, text = "Right hand chosen as steering hand")
        self.hand_label.grid(row = 3, column = 0, columnspan = 2, padx = 20, pady = 0)

        #Slider and label:
        self.sensitivity_slider = customtkinter.CTkSlider(self.settings_frame, from_ = 0, to = 100, command = self.slider_value)
        self.sensitivity_slider.grid(row=4, column=0, columnspan = 2, padx=20, pady=0)
        self.sensitivity_label = customtkinter.CTkLabel(self.settings_frame, text="Sensitivity: 50%")
        self.sensitivity_label.grid(row = 5, column = 0, columnspan = 2, padx=20, pady=0)





        #Controller frame design
        self.canvas = customtkinter.CTkCanvas(self.controller_frame, bg='#EEE')
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.settings_button = customtkinter.CTkButton(self.canvas, text = "settings", command = self.settings_button_event)
        self.resize_button = customtkinter.CTkButton(self.canvas, text = "Resize", command = self.resize_button_event)



        # Bind the movement to the key press event
        self.bind("<Key>", self.on_keypress)

        #start on controller page
        self.select_frame_by_name("controller")

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
        self.sensitivity_label.configure(text = ("Sensitivity: " + str(int(value)) + "%"))




    #Tegner ellementene i emnulatoren ved oppstart
    def Draw_canvas_elements(self,senter_x,senter_y):


        self.car_wheel1 = self.canvas.create_aa_circle(
            senter_x + self.coords_unit, senter_y-self.coords_unit, int(self.coords_unit/3), fill = "black"
        )
        self.car_wheel2 = self.canvas.create_aa_circle(
            senter_x - self.coords_unit, senter_y-self.coords_unit, int(self.coords_unit/3), fill = "black"
        )
        self.car_wheel3 = self.canvas.create_aa_circle(
            senter_x - self.coords_unit, senter_y+self.coords_unit, int(self.coords_unit/3), fill = "black"
        )
        self.car_wheel4 = self.canvas.create_aa_circle(
            senter_x + self.coords_unit, senter_y+self.coords_unit, int(self.coords_unit/3), fill = "black"
        )

        self.car = self.canvas.create_rectangle(
            senter_x-self.coords_unit, senter_y-self.coords_unit, 
            senter_x+self.coords_unit, senter_y+self.coords_unit, 
            fill="blue", outline="blue")

        self.car_front = self.canvas.create_oval(
            senter_x-self.coords_unit, senter_y-self.coords_unit*2 , 
            senter_x+self.coords_unit, senter_y+self.coords_unit*0, 
            fill = "blue", outline="blue")

        self.car_back = self.canvas.create_oval(
            senter_x-self.coords_unit, senter_y-self.coords_unit*0 , 
            senter_x+self.coords_unit, senter_y+self.coords_unit*2, 
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
        
        self.controller_text = self.canvas.create_text(senter_x, self.coords_unit, text = "Hands-off ROV, Overskrift", font = ('Times 25 bold'))
        self.settings_button.place(x=0, y=0)
        self.resize_button.place(x=0, y=30)
        
        
        #Definerer pointer
        self.hand_pointer_base = self.canvas.create_aa_circle(
            senter_x, senter_y, int(self.coords_unit/3), fill = "white"
        )
        self.hand_pointer = self.canvas.create_aa_circle(
            senter_x, senter_y, int(self.coords_unit/4), fill = "black"
        )

        
    #endrer pilen fremmover
    def Draw_hand_movement(self,x_value, y_value):
        if (self.controller_enable):
            self.controller_frame.update()
            senter_x = (self.controller_frame.winfo_width())/2
            senter_y = (self.controller_frame.winfo_height())/2

            self.canvas.coords(self.hand_pointer_base, senter_x+x_value, senter_y+y_value)
            self.canvas.coords(self.hand_pointer, senter_x+x_value, senter_y+y_value)


    def Draw_arrows_movement(self, length_left, length_right):
        length_left = (length_left -100) * self.coords_unit/20
        length_right = (length_right -100) * self.coords_unit/20

        self.controller_frame.update()
        senter_x = (self.controller_frame.winfo_width())/2
        senter_y = (self.controller_frame.winfo_height())/2

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

        # show selected frame
        if name == "settings":
            self.settings_frame.grid(row=0, column=0, sticky=N)
        else:
            self.settings_frame.grid_forget()
        if name == "controller":
            self.controller_frame_init()
        else:
            self.controller_frame_forget()

    #Sletter alle ellemntene i emmulateron når fanen lukkes
    def controller_frame_forget(self):
        self.controller_enable = FALSE
        self.controller_frame.grid_forget()

        #Deleting the car:
        self.canvas.delete(self.car)
        self.canvas.delete(self.car_wheel1)
        self.canvas.delete(self.car_wheel2)
        self.canvas.delete(self.car_wheel3)
        self.canvas.delete(self.car_wheel4)
        self.canvas.delete(self.car_front)
        self.canvas.delete(self.car_back)
        
        # Piler og info
        self.canvas.delete(self.controller_text)
        self.canvas.delete(self.arrow_left)
        self.canvas.delete(self.arrow_right)
        self.canvas.delete(self.left_stop)
        self.canvas.delete(self.right_stop)

        # musepeker
        self.canvas.delete(self.hand_pointer)
        self.canvas.delete(self.hand_pointer_base)
    
    #Tegner alle elementene i emmulatoren når fanen åpnes
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

    #Når hjem knappen i menyen trykkes
    def settings_button_event(self):
        self.select_frame_by_name("settings")

    def resize_button_event(self):
        self.controller_frame_forget()
        self.controller_frame_init()
    #Når controller knappen i menyen trykkes
    def controller_button_event(self):
        self.select_frame_by_name("controller")
    #Når det endres valg i nedtreksmenyen
    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)



#----------------------------------------------------------------------------------------------------------------------------------------------



#Informasjon fra Leap Motion Controller sendes inn her
#Frame interrupten skjer hver gang det mottas en frame og det er derfor lurt å bruke denne som main fordi den kjører hver gang det mottas ny innformansjon
class SampleListener(Leap.Listener):

    def __init__(self):
        super().__init__()
        self.origon_x = 0
        self.origon_y = 0

    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']

    #Kjører når objektet startes
    def on_init(self, controller):
        print ('Leap init')

    #Kjører hver gang Leap Motion Controller kobles til
    def on_connect(self, controller):
        # hmi.controller_info.configure(text = "Leap connected")
        print ('Leap connect')
    
    #Kjører hver gang Leap Motion Controller kobles fra
    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        # hmi.controller_info.configure(text = "Not connected")
        print ('Leap disconnect')

    #Kjører hver når objektet avsluttes
    def on_exit(self, controller):
        print ('Leap exit')
        print(hmi.first_hand)

    def on_frame(self, controller):
        
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        

        start = ("<").encode()
        stop = (">").encode()


# Kommenterer ut fra her for å endre og se:

        # Get hands
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"

            if ((handType == hmi.first_hand) & (hand.pinch_distance > 25)):
                
                forward = math.floor((hand.palm_position.z-self.origon_y))
                sideways = math.floor((hand.palm_position.x-self.origon_x))
                HMI.Draw_hand_movement(hmi,sideways, forward)
                
                hmi.canvas.itemconfig(hmi.controller_text, text="Leap connected X = " + str(sideways) + " Y = " + str(forward) + " Pinch = " + str(hand.pinch_distance))

                forward = math.floor((hand.palm_position.z-self.origon_y)*(-1)+100)
                sideways = math.floor((hand.palm_position.x-self.origon_x)*0.5)


                left_number = forward+sideways

                if(left_number < 0):
                    left_number = 0
                elif(left_number > 200):
                    left_number = 200

                right_number = forward-sideways

                if(right_number<0):
                    right_number = 0
                elif(right_number > 200):
                    right_number = 200

                left_control = struct.pack("B", math.floor(left_number))
                right_control = struct.pack("B", math.floor(right_number))
                #ser.write(start + left_control + right_control + stop)#pwm signal til motoren er per nå kunn fremover og fra 0 til 254 på hver motor. motorene begynner ikke å kjøre før nermere 100 på pwm dette må fikses

                HMI.Draw_arrows_movement(hmi,left_number,right_number)

            else:
                self.origon_x = hand.palm_position.x
                self.origon_y = hand.palm_position.z
                left_number = 100
                right_number = 100
                left_control = struct.pack("B", math.floor(left_number))
                right_control = struct.pack("B", math.floor(right_number))
                #ser.write(start + left_control + right_control + stop)
                forward = math.floor((hand.palm_position.z-self.origon_y))
                sideways = math.floor((hand.palm_position.x-self.origon_x))
                HMI.Draw_hand_movement(hmi,sideways, forward)
                HMI.Draw_arrows_movement(hmi,left_number,right_number)
                # hmi.controller_info.configure(text = "Leap connected X = " + str(sideways) + " Y = " + str(forward) + " Pinch = " + str(hand.pinch_distance))


            # Fortsett her på onsdag:
            # if ((handType == hmi.second_hand) & (hand.pinch_distance > 25)):
            #     forward = math.floor((hand.palm_position.z-self.origon_y))
            #     sideways = math.floor((hand.palm_position.x-self.origon_x))
            #     HMI.Draw_hand_movement(hmi, sideways, forward)




        if frame.hands.is_empty:
            left_number = 100
            right_number = 100
            left_control = struct.pack("B", math.floor(left_number))
            right_control = struct.pack("B", math.floor(right_number))
            HMI.Draw_hand_movement(hmi,0, 0)
            HMI.Draw_arrows_movement(hmi,100,100)
            #ser.write(start + left_control + right_control + stop)

        # if not frame.hands.is_empty:
        #     pass




        

def main():
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

