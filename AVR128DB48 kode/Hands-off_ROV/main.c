/*
 * Hands-off_ROV.c
 *
 * Created: 24/01/2023 09:14:24
 * Author : Oyste
 */ 

#include <avr/io.h>
#include <avr/interrupt.h>
#define F_CPU 4000000UL
#include <util/delay.h>
#include <avr/wdt.h>
#include <avr/cpufunc.h>
#include <avr/sleep.h>
#include <string.h>
#include <stdio.h>
#include "ALL.h"

#define testspeed 100


uint16_t counter;
uint8_t message_resieved;
uint8_t message_counter;
uint8_t message_counter_2;

uint8_t counter_Left;
uint8_t counter_Right;


uint8_t Speed_L_tosend;
uint8_t Speed_R_tosend;
uint8_t counter_Left_tosend;
uint8_t counter_Right_tosend;

uint8_t Speed_test;
uint8_t Speed_test_R;
uint8_t Speed_test_L;
uint8_t Speed_test_old;


uint8_t PID_Left_enable = 0;
uint8_t PID_Right_enable = 0;



uint8_t Set_speed_right;



uint8_t Forward_R;
uint8_t Forward_L;
uint8_t counter1;
uint8_t counter2;
uint8_t counter3;
uint8_t Left_Tachometer_1;
uint8_t Left_Tachometer_2;

int main(void)
{
	USART3_init();
	TCA_Motor_Driver_init();
	TCB_init();
	message[0] = '<';
	message[1] = testspeed;
	message[2] = testspeed;
	message[3] = '>';
	
// 	Speed_Ref_Right = 0;
// 	e_k1_Right = 0;
// 	u_k1_Right = 0;
	
	TCA_Motor_Driver_Set_Left(message[1]);
	TCA_Motor_Driver_Set_Right(message[2]);
	
	_delay_ms(500);
	
	PORTC.DIRSET |= (1<<0) | (1<<1) | (1<<2) | (1<<3);
	
	PORTB.DIRSET = (1<<3);
	
	USART3_transmit_char('B');
	
	sei();
	while (1)
	{		
		if (message_counter_2 > 2)
		{
			USART3_transmit_char(1);
			USART3_transmit_char('<');
			USART3_transmit_char(Speed_L_tosend);
			USART3_transmit_char(Speed_R_tosend);
			USART3_transmit_char(counter_Left_tosend);
			USART3_transmit_char(counter_Right_tosend);
			message_counter_2 = 0;
 		}
;
	}
}


//Interupt for å skrive til microchip
ISR(USART3_RXC_vect)
{
	if (message[0] != '<')
	{
		message_counter = 0;
		message_counter_2 = 0;
	}
	if (message_counter < 3)
	{
		message[message_counter] = USART3_receive_char ();
		message_counter = message_counter + 1;
		message_counter_2 = message_counter_2 + 1;
	}
	if (message_counter > 2)
	{
		TCA_Motor_Driver_Set_Left(message[1]);
		TCA_Motor_Driver_Set_Right(message[2]);
		
		Speed_L_tosend = (Speed_L>>8);
		Speed_R_tosend = (Speed_R>>8);
		counter_Left_tosend = counter_Left;
		counter_Right_tosend = counter_Right;
		
// 		Speed_Ref_Right = message[2];
// 		Speed_Ref_Right = Speed_Ref_Right - 100;
// 		Speed_Ref_Right = (Speed_Ref_Right<<16)/10	
	
		counter_Left = 0;
		counter_Right = 0;
		message_counter = 0;
	}
	
	
}



ISR(PORTC_PORT_vect)
{	
	PORTC.INTFLAGS |= Tachometer1 | Tachometer3;
}

//Left motor
ISR(TCB3_INT_vect)
{
	
	if (TCB3.INTFLAGS & TCB_OVF_bm)
	{
		Speed_L = 65535;
		Forward_L = 0;
		TCB3.INTFLAGS = TCB_OVF_bm;
	} else 
	{
		if (PORTC.IN & Tachometer4)
		{
			Forward_L = 1;
			counter_Left = counter_Left+1;
		}else{
			Forward_L = 255;
			counter_Left = counter_Left-1;
		}
		Speed_L = TCB3.CCMP;
		//TCA_Motor_Driver_Set_Left_PID(message[1], Speed_L);
	}
}


//Right motor
ISR(TCB2_INT_vect)
{
	
	if (TCB2.INTFLAGS & TCB_OVF_bm)
	{
		Speed_R = 65535;
		//USART3_transmit_char('O');
		//TCA_Motor_Driver_Set_Right_PID(Speed_Ref_Right, Speed_R);
		Forward_R = 0;
		TCB2.INTFLAGS = TCB_OVF_bm;
	} else
	{
		Speed_R = TCB2.CCMP;
// 		if (Speed_R < 18757){
// 			Speed_R = 18757-Speed_R;
// 			Speed_R = (Speed_R<<16);
// 			Speed_R = Speed_R/16965;
// 		}else{
// 			Speed_R = 0;
// 		}
		
		
		
		if (PORTC.IN & Tachometer2)
		{
			Forward_R = 255;
			Speed_R = -Speed_R;
			counter_Right = counter_Right-1;
		}else{
			Forward_R = 1;
			counter_Right = counter_Right+1;
		}
		//TCA_Motor_Driver_Set_Right_PID(Speed_Ref_Right, Speed_R);
		
	}
	
}
