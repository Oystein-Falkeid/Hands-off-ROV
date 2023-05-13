/*
 * ALL.c
 *
 * Created: 11/10/2022 14:24:36
 *  Author: Oyste
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


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//TCA
void TCA_Motor_Driver_init()
{
	TCA0.SINGLE.PER = TCA0_CMP_MAX;
	TCA0.SINGLE.CMP0 = TCA0_CMP_MIN;
	RightMotor.OUTCLR = LeftMotorReverse_bm;
	TCA0.SINGLE.CMP1 = TCA0_CMP_MIN;
	LeftMotor.OUTCLR = RightMotorReverse_bm;
	
	TCA0.SINGLE.CTRLA = TCA_SINGLE_ENABLE_bm | TCA_SINGLE_CLKSEL_DIV1_gc;
	TCA0.SINGLE.CTRLB = TCA_SINGLE_CMP0EN_bm | TCA_SINGLE_CMP1EN_bm | TCA_SINGLE_WGMODE_SINGLESLOPE_gc;
	
	PORTMUX.TCAROUTEA |= PORTMUX_TCA0_PORTC_gc;
}

void TCA_Motor_Driver_Set_Left( uint8_t left)
{
	if (left > 100)//Fremover
	{
		TCA0.SINGLE.CMP0 = ((left-100)*TCA0_CMP_MAX)/100;
		RightMotor.OUTCLR = LeftMotorReverse_bm;
		
	}
	if (left < 100)//Bakover
	{
		TCA0.SINGLE.CMP0 = ((left-100)*TCA0_CMP_MAX)/100;
		RightMotor.OUTSET = LeftMotorReverse_bm;
	}
	if ( left == 100)//Stop
	{
		TCA0.SINGLE.CMP0 = TCA0_CMP_MIN;
		RightMotor.OUTCLR = LeftMotorReverse_bm;
	}
}

void TCA_Motor_Driver_Set_Right(uint8_t right)
{
	if (right > 100)//Fremover
	{
		TCA0.SINGLE.CMP1 = ((right-100)*TCA0_CMP_MAX)/100;
		RightMotor.OUTCLR = RightMotorReverse_bm;
	}
	if (right < 100)//Bakover
	{
		TCA0.SINGLE.CMP1 = ((right-100)*TCA0_CMP_MAX)/100;
		RightMotor.OUTSET = RightMotorReverse_bm;
	}
	if (right == 100)//Stop
	{
		TCA0.SINGLE.CMP1 = TCA0_CMP_MIN;
		RightMotor.OUTCLR = RightMotorReverse_bm;
	}
}



void TCA_Motor_Driver_Set_Left_PID(int32_t y_ref_Left, int32_t y_Left)
{
	e_k_Left = y_ref_Left - y_Left;

	u_k_Left = u_k1_Left + e_k_Left - e_k1_Left;

	temp_PID_Left = e_k_Left + e_k1_Left;
	temp_PID_Left = temp_PID_Left * y_Left;
	temp_PID_Left = temp_PID_Left / 34000;
	
	u_k_Left = u_k_Left + temp_PID_Left;
	
	if (u_k_Left > TCA0_CMP_MAX)
	{
		u_k_Left = TCA0_CMP_MAX;
	}else if (u_k_Left < -TCA0_CMP_MAX)
	{
		u_k_Left = -TCA0_CMP_MAX;
	}
	
	u_k1_Left = u_k_Left;
	e_k1_Left = e_k_Left;

	if (u_k_Left < 0)
	{
		u_k_Left = -u_k_Left;
		LeftMotor.OUTSET = LeftMotorReverse_bm;
		}else{
		LeftMotor.OUTCLR = LeftMotorReverse_bm;
	}
	
	TCA0.SINGLE.CMP1 = u_k_Left;
}

void TCA_Motor_Driver_Set_Right_PID(int32_t y_ref_Right, int32_t y_Right)
{
	e_k_Right = y_ref_Right +(- y_Right);
	
	u_k_Right = u_k1_Right + e_k_Right - e_k1_Right;

	temp_PID_Right = e_k_Right + e_k1_Right;
	temp_PID_Right = temp_PID_Right * y_Right;
	temp_PID_Right = temp_PID_Right / 34000;
	
	u_k_Right = u_k_Right + temp_PID_Right;
	

	
	u_k1_Right = u_k_Right;
	e_k1_Right = e_k_Right;

	if (u_k_Right < 0)
	{
		u_k_Right = -u_k_Right;
		RightMotor.OUTSET = RightMotorReverse_bm;
		}else{
		RightMotor.OUTCLR = RightMotorReverse_bm;
	}
	
	if (u_k_Right > TCA0_CMP_MAX)
	{
		u_k_Right = TCA0_CMP_MAX;
	}
	
	TCA0.SINGLE.CMP1 = u_k_Right;
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//TCB

void TCB_init()
{
	TCB0_init();
	TCB1_init();
	TCB2_init();
	TCB3_init();
	TCA1_init_TCB_CLOC();
	
}

void TCA1_init_TCB_CLOC()
{
	TCA1.SINGLE.CTRLA = TCA_SINGLE_ENABLE_bm | TCA_SINGLE_CLKSEL_DIV4_gc;
}

void TCB0_init()
{
	//PORTC.PIN6CTRL = PORT_ISC_RISING_gc;
}

void TCB1_init()
{
	//PORTC.PIN5CTRL = PORT_ISC_RISING_gc;
}

void TCB2_init()//right motor
{
	TCB2.CTRLA = TCB_CLKSEL_TCA1_gc | TCB_ENABLE_bm;
	TCB2.CTRLB = TCB_CNTMODE_FRQ_gc;
	TCB2.EVCTRL = TCB_EDGE_bm | TCB_CAPTEI_bm;
	TCB2.INTCTRL = TCB_CAPT_bm | TCB_OVF_bm;
	
	PORTC.PIN4CTRL = PORT_ISC_RISING_gc;
	//PORTC.PIN5CTRL = PORT_ISC_RISING_gc;
	EVSYS.CHANNEL2 = EVSYS_CHANNEL2_PORTC_PIN4_gc;
	EVSYS.USERTCB2CAPT = EVSYS_USER_CHANNEL2_gc;
}

void TCB3_init()//left motor
{
	TCB3.CTRLA = TCB_CLKSEL_TCA1_gc | TCB_ENABLE_bm;
	TCB3.CTRLB = TCB_CNTMODE_FRQ_gc;
	TCB3.EVCTRL = TCB_EDGE_bm | TCB_CAPTEI_bm;
	TCB3.INTCTRL = TCB_CAPT_bm | TCB_OVF_bm;
	
	PORTC.PIN6CTRL = PORT_ISC_RISING_gc;
	//PORTC.PIN7CTRL = PORT_ISC_RISING_gc;
	EVSYS.CHANNEL3 = EVSYS_CHANNEL3_PORTC_PIN6_gc;
	EVSYS.USERTCB3CAPT = EVSYS_USER_CHANNEL3_gc;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//USART
//init to use PortB0 and PortB1 for USART
void USART3_init (){
	USART3.BAUD = 137;
	PORTB.DIR |= USART_TX_PIN_bm;
	USART3.CTRLA |= USART_RXCIE_bm;
	USART3.CTRLB |= USART_TXEN_bm | USART_RXEN_bm;
}

uint8_t USART3_receive_char ()
{
	return USART3.RXDATAL;
}

//receves an aray of char if it begines with "<" and ends with ">" dos not stor "<" or ">"
void USART3_receive_aray ()
{
	message[0] = USART3.RXDATAL;
	if (message[0] == '<')
	{
		for (uint8_t i = 1; i < MESSAGE_LENGTH; i++)
		{
			while(!(USART3.STATUS & USART_RXCIF_bm))
			{
				;
			}
			message[i] = USART3.RXDATAL;
			if (message[i] == '>')
				break;
		}
	}
}

void USART3_transmit_char(char Character){
	while (!(USART3.STATUS & USART_DREIF_bm))
	{
		;
	}
	USART3.TXDATAL = Character;
}


