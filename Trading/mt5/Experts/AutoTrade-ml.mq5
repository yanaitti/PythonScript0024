//+------------------------------------------------------------------+
//|                                                  AutoTradeML.mq5 |
//|                                      Copyright 2021, LLC Yanyan. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2021, LLC Yanyan."
#property link      "https://www.mql5.com"
#property version   "1.03"

#include <JAson.mqh>

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
//--- destroy timer
   EventKillTimer();
   
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
//   trade_flg = true;
   
  //--- リクエストと結果の宣言と初期化
  MqlTick latest_price;
  MqlTradeRequest request={0};
  MqlTradeResult  result={0};
     
  //--- Get the last price quote using the MQL5 MqlTick Structure
  if(!SymbolInfoTick(_Symbol,latest_price))
  {
   Alert("Error getting the latest price quote - error:",GetLastError(),"!!");
   return;
  }

   if(trade_flg == 1) {

   //--- リクエストのパラメータ
//      price = SymbolInfoDouble(Symbol(),SYMBOL_ASK)*point;
      request.action   = TRADE_ACTION_DEAL;                     //　取引操作タイプ
      request.symbol   = _Symbol;                             // シンボル
      request.volume   = Lot;                                   // 0.1ロットのボリューム
      request.type     = ORDER_TYPE_BUY;                       // 注文タイプ
      request.price    = NormalizeDouble(latest_price.ask, _Digits); // 発注価格
      request.magic    = EA_Magic;                         // 注文のMagicNumber
      request.sl       = NormalizeDouble(latest_price.ask - STP*_Point,_Digits);
      request.tp       = NormalizeDouble(latest_price.ask + TKP*_Point,_Digits);
      request.type_filling = ORDER_FILLING_FOK;
      request.deviation = 100;
   //--- リクエストの送信
      if(!OrderSend(request,result))
         PrintFormat("OrderSend error %d",GetLastError());     // リクエストの送信が失敗した場合、エラーコードを出力する
   //--- 操作に関する情報
      PrintFormat("retcode=%u  deal=%I64u  order=%I64u",result.retcode,result.deal,result.order);   
   }else if(trade_flg == 2) {
   //--- リクエストのパラメータ
//      price = SymbolInfoDouble(Symbol(),SYMBOL_ASK)*point;
      request.action   = TRADE_ACTION_DEAL;                     //　取引操作タイプ
      request.symbol   = _Symbol;                             // シンボル
      request.volume   = Lot;                                   // 0.1ロットのボリューム
      request.type     = ORDER_TYPE_SELL;                       // 注文タイプ
      request.price    = NormalizeDouble(latest_price.bid, _Digits); // 発注価格
      request.magic    = EA_Magic;                         // 注文のMagicNumber
      request.sl       = NormalizeDouble(latest_price.bid + STP*_Point,_Digits);
      request.tp       = NormalizeDouble(latest_price.bid - TKP*_Point,_Digits);
      request.type_filling = ORDER_FILLING_FOK;
      request.deviation = 100;
   //--- リクエストの送信
      if(!OrderSend(request,result))
         PrintFormat("OrderSend error %d",GetLastError());     // リクエストの送信が失敗した場合、エラーコードを出力する
   //--- 操作に関する情報
      PrintFormat("retcode=%u  deal=%I64u  order=%I64u",result.retcode,result.deal,result.order);   
   }
   
   gPrvBars = currentBars;
  }
//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
  {
//---
   
  }
//+------------------------------------------------------------------+
// string URL = "https://stg-autotrade-ml.herokuapp.com/predict";
 
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
   Print(ReceivedText);
   Print("Updated!");
   
   return int(ReceivedText);
}