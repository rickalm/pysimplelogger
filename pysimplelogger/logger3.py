from __future__ import print_function
import logging, os, sys, traceback, weakref, inspect

from pprint import pprint

__all__ = [ 'newLogger', 'tracer', 'setDefaultLevel', 'criticalLevel', 'errorLevel', 'warningLevel', 'warnLevel', 'infoLevel', 'debugLevel', 'traceLevel', 'fatalLevel' ]

criticalLevel = logging.CRITICAL
fatalLevel = logging.CRITICAL
errorLevel = logging.ERROR
warningLevel = logging.WARNING
warnLevel = logging.WARNING
infoLevel = logging.INFO
debugLevel = logging.DEBUG
traceLevel = logging.DEBUG - 5

# Some code grabbed from logging to deal with internal issues
#
# _srcfile is used when walking the stack to check when we've got the first
# caller stack frame.
#
if hasattr(sys, 'frozen'): # support for py2exe
    _srcfile = os.path.normcase("logger3%s__init__%s" % (os.sep, __file__[-4:]))
elif __file__[-4:].lower() in ['.pyc', '.pyo']:
    _srcfile = os.path.normcase(__file__[:-4] + '.py')
else:
    _srcfile = os.path.normcase(__file__)
    
_myDefaultLevel = infoLevel
_rootLogger = None
_lastLogger = None
    
def setDefaultLevel(level): 
    """Set global default log level
    
    :param level: Numeric log level
    :type level: int
    
    :return: value stored in global defaultLevel, useful for confirming value was actually stored
    :rtype: int
    """
    
    global _myDefaultLevel
    if not isinstance(level,int):
        raise ValueError('Argument must be integer')

    _myDefaultLevel = level
    return _myDefaultLevel
    
def getDefaultLevel():
    """Fetch current defaultLevel from globals
    
    :return: Numeric log level
    :rtype: int
    """
    
    global _myDefaultLevel
    return _myDefaultLevel
    
def tracer(func):
    """Decorator to trace entry/exit of functions
    """
    def wrapper(*args, **kwargs):
        """Function wrapper for capturing invocation, params and returns from any function"""
        
        # If we are not at traceLevel, just call the wrapped function without any instrumentation
        #
        if getDefaultLevel() > traceLevel:
            return func(*args, **kwargs)
            
        else:
            # Get info about the function we are wrapping
            #
            func_info = dict(inspect.getmembers(func))
            code_info = dict(inspect.getmembers(func_info.get('__code__')))
            
            module = func_info.get('__module__')
            method = func_info.get('__name__')
            line = code_info.get('co_firstlineno')
            
            try:
                caller_lineno = sys.exc_info()[-1].tb_lineno
            except:
                caller_lineno = 'unknown'
                
            try:
                caller_name = sys.exc_info()[-1].tb_frame.f_code.co_filename
            except:
                caller_name = 'unknown'

            target = '{}/{}:{}'.format(module, method, line)
            caller = '{}:{}'.format(caller_name, caller_lineno)

            # In case we need to explore the structures again
            # print(func_info.keys())
            # print(code_info.keys())
            # traceback.print_tb(sys.exc_info()[2])

            l = newLogger(None, loggerName=target)
            l.trace('tracer-entering, caller {}'.format(caller))
            
            for i, v in enumerate(args):
                l.trace_json_dumps('Arg[{}]'.format(i), v)
            
            for k, v in kwargs.items():
                l.trace_json_dumps('KeyWord({})'.format(k), v)
                
            l.trace('tracer-invoking')
            r = func(*args, **kwargs)
            
            l.trace('tracer-exiting')
            l.trace_json_dumps('Return', r)

            return r
    return wrapper

def function_name(lookBack=1):
    return sys._getframe(lookBack).f_code.co_name

def caller_name():
    for i in [2,3,4,5,6,7,8]:
        if not function_name(i) in __all__:
            return function_name(i)
        
def firstValid(*iterable):
    '''Return the first non-None value in the list
    '''
    try:
        return list((el for el in iterable if el is not None))[0]
    except:
        return None

def newLogger(parentLogger, loggerName=None, level=None, logFormat=None, **kwargs):
    """Simplified log manager function. Ties to previously defined logger if the parent logger is not supplied. Based on Python logging with additional wrappers.
    
    :param parentLogger: Previous SimpleLogger object or None to create a new logger chain
    :type parentLogger: class SimpleLogger
    :param loggerName: string to include into the prefix of the log entries
    :type loggerName: str
    :param level: Integer log level as defined by this module
    :type level: int
    :param logFormat: log format string as defined by SimpleLogger.Formatter(logging.Formatter)
    :type logFormat: str

    :return: Logger object
    :rtype: SimpleLogger
    
    """
    global _rootLogger
    global _lastLogger
    
    #parentLogger = parentLogger or _lastLogger or _rootLogger
    #loggerName = str(loggerName or traceback.extract_stack(None, 2)[0][2])

    parentLogger = firstValid(parentLogger, kwargs.pop('parentLogger', _rootLogger))
    loggerName = firstValid(loggerName, kwargs.pop('loggerName', caller_name()))
    level = firstValid(level, kwargs.pop('level', getDefaultLevel()))
    
    if parentLogger is None:
        thisLogger = SimpleLogger(parentLogger, loggerName=loggerName, level=level)
        thisLogger.propagate = False
    else:
        thisLogger = parentLogger.getChild(loggerName, level=level)

    # Clear out existing handlers
    #
    for handler in thisLogger.handlers:
        try:
            thisLogger.removeHandler(handler)
        except:
            pass
    #
    # Clear out existing handlers

    # append new handler
    #
    sh = logging.StreamHandler()
    sh.flush = sys.stdout.flush
    sh.setLevel(thisLogger.level)
    sh.setFormatter(SimpleLogger.Formatter(firstValid(logFormat, '--- %(levelname)s:%(name)s:%(lineno)d: %(message)s')))
    thisLogger.addHandler(sh)
    #
    # append new handler
    
    # Update _rootLogger if undefined
    # Remember _lastLogger as well for reentry
    #
    _rootLogger = firstValid(_rootLogger, thisLogger)
    _lastLogger = thisLogger
    
    return thisLogger


class SimpleLogger(logging.Logger):    
    # Wrappers for logging classes
    #
    
    # Seems that logging looks for common parent classes for its children
    # so have to be named with same root
    #
    class Formatter(logging.Formatter):
        """Wrapper class for logging.Formatter because underlying logging class uses parent class name to find children
        """
        def __init__(self, *args, **kwargs):
            if sys.version_info[0] == 3:
                super().__init__(*args, **kwargs)
            else:
                super(SimpleLogger.Formatter,self).__init__(*args, **kwargs)

    class RootLogger(logging.RootLogger):
        """Wrapper class for logging.RootLogger because underlying logging class uses parent class name to find children
        """
        def __init__(self, *args, **kwargs):
            if sys.version_info[0] == 3:
                super().__init__(*args, **kwargs)
            else:
                super(SimpleLogger.RootLogger,self).__init__(*args, **kwargs)

    class Manager(logging.Manager):
        """Wrapper class for logging.Manager because underlying logging class uses parent class name to find children
        """
        def __init__(self, *args, **kwargs):
            if sys.version_info[0] == 3:
                super().__init__(*args, **kwargs)
            else:
                super(SimpleLogger.Manager,self).__init__(*args, **kwargs)
    #
    # Wrappers for logging classes

    def __del__(self):
        global _rootLogger
        if _rootLogger == self:
            _rootLogger = None
        del self
            
    # Replacing logging methods
    #
    def __init__(self, name, **kwargs):
        """Wrapper for :class:`logging` replacing the children with the required wrapped children
        
        Adds support for a 'TRACE' level of logging which combined with the @SimpleLogger.tracer decorator allows instrumentating calling sequences within log files
        """

        logging.addLevelName(traceLevel, "TRACE")
        level = kwargs.pop('level', getDefaultLevel())
        loggerName = firstValid(name, kwargs.pop('loggerName', caller_name()))

        print("** ",level,loggerName,kwargs)

        self.root = SimpleLogger.RootLogger(level=level)
        self.manager = self.Manager(self.root)
        self.manager.loggerClass = SimpleLogger

        if sys.version_info[0] == 3:
            super().__init__(loggerName, level=level)
            self.findCaller = self.findCaller3
        else:
            super(SimpleLogger,self).__init__(loggerName, level=level)
            self.findCaller = self.findCaller2
            

    def getChild(self, suffix=None, level=None):
        """Wrapper for :class:`logging.getChild` replacing the children with the required wrapped children
        """
        
        print(suffix)
        suffix = firstValid(suffix, traceback.extract_stack(None, 3)[0][2])
        print(suffix)
        
        if self.root is not self:
            suffix = '.'.join([self.name, suffix])

        thisLogger = self.manager.getLogger(suffix)
        thisLogger.propagate = self.propagate
        thisLogger.setLevel(firstValid(level, self.level))
        return thisLogger
        

    def findCaller2(self, v1=None):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        
        Based on code from logging class for Python2.x
        """
        if v1 is None:
            return "(unknown file)", 0, "(unknown function)"
        else:
            f = v1.f_back
        
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            break
        return rv


    def findCaller3(self, stack_info=False):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        source from logging.py codebase
        
        Based on code from logging class for Python 3.x
        """
        # If we didn't find the currentframe, then return defaults
        #
        rv = "(unknown file)", 0, "(unknown function)", None

        if self.currentframe() is None:
            return rv
        else:
            f = self.currentframe().f_back
        
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            sinfo = None
            if stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
                sio.close()
            rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
            break
        return rv
    #
    # Replacing logging methods


    def json_serializer(self, obj):
        """JSON serializer for objects not serializable by default json code
        
        Currently adds support for date and datetime objects
        """
        
        from datetime import date, datetime
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        
        raise TypeError ("Type %s not serializable" % type(obj))


    def json_outputer(self, *args, **kwargs):
        """A json formatter for logging that indents the logs according to the current log format
        """
        
        import re, json
        myArgs = dict(kwargs)
        
        # Set defaults if not already defined
        #
        myArgs['default'] = myArgs.get('default', self.json_serializer)
        myArgs['indent'] = myArgs.get('indent', 2)
        
        try:
            return re.sub(
                '^', 
                ' ' * ( myArgs['indent'] * 2), 
                json.dumps(*args, **myArgs), 
                flags=re.MULTILINE
            )
            
        except Exception as e:
            # We failed to produce a JSON dump, so share what info we know about the object
            return None


    def json_dumps(self, *args, **kwargs):
        """
        # If we were given 2 args the first being a string
        # then assume its a descriptor and object
        #
        """
        
        if len(args) == 2 and isinstance(args[0], str):
            reply = self.json_outputer(args[1])
            if reply is None:
                return "{}  type:{}".format(args[0], type(args[1]))
            else:
                return "{}  type:{}  data:\n{}".format(args[0], type(args[1]), reply)
                
        # Otherwise just dump the passed args
        else:
            return firstValid(self.json_outputer(args, **kwargs), [ list(args), dict(kwargs) ])

    # New handers and their json dumpers
    def fatal(self, *args, **kwargs):
        self.log(fatalLevel, *args, **kwargs)
        
    def fatal_json_dumps(self, *args, **kwargs):
        if self.level <= fatalLevel:             
            self.log(fatalLevel, self.json_dumps(*args, **kwargs))
        
    def trace(self, *args, **kwargs):
        self.log(traceLevel, *args, **kwargs)

    def trace_json_dumps(self, *args, **kwargs):
        if self.level <= traceLevel:             
            self.log(traceLevel, self.json_dumps(*args, **kwargs))

    def error_tb(self, *args, **kwargs):
        if self.level <= errorLevel:             
            self.log(errorLevel, *args, **kwargs)
            self.log(errorLevel, traceback.format_exc(10))

    # warn may be deprecated, but get over it people expect it to exist
    #
    def warn(self, *args, **kwargs):
        self.log(warningLevel, *args, **kwargs)

    def warn_json_dumps(self, *args, **kwargs):
        if self.level <= warningLevel:             
            self.log(warningLevel, self.json_dumps(*args, **kwargs))
  
                    
    # dumpers for existing errortypes
    #
    def debug_json_dumps(self, *args, **kwargs):
        if self.level <= debugLevel:             
            self.log(debugLevel, self.json_dumps(*args, **kwargs))

    def info_json_dumps(self, *args, **kwargs):
        if self.level <= infoLevel:             
            self.log(infoLevel, self.json_dumps(*args, **kwargs))

    def warning_json_dumps(self, *args, **kwargs):
        if self.level <= warningLevel:             
            self.log(warningLevel, self.json_dumps(*args, **kwargs))

    def error_json_dumps(self, *args, **kwargs):
        if self.level <= errorLevel:             
            self.log(errorLevel, self.json_dumps(*args, **kwargs))

    def critical_json_dumps(self, *args, **kwargs):
        if self.level <= criticalLevel:             
            self.log(criticalLevel, self.json_dumps(*args, **kwargs))

    # next bit from 1.5.2's inspect.py
    #
    def currentframe(self):
        if hasattr(sys, '_getframe'): 
            return sys._getframe(3)
        else:
            """Return the frame object for the caller's stack frame."""
            try:
                raise Exception
            except:
                return sys.exc_info()[2].tb_frame.f_back
