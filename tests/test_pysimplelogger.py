import pytest
from pyrandomtools import asList, listContains

import pysimplelogger as under_test

# Lets use same output list for each test to simplify understanding
#
def logActions(thisLogger):
  thisLogger.fatal("Start")
  thisLogger.critical("CriticalLevel")
  thisLogger.trace("TraceLevel")
  thisLogger.debug("DebugLevel")
  thisLogger.info("InfoLevel")
  thisLogger.warning("WarningLevel")
  thisLogger.warn("WarnLevel")
  thisLogger.error("ErrorLevel")
  thisLogger.fatal("End")

def test_logger_info(capsys):
  myLogger = under_test.newLogger(None, level=under_test.infoLevel)
  logActions(myLogger)
  output = capsys.readouterr().err.split('\n')

  assert listContains('Start', output)
  assert listContains('test_logger_info', output)    # Name of this function
  assert not listContains('TraceLevel', output)
  assert not listContains('DebugLevel', output)
  assert listContains('InfoLevel', output)
  assert listContains('WarningLevel', output)
  assert listContains('WarnLevel', output)
  assert listContains('ErrorLevel', output)
  assert listContains('CriticalLevel', output)
  assert listContains('End', output)

def test_logger_debug(capsys):
  myLogger = under_test.newLogger(None, level=under_test.debugLevel, loggerName='--debug--')
  logActions(myLogger)
  output = capsys.readouterr().err.split('\n')

  assert listContains('Start', output)
  assert listContains('--debug--', output)          # My spedified name
  assert not listContains('TraceLevel', output)
  assert listContains('DebugLevel', output)
  assert listContains('InfoLevel', output)
  assert listContains('WarningLevel', output)
  assert listContains('WarnLevel', output)
  assert listContains('ErrorLevel', output)
  assert listContains('CriticalLevel', output)
  assert listContains('End', output)
  
def test_logger_trace(capsys):
  myLogger = under_test.newLogger(None, level=under_test.traceLevel)
  logActions(myLogger)
  output = capsys.readouterr().err.split('\n')

  assert listContains('Start', output)
  assert listContains('test_logger_trace', output)
  assert listContains('TraceLevel', output)
  assert listContains('DebugLevel', output)
  assert listContains('InfoLevel', output)
  assert listContains('WarningLevel', output)
  assert listContains('WarnLevel', output)
  assert listContains('ErrorLevel', output)
  assert listContains('CriticalLevel', output)
  assert listContains('End', output)
  
def test_logger_child(capsys):
  rootLogger = under_test.newLogger(None, level=under_test.infoLevel)
  myLogger = under_test.newLogger(rootLogger, loggerName='child')
  logActions(myLogger)
  output = capsys.readouterr().err.split('\n')
  print(output)

  assert listContains('Start', output)
  assert not listContains('TraceLevel', output)
  assert not listContains('DebugLevel', output)
  assert listContains('InfoLevel', output)
  assert listContains('WarningLevel', output)
  assert listContains('WarnLevel', output)
  assert listContains('ErrorLevel', output)
  assert listContains('CriticalLevel', output)
  assert listContains('End', output)  
