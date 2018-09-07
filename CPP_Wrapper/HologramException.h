#ifndef _HOLOGRAMEXCEPTION_H
#define _HOLOGRAMEXCEPTION_H

#include <exception>
#include <string>
using namespace std;


namespace Hologram
{

	/// <summary>
	/// The Hologram Exception that its functions can throw
	/// </summary>
	/// <seealso cref="exception" />
	class HologramException :
		public exception
	{
	public:
		/// <summary>
		/// Initializes a new instance of the <see cref="HologramException"/> class.
		/// </summary>
		HologramException();
		/// <summary>
		/// Initializes a new instance of the <see cref="HologramException"/> class.
		/// </summary>
		/// <param name="message">The message.</param>
		/// <param name="file">The file.</param>
		/// <param name="line">The line.</param>
		HologramException(const char* message, const char* function, const char* file, int line);
		/// <summary>
		/// Finalizes an instance of the <see cref="HologramException"/> class.
		/// </summary>
		~HologramException();

		/// <summary>
		/// Gets the message.
		/// </summary>
		/// <returns></returns>
		string getMessage(void);
		/// <summary>
		/// Gets the function.
		/// </summary>
		/// <returns></returns>
		string getFunction(void);
		/// <summary>
		/// Gets the file.
		/// </summary>
		/// <returns></returns>
		string getFile(void);
		/// <summary>
		/// Gets the line.
		/// </summary>
		/// <returns></returns>
		int    getLine(void);

		/// <summary>
		/// To the string.
		/// </summary>
		/// <returns></returns>
		string ToString(void);

	private:
		string _message;
		string _function;
		string _file;
		int    _line;
	};

}
#endif //_HOLOGRAMEXCEPTION_H
