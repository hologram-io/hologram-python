#include "HologramCloud.h"
#include "HologramException.h"
#include "InternalHelpers.hpp"
#include <vector>
#include <string>
#include <sstream>
#include <iomanip>

// Just a little helper macro for all of the python functions to check if they work ad advertised.
#define PY_CHECK(o, n, m)		PPyObject o; if((o = (n)) == NULL) { PyErr_Print(); throw new HologramException(m, #n, __FILE__, __LINE__);  }
// Same as above, just does not create the objects and expects it to already have been declared.
#define PY_CHECK_NOOBJ(o, n, m) if ((o = (n)) == NULL) { PyErr_Print(); throw new HologramException(m, #n, __FILE__, __LINE__); }
// And for a bool return
#define PY_CHECK_BOOL(n, m)		if(((n)) != 0) { PyErr_Print(); throw new HologramException(m, #n, __FILE__, __LINE__);  }
// I just don't want to have references hanging around that I threw away are not NULL. It's just not right...
#define PY_DECREF(n) Py_DECREF(n); n = NULL
#define PY_XDECREF(n) Py_XDECREF(n); n = NULL

namespace Hologram
{

	HologramCloud::HologramCloud(map<string, string>& credentials, bool enable_inbound, string network, AUTHENTICATION_HANDLERS authentication_type)
	{
		// Initialize all the class variables to 0
		memset(this, 0, sizeof(HologramCloud));

		// initialize the python interpreter
		Py_Initialize();

		// Load the HologramCloud module
		// Do not step over this with a debugger. For some reason, python does not like it and becomes a viper.
		PY_CHECK(pyModuleHologram, PyImport_ImportModule("Hologram.HologramCloud"), "Could not import the module.");
		// Get the HologramCloud class attribute of the module. This does not instantiate it, just gives the "definition".
		PY_CHECK(pyClassHologramCloud, PyObject_GetAttrString(pyModuleHologram, "HologramCloud"), "Could not find the HologramCloud class in the module.");
		PY_DECREF(pyModuleHologram); //we don't need that no more

		// Now we need to pythonize all the parameters... man do I hate python! Lack of strong typing kills me.
		
		// Lets put it in a block to keep the variable scope cleaner...
		{
			vector<string> keys = extract_keys<string, string>(credentials);
			vector<string> values = extract_values<string, string>(credentials);

			// Lets fill the credentials dictionary if we have anything in the params...
			PY_CHECK(pyCredentialsArg, PyDict_New(), "Could not create credentials dictionary");

			for (size_t i = 0; i < keys.size(); i++)
			{
				PY_CHECK(pyValue, PyString_FromString(values.at(i).c_str()), "Could not generate Python string.");
				// A little lengthy, but I want it to be in one line for the debug macros to return the correct line number.
				PY_CHECK_BOOL(PyDict_SetItemString(pyCredentialsArg, keys.at(i).c_str(), pyValue), "Could not add entry to PyDictionary");
				PY_DECREF(pyValue); // We don't need that any more...
			}

			PPyObject pyEnableInboundArg = enable_inbound ? Py_True : Py_False;

			PY_CHECK(pyNetworkArg, PyString_FromString(network.c_str()), "Could not generate Python string.");

			PPyObject pyAuthType = NULL;
			switch (authentication_type)
			{
			case AUTHENTICATION_HANDLERS::totp:
				PY_CHECK_NOOBJ(pyAuthType, PyString_FromString("totp"), "Could not generate Python string.");
				break;

			case AUTHENTICATION_HANDLERS::csrpsk:
				PY_CHECK_NOOBJ(pyAuthType, PyString_FromString("csrpsk"), "Could not generate Python string.");
				break;

			case AUTHENTICATION_HANDLERS::sim_otp:
				PY_CHECK_NOOBJ(pyAuthType, PyString_FromString("sim_otp"), "Could not generate Python string.");
				break;

			default: //Something went REALLY wrong here...
				throw new HologramException("Authentication Type is not valid", "", __FILE__, __LINE__);
				break;
			}

			// Now, lets generate the Tuple to give to the constructor
			PY_CHECK(pyHologramCloudArgs, PyTuple_New(4), "Could not generate Python tuple.");

			// The tuple set item function steals our reference, so it's their job to decrease it :)
			PY_CHECK_BOOL(PyTuple_SetItem(pyHologramCloudArgs, 0, pyCredentialsArg), "Could not set python tuple");
			PY_CHECK_BOOL(PyTuple_SetItem(pyHologramCloudArgs, 0, pyEnableInboundArg), "Could not set python tuple");
			PY_CHECK_BOOL(PyTuple_SetItem(pyHologramCloudArgs, 0, pyNetworkArg), "Could not set python tuple");
			PY_CHECK_BOOL(PyTuple_SetItem(pyHologramCloudArgs, 0, pyAuthType), "Could not set python tuple");

			// Ok... finally we are able to grab an instance of the HologramCloud class! About time!
			PY_CHECK_NOOBJ(this->_pyInstanceHologramCloud, PyObject_CallObject(pyClassHologramCloud, pyHologramCloudArgs), "Could not instantiate HologramCloud class.");
			PY_DECREF(pyHologramCloudArgs); // Dont need this any more...
			PY_DECREF(pyClassHologramCloud); // Neither this...

			// Done! Now we can use the class
		}
	}


	HologramCloud::~HologramCloud()
	{
		// Lets clean up...
		PY_XDECREF(this->_pyInstanceHologramCloud);

		Py_Finalize();
	}

	bool HologramCloud::connect(int timeout)
	{
		bool result = false;

		//Get the network object so that we can connect
		PY_CHECK(pyNetworkProperty, PyObject_GetAttrString(this->_pyInstanceHologramCloud, "network"), "Could not get the network interface from the python class.");
		
		//Call the connect function
		PY_CHECK(pyConnectResult, PyObject_CallMethod(pyNetworkProperty, (char*)"connect", NULL, NULL), "Could not get the connect method from the python class");
		PY_DECREF(pyNetworkProperty);
		result = PyObject_IsTrue(pyConnectResult);
		PY_DECREF(pyConnectResult); //Dont need any more...

		return this->_isConnected = result;
	}

	bool HologramCloud::disconnect(void)
	{
		bool result = false;

		//Get the network object so that we can connect
		PY_CHECK(pyNetworkProperty, PyObject_GetAttrString(this->_pyInstanceHologramCloud, "network"), "Could not get the network interface from the python class.");

		//Call the disconnect function
		PY_CHECK(pyDisconnectResult, PyObject_CallMethod(pyNetworkProperty, (char*)"disconnect", NULL, NULL), "Could not get the disconnect method from the python class");
		PY_DECREF(pyNetworkProperty);
		result = PyObject_IsTrue(pyDisconnectResult);
		PY_DECREF(pyDisconnectResult); //Dont need any more...

		this->_isConnected = false;

		return result;
	}

	bool HologramCloud::openReceiveSocket(void)
	{
		bool result = false;

		//Call the openReceiveSocket function
		PY_CHECK(pyOpenReceiveSocketResult, PyObject_CallMethod(this->_pyInstanceHologramCloud, (char*)"openReceiveSocket", NULL, NULL), "Could not get the openReceiveSocket method from the python class");
		result = PyObject_IsTrue(pyOpenReceiveSocketResult);
		PY_DECREF(pyOpenReceiveSocketResult); //Dont need any more...

		return result;
	}

	void HologramCloud::closeReceiveSocket(void)
	{
		// Call the closeReceiveSocket function
		PY_CHECK(pyCloseReceiveSocket, PyObject_CallMethod(this->_pyInstanceHologramCloud, (char*)"closeReceiveSocket", NULL, NULL), "Could not get the closeReceiveSocket method from the python class");
		PY_DECREF(pyCloseReceiveSocket);
	}

	string HologramCloud::getResultString(ERROR_CODES code)
	{
		return _mErrorDesc.at(code);
	}

	void HologramCloud::setAuthenticationType(map<string, string>& credentials, AUTHENTICATION_HANDLERS authentication_type)
	{
		// Now we need to pythonize all the parameters... man do I hate python! Lack of strong typing kills me.

		vector<string> keys = extract_keys<string, string>(credentials);
		vector<string> values = extract_values<string, string>(credentials);

		// Lets fill the credentials dictionary if we have anything in the params...
		PY_CHECK(pyCredentialsArg, PyDict_New(), "Could not create credentials dictionary");

		for (size_t i = 0; i < keys.size(); i++)
		{
			PY_CHECK(pyValue, PyString_FromString(values.at(i).c_str()), "Could not generate Python string.");
			// A little lengthy, but I want it to be in one line for the debug macros to return the correct line number.
			PY_CHECK_BOOL(PyDict_SetItemString(pyCredentialsArg, keys.at(i).c_str(), pyValue), "Could not add entry to PyDictionary");
			PY_DECREF(pyValue); // We don't need that any more...
		}

		const char* sAuthType = "";
		switch (authentication_type)
		{
		case AUTHENTICATION_HANDLERS::totp:
			sAuthType = "totp";
			break;

		case AUTHENTICATION_HANDLERS::csrpsk:
			sAuthType = "csrpsk";
			break;

		case AUTHENTICATION_HANDLERS::sim_otp:
			sAuthType = "sim_otp";
			break;

		default: //Something went REALLY wrong here...
			throw new HologramException("Authentication Type is not valid", "", __FILE__, __LINE__);
			break;
		}

		// The tuple set item function steals our reference, so it's their job to decrease it :)

		//Call the setAuthenticationType function
		PY_CHECK(pysetAuthenticationTypeResult, PyObject_CallMethod(this->_pyInstanceHologramCloud, (char*)"setAuthenticationType", (char*)"Os", pyCredentialsArg, (char*)sAuthType), "Could not get the setAuthenticationType method from the python class");
		PY_DECREF(pyCredentialsArg);
		PY_DECREF(pysetAuthenticationTypeResult); //Dont need any more...
	}

	ERROR_CODES HologramCloud::sendMessage(string& message, vector<string> topics, int timeout)
	{
		ERROR_CODES result = ERROR_CODES::ERR_OK;
		
		PPyObject pyTopicsList = NULL;
		// Generate the parameters
		if (topics.empty())
			pyTopicsList = Py_None;
		else
		{
			PY_CHECK_NOOBJ(pyTopicsList, PyList_New(topics.size()), "Could not generate the python list");
			for (size_t i = 0; i < topics.size(); i++)
			{
				PY_CHECK(pyStrTopic, PyString_FromString(topics.at(i).c_str()), "Could not generate python string.");
				PY_CHECK_BOOL(PyList_SetItem(pyTopicsList, i, pyStrTopic), "Could not set item into list.");
				PY_DECREF(pyStrTopic);
			}
		}
		
		//Call the sendSMS function
		PY_CHECK(pySendMessage, PyObject_CallMethod(this->_pyInstanceHologramCloud, (char*)"sendMessage", (char*)"sOi", message.c_str(), pyTopicsList, timeout), "Could not get the sendSMS method from the python class");
		PY_DECREF(pyTopicsList);
		result = (ERROR_CODES)PyInt_AsLong(pySendMessage);
		PY_DECREF(pySendMessage); //Dont need any more...

		return result;
	}

	string HologramCloud::sendSMS(string & destination_number, string & message)
	{
		string result = "";

		//Call the sendSMS function
		PY_CHECK(pySendSMS, PyObject_CallMethod(this->_pyInstanceHologramCloud, (char*)"sendSMS", (char*)"ss", destination_number.c_str(), message.c_str()), "Could not get the sendSMS method from the python class");
		result = string(PyString_AsString(pySendSMS));
		PY_DECREF(pySendSMS); //Dont need any more...

		return result;
	}

	string HologramCloud::request_hex_nonce(void)
	{
		string result = "";

		//Call the request_hex_nonce function
		PY_CHECK(pyRequest_hex_nonceResult, PyObject_CallMethod(this->_pyInstanceHologramCloud, (char*)"request_hex_nonce", NULL, NULL), "Could not get the request_hex_nonce method from the python class");
		result = string(PyString_AsString(pyRequest_hex_nonceResult));
		PY_DECREF(pyRequest_hex_nonceResult); //Dont need any more...

		return result;
	}

	void HologramCloud::enableSMS(void)
	{
		// Call the closeReceiveSocket function
		PY_CHECK(pyEnableSMSResult, PyObject_CallMethod(this->_pyInstanceHologramCloud, (char*)"enableSMS", NULL, NULL), "Could not get the enableSMS method from the python class");
		PY_DECREF(pyEnableSMSResult);
	}

	void HologramCloud::disableSMS(void)
	{
		// Call the closeReceiveSocket function
		PY_CHECK(pyDisableSMSResult, PyObject_CallMethod(this->_pyInstanceHologramCloud, (char*)"disableSMS", NULL, NULL), "Could not get the disableSMS method from the python class");
		PY_DECREF(pyDisableSMSResult);
	}

	bool HologramCloud::popReceivedSMS(PSMS pSMS)
	{
		bool result = true;

		// If pSMS is NULL, its bad, so throw a pointer exception
		if (pSMS == NULL)
			throw make_exception_ptr<PSMS>(pSMS);

		memset(pSMS, 0, sizeof(SMS));

		//Call the popReceivedSMS function
		PY_CHECK(pyPopReceivedSMSResult, PyObject_CallMethod(this->_pyInstanceHologramCloud, (char*)"popReceivedSMS", NULL, NULL), "Could not get the popReceivedSMS method from the python class");
		if (pyPopReceivedSMSResult == Py_None)
		{
			result = false;
			PY_DECREF(pyPopReceivedSMSResult); //Dont need any more...
			return result;
		}

		//Fill the SMS struct
		PY_CHECK(pySMSSender, PyObject_GetAttrString(pyPopReceivedSMSResult, "sender"), "Could not get sender object from SMS result");
		PY_CHECK(pySMSTimeStamp, PyObject_GetAttrString(pyPopReceivedSMSResult, "timestamp"), "Could not get timestamp object from SMS result");
		PY_CHECK(pySMSMessage, PyObject_GetAttrString(pyPopReceivedSMSResult, "message"), "Could not get message object from SMS result");

		PY_CHECK(pySMSYear, PyObject_GetAttrString(pySMSTimeStamp, "year"), "Could not get year object from TimeStamp result");
		PY_CHECK(pySMSMonth, PyObject_GetAttrString(pySMSTimeStamp, "month"), "Could not get month object from TimeStamp result");
		PY_CHECK(pySMSDay, PyObject_GetAttrString(pySMSTimeStamp, "day"), "Could not get day object from TimeStamp result");
		PY_CHECK(pySMSHour, PyObject_GetAttrString(pySMSTimeStamp, "hour"), "Could not get hour object from TimeStamp result");
		PY_CHECK(pySMSMinute, PyObject_GetAttrString(pySMSTimeStamp, "minute"), "Could not get minute object from TimeStamp result");
		PY_CHECK(pySMSSecond, PyObject_GetAttrString(pySMSTimeStamp, "second"), "Could not get second object from TimeStamp result");
		PY_CHECK(pySMSTZQuater, PyObject_GetAttrString(pySMSTimeStamp, "tzquarter"), "Could not get tzquarter object from TimeStamp result");

		pSMS->sender = PyString_AsString(pySMSSender);
		PY_DECREF(pySMSSender);
		pSMS->message = PyString_AsString(pySMSMessage);
		PY_DECREF(pySMSMessage);
		pSMS->time.tm_year = PyInt_AsLong(pySMSYear) - 1900;
		PY_DECREF(pySMSYear);
		pSMS->time.tm_mon = PyInt_AsLong(pySMSMonth);
		PY_DECREF(pySMSMonth);
		pSMS->time.tm_mday = PyInt_AsLong(pySMSDay);
		PY_DECREF(pySMSDay);
		pSMS->time.tm_hour = PyInt_AsLong(pySMSHour);
		PY_DECREF(pySMSHour);
		pSMS->time.tm_min = PyInt_AsLong(pySMSMinute);
		PY_DECREF(pySMSMinute);
		pSMS->time.tm_sec = PyInt_AsLong(pySMSSecond);
		PY_DECREF(pySMSSecond);
		pSMS->time.tm_gmtoff = PyInt_AsLong(pySMSTZQuater) * 4 * 60;
		PY_DECREF(pySMSTZQuater);

		PY_DECREF(pyPopReceivedSMSResult); //Dont need any more...

		return result;
	}

	string HologramCloud::popReceivedMessage(void)
	{
		string result = "";

		//Call the popReceivedMessage function
		PY_CHECK(pyPopReceivedMessageResult, PyObject_CallMethod(this->_pyInstanceHologramCloud, (char*)"popReceivedMessage", NULL, NULL), "Could not get the popReceivedMessage method from the python class");
		if (pyPopReceivedMessageResult == Py_None)
			result = "";
		else
			result = string(PyString_AsString(pyPopReceivedMessageResult));
		Py_DECREF(Py_None);
		PY_DECREF(pyPopReceivedMessageResult); //Dont need any more...

		return result;
	}

	bool HologramCloud::getLocation(PLOCATION pLocation)
	{
		bool result = true;

		// If pSMS is NULL, its bad, so throw a pointer exception
		if (pLocation == NULL)
			throw make_exception_ptr<PLOCATION>(pLocation);

		memset(pLocation, 0, sizeof(LOCATION));

		//Get the network object so that we can connect
		PY_CHECK(pyNetworkProperty, PyObject_GetAttrString(this->_pyInstanceHologramCloud, "network"), "Could not get the network interface from the python class.");

		//Lets see if we can get the devices location...
		PY_CHECK(pyLocation, PyObject_GetAttrString(pyNetworkProperty, "location"), "Could not get location attribute");

		PY_CHECK(pyLocationDate, PyObject_GetAttrString(pyLocation, "date"), "Could not get date attribute from location");
		PY_CHECK(pyLocationTime, PyObject_GetAttrString(pyLocation, "time"), "Could not get time attribute from location");
		PY_CHECK(pyLocationLatitude, PyObject_GetAttrString(pyLocation, "latitude"), "Could not get latitude attribute from location");
		PY_CHECK(pyLocationLongitude, PyObject_GetAttrString(pyLocation, "longitude"), "Could not get longitude attribute from location");
		PY_CHECK(pyLocationAltitude, PyObject_GetAttrString(pyLocation, "altitude"), "Could not get altitude attribute from location");
		PY_CHECK(pyLocationUncertainty, PyObject_GetAttrString(pyLocation, "uncertainty"), "Could not get uncertainty attribute from location");

		stringstream dateTimeVal(string(string(PyString_AsString(pyLocationDate)) + string(" ") + string(PyString_AsString(pyLocationTime))));
		dateTimeVal >> get_time(&pLocation->datetime, "%d/%m/%Y %H:%M:%S");
		
		pLocation->latitude = atof(PyString_AsString(pyLocationLatitude));
		pLocation->longitude = atof(PyString_AsString(pyLocationLongitude));
		pLocation->altitude = atof(PyString_AsString(pyLocationAltitude));
		pLocation->uncertainty = atof(PyString_AsString(pyLocationUncertainty));

		Py_DECREF(pyLocationDate);
		Py_DECREF(pyLocationTime);
		Py_DECREF(pyLocationLatitude);
		Py_DECREF(pyLocationLongitude);
		Py_DECREF(pyLocationAltitude);
		Py_DECREF(pyLocationUncertainty);
		Py_DECREF(pyLocation);

		return result;
	}
	bool HologramCloud::IsConnected(void)
	{
		return this->_isConnected;
	}
}