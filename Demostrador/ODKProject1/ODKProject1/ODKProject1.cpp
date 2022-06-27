#include "stdafx.h"
#include "ODK_Functions.h"
#include "tchar.h"

#include <string>

#include "include/MQTTClient.h"

#include "ODK_StringHelper.h"

#include "nlohmann/json.hpp"
using json = nlohmann::json;

#define QOS 0

MQTTClient client;
volatile MQTTClient_deliveryToken deliveredtoken;

bool rcvdFlag;
char* rcvdTopic;
int rcvdTopicLen;
char* rcvdMessage;
int rcvdMessageLen;

/*
control_flags rcvdFlags;
fog2plc rcvdPlan;
*/



void connlost(void* context, char* cause)
{
    ODK_TRACE("Connection lost!");
}

int msgarrvd(void* context, char* topicName, int topicLen, MQTTClient_message* message)
{
    ODK_TRACE("msgarrvd: %s (%d) %s (%d)", topicName, topicLen, message->payload, message->payloadlen);

    rcvdFlag = 1;
    rcvdTopic = topicName;
    rcvdTopicLen = topicLen;
    rcvdMessage = (char*)message->payload;
    rcvdMessageLen = message->payloadlen;

    MQTTClient_freeMessage(&message);
    MQTTClient_free(topicName);

    return 1;
}

void delivered(void* context, MQTTClient_deliveryToken dt)
{
    ODK_TRACE("Msg published!");
    deliveredtoken = dt;
}


/*
 * OnLoad() is invoked after the application binary was loaded.
 * @return ODK_SUCCESS       notify, that no error occurs
 *                            - OnRun() will be invoked automatically
 *         any other value   notify, that an error occurs (user defined)
 *                            - OnUnload() will be invoked automatically
 *                            - ODK application will be unloaded automatically
 */
EXPORT_API ODK_RESULT OnLoad(void)
{
    ODK_TRACE("Entrando en OnLoad...");
    // place your code here

    char SERVER_ADDRESS[256] = "192.168.1.1:31883";
    char CLIENT_ID[256] = "ODK_app";
    char TOPICtoMachine[256] = "Machine/to";

    MQTTClient_create(&client, SERVER_ADDRESS, CLIENT_ID, MQTTCLIENT_PERSISTENCE_NONE, NULL);
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    conn_opts.keepAliveInterval = 20;
    conn_opts.cleansession = 1;

    MQTTClient_setCallbacks(client, NULL, connlost, msgarrvd, delivered);

    conn_opts.username = "admin";
    //conn_opts.password = "admin";
    conn_opts.password = "mosquittoGCIS";
    
    int rc;
    if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS) {
        ODK_TRACE("Error connecting to the broker!");
        return ODK_SUCCESS;
    }
    
    ODK_TRACE("Connected to the broker!");

    rcvdFlag = 0;
    MQTTClient_subscribe(client, TOPICtoMachine, QOS);
    ODK_TRACE("Subscribed to topic %s", TOPICtoMachine);

    return ODK_SUCCESS;
}

/*
 * OnUnload() is invoked before the application binary is unloaded or when
 *            ODK-Host terminates.
 * @return ODK_SUCCESS       notify, that no error occurs
 *         any other value   notify, that an error occurs (user defined)
 *                            - ODK application will be unloaded anyway
 */
EXPORT_API ODK_RESULT OnUnload(void)
{
    // place your code here
    return ODK_SUCCESS;
}

/*
 * OnRun() is invoked when the CPU transitions to the RUN state and
 *         after OnLoad().
 * @return Does not affect the load operation or state transition.
 */
EXPORT_API ODK_RESULT OnRun(void)
{
    // place your code here
    return ODK_SUCCESS;
}

/*
 * OnStop() is invoked when the CPU transitions to the STOP/SHUTDOWN state
 *          or before unloading the ODK application.
 * @return Does not affect the load operation or state transition.
 */
EXPORT_API ODK_RESULT OnStop(void)
{
    // place your code here
    return ODK_SUCCESS;
}

ODK_RESULT Publish(/*IN*/ const ODK_S7STRING message[256])
{
    // place your code here

    char payload[256];
    Convert_S7STRING_to_SZSTR(message, payload, 256);

    char TOPICfromMachine[256] = "Machine/from";

    MQTTClient_message pubmsg = MQTTClient_message_initializer;
    MQTTClient_deliveryToken token;

    pubmsg.payload = payload;
    pubmsg.payloadlen = strlen(payload);
    pubmsg.qos = QOS;
    pubmsg.retained = 0;
    deliveredtoken = 0;
    MQTTClient_publishMessage(client, TOPICfromMachine, &pubmsg, &token);
    MQTTClient_waitForCompletion(client, token, 1000L);

    ODK_TRACE("Publishing data: %s", payload);

    return ODK_SUCCESS;
}

ODK_RESULT CheckSubscriptions(/*OUT*/ ODK_S7STRING app2PLCtopic[256], /*OUT*/ ODK_INT8& app2PLCtopicLen,
                              /*OUT*/ ODK_S7STRING app2PLCmsg[256], /*OUT*/ ODK_INT8& app2PLCmsgLen,
                              /*INOUT*/ ODK_BOOL& flag)
{
    // place your code here
    
    flag = rcvdFlag;
    Convert_SZSTR_to_S7STRING(rcvdTopic, app2PLCtopic);
    app2PLCtopicLen = rcvdTopicLen;
    Convert_SZSTR_to_S7STRING(rcvdMessage, app2PLCmsg);
    app2PLCmsgLen = rcvdMessageLen;
    
    return ODK_SUCCESS;
}

ODK_RESULT ReadFabPlan(/*OUT*/control_flags& flags, /*OUT*/fog2plc& data_out)
{
    ODK_TRACE("Entrando en ReadFabPlan...");

    const char* Message = rcvdMessage;
    json msg = json::parse(Message);

    ODK_TRACE("Mensaje parseado.");

    flags.Control_Flag_Item_Completed = msg["flags"]["Control_Flag_Item_Completed"].get<bool>();
    flags.Control_Flag_New_Service = msg["flags"]["Control_Flag_New_Service"].get<bool>();
    flags.Control_Flag_Service_Completed = msg["flags"]["Control_Flag_Service_Completed"].get<bool>();

    ODK_TRACE("Flags obtenidas.");

    data_out.Id_Batch_Reference = msg["str_in"]["Id_Batch_Reference"].get<int>();
    data_out.Id_Machine_Reference = msg["str_in"]["Id_Machine_Reference"].get<int>();
    data_out.Id_Order_Reference = msg["str_in"]["Id_Order_Reference"].get<int>();
    data_out.Id_Ref_Subproduct_Type = msg["str_in"]["Id_Ref_Subproduct_Type"].get<int>();
    data_out.Operation_No_of_Items = msg["str_in"]["Operation_No_of_Items"].get<int>();
    data_out.Operation_Ref_Service_Type = msg["str_in"]["Operation_Ref_Service_Type"].get<int>();

    ODK_TRACE("Plan leído.");

    return ODK_SUCCESS;
}