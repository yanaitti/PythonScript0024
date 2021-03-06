//+------------------------------------------------------------------+
//|                                                 AutoTrade-ml.mq4 |
//|                                       Copyright 2021, LLC Yanyan |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2021, LLC Yanyan"
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include <JAson.mqh>
#include <stdlib.mqh>

// -- input parameters
input int StopLoss = 5;
input int TakeProfit = 5;
input int Buffer = 1;
input double Lot = 0.1;
input int EA_Magic=12345;   // EA Magic Number
input string PREDICT_URL = "https://stg-autotrade-ml.herokuapp.com/v1_1/predict";

// -- other parameters
int STP, TKP;

//+------------------------------------------------------------------+
//| Global variables                                                 |
//+------------------------------------------------------------------+
// 共通
int gPrvBars = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
//---
   STP = StopLoss;
   TKP = TakeProfit;
  
   if(_Digits==5 || _Digits==3){
    STP = STP*10;
    TKP = TKP*10;
   }
//--- create timer
   gPrvBars = iBars(NULL,0);

//---
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
//---
   
  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
//---
   int currentBars = iBars(NULL,0);
   int trade_flg = 0;

   // 新しい足を生成した時ではない場合は、スキップ
   if(currentBars == gPrvBars){
    gPrvBars = currentBars;
    return;
   }
   
   trade_flg = GetWebData();
//   trade_flg = 1;
   int ticket_id = 0;

   if(trade_flg == 1) {
    //--- リクエストの送信
    ticket_id = OrderSend(_Symbol, OP_BUY, Lot, Ask, 20, NormalizeDouble(Ask - STP*_Point,_Digits), NormalizeDouble(Ask + TKP*_Point,_Digits), NULL, EA_Magic, 0, clrRed);
    if(ticket_id == -1){
     int errorcode = GetLastError();
     printf("エラーコード:%d , 詳細:%s ",errorcode , ErrorDescription(errorcode));
    }
    printf("ask: %f, stp: %d, point: %f, digit: %d", Ask, STP, _Point, _Digits);
    printf("sl: %f, tp: %f", NormalizeDouble(Ask - STP*_Point,_Digits), NormalizeDouble(Ask + TKP*_Point,_Digits));
   }else if(trade_flg == 2) {
    //--- リクエストの送信
    ticket_id = OrderSend(_Symbol, OP_SELL, Lot, Bid, 20, NormalizeDouble(Bid + STP*_Point,_Digits), NormalizeDouble(Bid - TKP*_Point,_Digits), NULL, EA_Magic, 0, clrBlue);
    if(ticket_id == -1){
     int errorcode = GetLastError();
     printf("エラーコード:%d , 詳細:%s ",errorcode , ErrorDescription(errorcode));
    }
    printf("ask: %f, stp: %d, point: %f, digit: %d", Ask, STP, _Point, _Digits);
    printf("sl: %f, tp: %f", NormalizeDouble(Ask - STP*_Point,_Digits), NormalizeDouble(Ask + TKP*_Point,_Digits));
   }
   
   gPrvBars = currentBars;
  }
//+------------------------------------------------------------------+
int GetWebData()
  {
   CJAVal jv;

   int WebR; 
   int timeout = 5000;
   string cookie = NULL, headers; 
   char data[], ReceivedData[];
   int shift = 1;

   int time = iTime(Symbol(), Period(), shift); 
   double open = iOpen(Symbol(), Period(), shift); 
   double high = iHigh(Symbol(), Period(), shift); 
   double low = iLow(Symbol(), Period(), shift); 
   double close = iClose(Symbol(), Period(), shift); 

   jv["curr"]=Symbol();
   jv["perd"]="15";
   jv["time"]=time;
   jv["open"]=open;
   jv["high"]=high;
   jv["low"]=low;
   jv["close"]=close;
   
   ArrayResize(data, StringToCharArray(jv.Serialize(), data, 0, WHOLE_ARRAY)-1);

   WebR = WebRequest("POST", PREDICT_URL, "Content-Type: application/json\r\n", timeout, data, ReceivedData, headers );
   if(!WebR) Print("Web request failed");   
   
   string ReceivedText = CharArrayToString(ReceivedData);
   Comment(ReceivedText);
   Comment(close);
   Print(ReceivedText);
   Print("Updated!");
      
   return int(ReceivedText);
  }
