/*
 * ALL.h
 *
 * Created: 11/10/2022 14:24:15
 *  Author: Oyste
 */ 


#ifndef ALL_H_
#define ALL


#define FALSE 0
#define TRUE 1

#define RightMotor PORTC
#define LeftMotor PORTC

#define RightMotorReverse_bm (1<<3)
#define LeftMotorReverse_bm (1<<2)

#define USART_TX_PIN_bm (1<<0)
#define TCA0_CMP_MAX 65535
#define TCA0_CMP_MIN 0


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//TCA

uint16_t u;
uint8_t u_prosent;

uint16_t counter_tcb;
uint8_t counter_tcb_8;

uint8_t hr;

void TCA_Motor_Driver_init();

void TCA_Motor_Driver_Set_Right(uint8_t right);
void TCA_Motor_Driver_Set_Left(uint8_t left);


uint8_t Error_Faktor_L;
uint8_t Error_Faktor_R;

uint32_t y_ref;
uint32_t mesured_speed_32;
uint32_t e;
uint32_t t;
uint32_t e_t;

uint32_t I_L;
uint32_t I_R;

#define kp 4
#define min 200
#define max 46

#define Kp 1
#define Ti 1
#define Ti_2 100


#define Tachometer_min 18757
#define Tachometer_max 1792

//PID values

int32_t u_k_Left;
int32_t u_k1_Left;

int32_t e_k_Left;
int32_t e_k1_Left;

int32_t temp_PID_Left;

uint32_t Speed_Ref_Left;


int32_t u_k_Right;
int32_t u_k1_Right;

int32_t e_k_Right;
int32_t e_k1_Right;

int32_t temp_PID_Right;

int32_t Speed_Ref_Right;


uint32_t PID;
uint16_t PID_16;

int32_t Speed_L;
int32_t Speed_R;


void TCA_Motor_Driver_Set_Right_PID(int32_t y_ref_Left, int32_t y_Left);
void TCA_Motor_Driver_Set_Left_PID(int32_t y_ref_Right, int32_t y_Right);

void TCA_Motor_Driver_kill();

//variables used for primitive transmition off char
#define MESSAGE_LENGTH 4
char message[MESSAGE_LENGTH];
char Character;





/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//TCB

#define Tachometer1 (1<<4)
#define Tachometer2 (1<<5)
#define Tachometer3 (1<<6)
#define Tachometer4 (1<<7)


void TCB_init();
void TCA1_init_TCB_CLOC();

void TCB0_init();
void TCB1_init();
void TCB2_init();
void TCB3_init();




////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//USART

void USART3_init();

uint8_t USART3_receive_char ();
void USART3_receive_aray ();
void USART3_transmit_char(char Character);


#endif /* ALL_H_ */