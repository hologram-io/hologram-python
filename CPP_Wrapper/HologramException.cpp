#include "HologramException.h"
#include <sstream>

Hologram::HologramException::HologramException()
{
	this->_message = "";
	this->_file = "";
	this->_line = 0;
}


Hologram::HologramException::HologramException(const char* message, const char* function, const char* file, int line)
{
	this->_message = message;
	this->_function = function;
	this->_file = file;
	this->_line = line;
}

Hologram::HologramException::~HologramException()
{
	//Nothing to do here...
}

string Hologram::HologramException::getMessage(void)
{
	return this->_message;
}

string Hologram::HologramException::getFunction(void)
{
	return this->_function;
}

string Hologram::HologramException::getFile(void)
{
	return this->_file;
}

int Hologram::HologramException::getLine(void)
{
	return this->_line;
}

string Hologram::HologramException::ToString(void)
{
	stringstream strBuilder;
	strBuilder << this->_message << endl << "Function: " << this->_function << endl << "File: " << this->_file << endl << "Line: " << this->_line << endl;
	return strBuilder.str();
}
