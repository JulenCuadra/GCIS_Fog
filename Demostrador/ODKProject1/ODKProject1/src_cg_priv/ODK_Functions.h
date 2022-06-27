/*
 * This file is AUTO GENERATED - DO NOT MODIFY this file. 
 * This file contains the function prototypes of ODK 1500S.
 *
 * File created by ODK_CodeGenerator version 205.100.101.18
 * at Thu June 23 11:59:42 2022 
*/

#if !defined ODK_Functions_H
#define ODK_Functions_H

#include "ODK_Types.h"

#ifdef DLL_EXPORT
  #define EXPORT_API extern "C" __declspec(dllexport)
#else
  #define EXPORT_API extern "C"
#endif

// Basic function in order to show 
// how to create a function in ODK 1500S.
ODK_RESULT Publish (
  /*IN*/const ODK_S7STRING message[256]);
#define _ODK_FUNCTION_PUBLISH  ODK_RESULT Publish (/*IN*/const ODK_S7STRING message[256])

ODK_RESULT CheckSubscriptions (
  /*OUT*/ODK_S7STRING app2PLCtopic[256],
  /*OUT*/ODK_INT8& app2PLCtopicLen,
  /*OUT*/ODK_S7STRING app2PLCmsg[256],
  /*OUT*/ODK_INT8& app2PLCmsgLen,
  /*INOUT*/ODK_BOOL& flag);
#define _ODK_FUNCTION_CHECKSUBSCRIPTIONS  ODK_RESULT CheckSubscriptions (/*OUT*/ODK_S7STRING app2PLCtopic[256], /*OUT*/ODK_INT8& app2PLCtopicLen, /*OUT*/ODK_S7STRING app2PLCmsg[256], /*OUT*/ODK_INT8& app2PLCmsgLen, /*INOUT*/ODK_BOOL& flag)

ODK_RESULT ReadFabPlan (
  /*OUT*/control_flags& flags,
  /*OUT*/fog2plc& data_out);
#define _ODK_FUNCTION_READFABPLAN  ODK_RESULT ReadFabPlan (/*OUT*/control_flags& flags, /*OUT*/fog2plc& data_out)

ODK_RESULT GetTrace (
  /*IN*/const ODK_INT16& TraceCount,
  /*OUT*/ODK_S7STRING TraceBuffer[256][127]);
#define _ODK_FUNCTION_GETTRACE  ODK_RESULT GetTrace (/*IN*/const ODK_INT16& TraceCount, /*OUT*/ODK_S7STRING TraceBuffer[256][127])

#endif