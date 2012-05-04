import htmlentitydefs
import re
import xml

_squeeze_re = re.compile(r"[\x00-\x20]+").sub
def squeeze(value):
    """
        Replace all sequences of whitespace chars with a single space.

        >>> squeeze("hello    world")
        'hello world'

        >> squeeze("Hello \n World!"
        'Hello World!"
    """
    return _squeeze_re(" ", value).strip()


def truncate(s,min_pos=0,max_pos=75,ellipsis=True):
    """Return a nicely shortened string if over a set upper limit
    (default 75 characters)

    What is nicely shortened? Consider this line from Orwell's 1984...
    0---------1---------2---------3---------4---------5---------6---------7---->
    When we are omnipotent we shall have no more need of science. There will be

    If the limit is set to 70, a hard truncation would result in...
    When we are omnipotent we shall have no more need of science. There wi...

    Truncating to the nearest space might be better...
    When we are omnipotent we shall have no more need of science. There...

    The best truncation would be...
    When we are omnipotent we shall have no more need of science...

    Therefore, the returned string will be, in priority...

    1. If the string is less than the limit, just return the whole string
    2. If the string has a period, return the string from zero to the first
        period from the right
    3. If the string has no period, return the string from zero to the first
        space
    4. If there is no space or period in the range return a hard truncation

    In all cases, the string returned will have ellipsis appended unless
    otherwise specified.

    Parameters:
        s = string to be truncated as a String
        min_pos = minimum character index to return as Integer (returned
                  string will be at least this long - default 0)
        max_pos = maximum character index to return as Integer (returned
                  string will be at most this long - default 75)
        ellipsis = returned string will have an ellipsis appended to it
                   before it is returned if this is set as Boolean
                   (default is True)
    Returns:
        Truncated String
    Throws:
        ValueError exception if min_pos > max_pos, indicating improper
        configuration
    Usage:
    short_string = trunc(some_long_string)
    or
    shorter_string = trunc(some_long_string,max_pos=15,ellipsis=False)
    """
    # Sentinel value -1 returned by String function rfind
    NOT_FOUND = -1
    # Error message for max smaller than min positional error
    ERR_MAXMIN = 'Minimum position cannot be greater than maximum position'

    # If the minimum position value is greater than max, throw an exception
    if max_pos < min_pos:
        raise ValueError(ERR_MAXMIN)
        # Change the ellipsis characters here if you want a true ellipsis
    if ellipsis:
        suffix = '...'
    else:
        suffix = ''
        # Case 1: Return string if it is shorter (or equal to) than the limit
    length = len(s)
    if length <= max_pos:
        return s
    else:
        # Case 2: Return it to nearest period if possible
        try:
            end = s.rindex('.',min_pos,max_pos)
        except ValueError:
            # Case 3: Return string to nearest space
            end = s.rfind(' ',min_pos,max_pos)
            if end == NOT_FOUND:
                end = max_pos

        if length > max_pos:
            return s[0:end] + suffix

def _build_unicode_map():
    unicode_map = {}
    for name, value in htmlentitydefs.name2codepoint.iteritems():
        unicode_map[name] = unichr(value)
    return unicode_map

_HTML_UNICODE_MAP = _build_unicode_map()

def utf8(value):
    if isinstance(value, unicode):
        return value.encode("utf-8")
    assert isinstance(value, str)
    return value


def _unicode(value):
    if isinstance(value, str):
        return value.decode("utf-8")
    assert isinstance(value, unicode)
    return value


def _convert_entity(m):
    if m.group(1) == "#":
        try:
            return unichr(int(m.group(2)))
        except ValueError:
            return "&#%s;" % m.group(2)
    try:
        return _HTML_UNICODE_MAP[m.group(2)]
    except KeyError:
        return "&%s;" % m.group(2)

def xhtml_escape(value):
    """
        Escapes a string so it is valid within XML or XHTML.

        >>> xhtml_escape("Hello Bill & Ted :>")
        'Hello Bill &amp; Ted :&gt;'
    """
    return utf8(xml.sax.saxutils.escape(value))

_xhtml_unescape_re = re.compile(r"&(#?)(\w+?);").sub
def xhtml_unescape(value):
    """
        Un-escapes an XML-escaped string.

        >>> xhtml_unescape('Hello Bill &amp; Ted :&gt;')
        u'Hello Bill & Ted :>'
    """
    return _xhtml_unescape_re(_convert_entity, _unicode(value))