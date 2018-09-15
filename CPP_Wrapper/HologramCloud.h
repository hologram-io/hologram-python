#ifndef _HOLOGRAMCLOUD_H
#define _HOLOGRAMCLOUD_H

#include <string>
#include <map>
#include <vector>
#include <ctime>

#include <python2.7/Python.h>

using namespace std;

#define HOLOGRAM_DEFAULT_SEND_MESSAGE_TIMEOUT	5
//#define HOLOGRAM_HOST_SEND						"cloudsocket.hologram.io"
//#define HOLOGRAM_PORT_SEND						9999
//#define HOLOGRAM_HOST_RECEIVE					"0.0.0.0"
//#define HOLOGRAM_PORT_RECEIVE					4010
//#define HOLOGRAM_MAX_SMS_LENGTH					160
#define HOLOGRAM_DEFAULT_CELLULAR_TIMEOUT		200

namespace Hologram
{
	typedef PyObject* PPyObject;	// Just to make it easier to write :)

	/// <summary>
	/// Enumerates the available auth handlers
	/// </summary>
	typedef enum 
	{
		/// <summary>
		/// CSRPSK Authentication
		/// </summary>
		csrpsk,		//CSRPSKAuthentication.CSRPSKAuthentication,
		/// <summary>
		/// TOTP Authentication
		/// </summary>
		totp,		//TOTPAuthentication
		/// <summary>
		/// SIM OTP Authentication
		/// </summary>
		sim_otp		//SIMOTPAuthentication
	}AUTHENTICATION_HANDLERS, *PAUTHENTICATION_HANDLERS;

	/// <summary>
	/// Enumerates the possible error codes
	/// </summary>
	typedef enum
	{
		/// <summary>
		/// No Error
		/// </summary>
		ERR_OK = 0,
		/// <summary>
		/// Connection was closed before a terminating character
		/// but message might be fine
		/// </summary>
		ERR_CONNCLOSED = 1,		// Connection was closed before a terminating character
								// but message might be fine
		/// <summary>
		/// Couldn't parse the message
		/// </summary>
		ERR_MSGINVALID = 2,		// Couldn't parse the message
		/// <summary>
		/// Auth section of message was invalid
		/// </summary>
		ERR_AUTHINVALID = 3,	// Auth section of message was invalid
		/// <summary>
		/// Payload type was invalid
		/// </summary>
		ERR_PAYLOADINVALID = 4,	// Payload type was invalid
		/// <summary>
		/// Protocol type was invalid
		/// </summary>
		ERR_PROTINVALID = 5,	// Protocol type was invalid
		/// <summary>
		/// An internal error occurred
		/// </summary>
		ERR_INTERNAL = 6,		// An internal error occurred
		/// <summary>
		/// Metadata was formatted incorrectly
		/// </summary>
		ERR_METADATA = 7,		// Metadata was formatted incorrectly
		/// <summary>
		/// Topic was formatted incorrectly
		/// </summary>
		ERR_TOPICINVALID = 8,	// Topic was formatted incorrectly
		/// <summary>
		/// Unknown error
		/// </summary>
		ERR_UNKNOWN = -1		// Unknown error
	}ERROR_CODES, *PERROR_CODES;

	/// <summary>
	/// SMS Structure
	/// </summary>
	typedef struct
	{
		string sender;		// Sender of the SMS
		struct tm time;			// Time the SMS was sent as struct tm
		string message;		// The SMS content
	}SMS, *PSMS;

	/// <summary>
	/// Location structure
	/// </summary>
	typedef struct
	{
		struct tm datetime;	// Current UTC Date/Time
		double latitude;	// Device Latitude
		double longitude;	// Device Longitude
		double altitude;	// Device Alteitude (currently unsopported on Nova)
		double uncertainty; // Location uncertainty value (no idea how to read that...
	}LOCATION, *PLOCATION;

	/// <summary>
	/// C++ Wrapper for the HologramCloud API from Hologram
	/// </summary>
	class HologramCloud
	{
	public:
		/// <summary>
		/// Initializes a new instance of the <see cref="HologramCloud" /> class.
		/// </summary>
		/// <param name="credentials">The credentials.</param>
		/// <param name="enable_inbound">if set to <c>true</c> [enable inbound].</param>
		/// <param name="network">The network.</param>
		/// <param name="authentication_type">Type of the authentication.</param>
		/// <exception cref="HologramException">Exception thrown on error</exception>
		HologramCloud(map<string, string> const& credentials, bool enable_inbound = false, string const& network = string(""), AUTHENTICATION_HANDLERS authentication_type = AUTHENTICATION_HANDLERS::totp);
		/// <summary>
		/// Finalizes an instance of the <see cref="HologramCloud"/> class.
		/// </summary>
		virtual ~HologramCloud();

		/// <summary>
		/// Connects to modem with the specified timeout.
		/// </summary>
		/// <param name="timeout">The timeout.</param>
		/// <returns>true on success</returns>
		bool connect(int timeout = HOLOGRAM_DEFAULT_CELLULAR_TIMEOUT);

		/// <summary>
		/// Disconnects this modem.
		/// </summary>
		/// <returns></returns>
		bool disconnect(void);

		/// <summary>
		/// Opens the receive socket.
		/// </summary>
		/// <returns></returns>
		bool openReceiveSocket(void);

		/// <summary>
		/// Closes the receive socket.
		/// </summary>
		void closeReceiveSocket(void);

		/// <summary>
		/// Converts an error code into a human readable string
		/// </summary>
		/// <param name="code">The error code.</param>
		/// <returns>The Error Description as const char*</returns>
		string getResultString(ERROR_CODES code);
		
		/// <summary>
		/// Sets the type of the authentication.
		/// </summary>
		/// <param name="credentials">The credentials as map<string, string>.</param>
		/// <param name="authentication_type">Type of the authentication.</param>
		void setAuthenticationType(map<string, string> credentials, AUTHENTICATION_HANDLERS authentication_type = AUTHENTICATION_HANDLERS::csrpsk);

		/// <summary>
		/// Sends a message to the cloud.
		/// </summary>
		/// <param name="message">The message as string.</param>
		/// <param name="topics">The topics defined in the backend as a list of string.</param>
		/// <param name="timeout">The timeout for sending the message in seconds.</param>
		/// <returns></returns>
		ERROR_CODES sendMessage(string message, vector<string> topics = vector<string>(), int timeout = HOLOGRAM_DEFAULT_SEND_MESSAGE_TIMEOUT);

		/// <summary>
		/// Sends an SMS.
		/// </summary>
		/// <param name="destination_number">The destination number.</param>
		/// <param name="message">The message.</param>
		/// <returns>A string with a response description</returns>
		string sendSMS(string destination_number, string message);

		/// <summary>
		/// Requests the hexadecimal nonce.
		/// </summary>
		/// <returns>Some string???</returns>
		string request_hex_nonce(void);

		/// <summary>
		/// Enables the SMS.
		/// </summary>
		void enableSMS(void);

		/// <summary>
		/// Disables the SMS.
		/// </summary>
		void disableSMS(void);

		/// <summary>
		/// Receives the first received SMS from the FIFO.
		/// </summary>
		/// <param name="pSMS">Pointer to a SMS structure</param>
		/// <returns>
		/// True if a msg was received
		/// </returns>
		bool popReceivedSMS(PSMS pSMS);

		/// <summary>
		/// Receives the first received message from the FIFO.
		/// </summary>
		/// <returns>The received message as string</returns>
		string popReceivedMessage(void);

		/// <summary>
		/// Gets the location.
		/// </summary>
		/// <param name="pLocation">Pointer to a location structure.</param>
		/// <returns>True if the location request succeeded</returns>
		bool getLocation(PLOCATION pLocation);

		/// <summary>
		/// Determines whether this instance is connected.
		/// </summary>
		/// <returns>
		///   <c>true</c> if this instance is connected; otherwise, <c>false</c>.
		/// </returns>
		bool IsConnected(void);

		/// <summary>
		/// Gets the socket status
		/// </summary>
		/// <returns>True if the socket is open</returns>
		bool SocketIsOpen(void);

	private:
		PPyObject _pyInstanceHologramCloud;

		bool _isConnected;
		bool _socketOpen;

		const map<ERROR_CODES, const char*> _mErrorDesc =
		{
			{ERROR_CODES::ERR_OK,				"Message sent successfully"},
			{ERROR_CODES::ERR_CONNCLOSED,		"Connection was closed so we couldn\'t read the whole message"},
			{ERROR_CODES::ERR_MSGINVALID,		"Failed to parse the message"},
			{ERROR_CODES::ERR_AUTHINVALID,		"Auth section of the message was invalid"},
			{ERROR_CODES::ERR_PAYLOADINVALID,	"Payload type was invalid"},
			{ERROR_CODES::ERR_PROTINVALID,		"Protocol type was invalid"},
			{ERROR_CODES::ERR_INTERNAL,			"Internal error in Hologram Cloud"},
			{ERROR_CODES::ERR_METADATA,			"Metadata was formatted incorrectly"},
			{ERROR_CODES::ERR_TOPICINVALID,		"Topic was formatted incorrectly"},
			{ERROR_CODES::ERR_UNKNOWN,			"Unknown error"}
		};
	};
}

#endif //_HOLOGRAMCLOUD_H
