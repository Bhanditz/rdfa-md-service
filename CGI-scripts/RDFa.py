#!/usr/bin/python
# -*- coding: utf-8 -*-
# Maintainer: Ivan Herman <ivan@w3.org>
"""
Possible CGI entry point for the RDFa 1.1 package.

This version is adapted to the particualarities of the W3C setup as well as my own machine for Python paths


@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@contact: Ivan Herman, ivan@w3.org
"""
from __future__ import print_function

__version__ = "3.0"
import cgi
import cgitb
import sys, os
#cgi.print_environ()

# Necessary setup on various environments. This may have to be adapted when
# installing the scripts on another architecture. "darwin" refers to my local
# Mac (and is therefore used for testing); W3C runs on linux machines.
if sys.platform == "darwin" :
	# this is my local machine
	sys.path.insert(0,"/Users/ivan/Library/Python")
	os.environ['PyRdfaCacheDir'] = '/Users/ivan/.pyrdfa-cache'
	cgitb.enable()
else :
	# this is the server on W3C
	sys.path.insert(0,"/usr/local/lib/python2.4/site-packages/PythonLib-IH")
	sys.path.insert(0,"/usr/local/lib/python2.4/site-packages/PythonLib-IH/rdfa-1.1")
	os.environ['PyRdfaCacheDir'] = '/usr/local/apache/cgi/cgi-bin-other/RDFa/data-local'
	cgitb.enable(display=0, logdir="/home/nobody/tracebacks/")

from rdfa_md import extract_rdf, validate_rdfa, err_message, brett_test


def uri_test(uri) :
	"""Testing, when running on W3C, the safety of the URL.
	If the the test does not pass, ie an exception is raised somewhere down the line, an error message is sent back (via HTTP) to the caller, and everything stops.

	@param uri: the URI to be checked.
	"""
	if not sys.platform == "darwin" : brett_test(uri)


def process_input(form):
	"""Pre-rocess the form data. If all checking and processing is fine, call out to processURI
	to do the real work.

	@param uri: the URI for the RDFa source (if relevant, ie, if the data is not uploaded or fed in as text)
	@param form: form data, as returned by Python's FieldStorage
	"""

	uri = ""
	# The 'uri' term is modified to be turned into a 'fake' value to denote the upload and text cases.
	if "uploaded" in form and form["uploaded"].file :
		# The real data is stored in the form as a reference to a file
		uri = "uploaded:"
	elif "text" in form and form["text"].value != None and len(form["text"].value.strip()) != 0 :
		uri  = "text:"
	else :
		# Either there is an error, and we have to stop there, or it is a real URI
		if not "uri" in form :
			print('Content-type: text/html; charset=utf-8')
			print('Status: 400 Invalid Input')
			print("")
			print("<html>")
			print("<head>")
			print("<title>Error in RDFa processing</title>")
			print("</head><body>")
			print("<h1>Error in distilling RDFa</h1>")
			print("<p>No URI has been specified</p>")
			print("</body>")
			print("</html>")
			sys.exit(1)

		try :
			uri = form.getfirst("uri")
		except :
			print('Content-type: text/html; charset=utf-8')
			print('Status: 400 Invalid Input')
			print("")
			print("<html>")
			print("<head>")
			print("<title>Error in RDFa processing</title>")
			print("</head><body>")
			print("<h1>Error in distilling RDFa</h1>")
			print("No URI has been specified")
			print("</body>")
			print("</html>")
			sys.exit(1)

	# If we got here, we should have the data hidden, in some way or other, behind the form data
	# and/or the URI
	try :
		# Thanks to Sergio and Diego for the idea and code for the referer branch
		if uri == "referer" :
			uri = os.getenv('HTTP_REFERER')
			if uri is None:
				newuri = "http://www.w3.org/2012/pyRdfa/no_referer.html"
			else:
				uri_test(uri)
				newuri = "http://www.w3.org/2012/pyRdfa/extract?uri=" + uri
			print("Status: 307 Moved Temporarily")
			print("Location: " + newuri)
			print("")
		else :
			# last point of check: use Brett's script to check the validity of the URI
			if not (uri == 'text:' or uri == 'uploaded:') :
				uri_test(uri)

			print( validate_rdfa(uri, form) if "validate" in form else extract_rdf(uri, form) )
	except Exception as e :
		l = len(e.args)
		msg = "" if l == 0 else (e.args[0] if l == 1 else repr(e.args))
		err_message(uri, 'Exception raised: "%s"' % msg)



#######################################################################################
# The real CGI processing!!
process_input(cgi.FieldStorage())