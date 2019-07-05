#!/usr/bin/env python
# python 3.6+

# TODO: Exception prevents restart on file date change?

import getopt
import json
import os
import re
import subprocess
import sys
import time
import threading
import traceback
import webbrowser

from urllib.parse import parse_qs
from socketserver import ThreadingMixIn
from http.server import HTTPServer, SimpleHTTPRequestHandler

if 'SYMPAD_RUNNED_AS_WATCHED' in os.environ: # sympy slow to import if not precompiled so don't do it for watcher process as is unnecessary there
	import sympy as sp
	from sast import AST # AUTO_REMOVE_IN_SINGLE_SCRIPT
	import sparser       # AUTO_REMOVE_IN_SINGLE_SCRIPT
	import sym           # AUTO_REMOVE_IN_SINGLE_SCRIPT

	_var_last = AST ('@', '_')
	_vars     = {_var_last: AST.Zero} # This is individual session STATE! Threading can corrupt this!

_DEFAULT_ADDRESS          = ('localhost', 8000)

_RUNNING_AS_SINGLE_SCRIPT = False # AUTO_REMOVE_IN_SINGLE_SCRIPT

_STATIC_FILES             = {'/style.css': 'css', '/script.js': 'javascript', '/index.html': 'html', '/help.html': 'html'}
_FILES                    = {} # pylint food # AUTO_REMOVE_IN_SINGLE_SCRIPT

#...............................................................................................
def _ast_remap (ast, map_):
	return \
			ast if not isinstance (ast, AST) else \
			_ast_remap (map_ [ast], map_) if ast in map_ else \
			AST (*(_ast_remap (a, map_) for a in ast))

class Handler (SimpleHTTPRequestHandler):
	def do_GET (self):
		if self.path == '/':
			self.path = '/index.html'

		if self.path not in _STATIC_FILES:
			self.send_error (404, f'Invalid path {self.path!r}')

		elif not _RUNNING_AS_SINGLE_SCRIPT:
			return SimpleHTTPRequestHandler.do_GET (self)

		else:
			self.send_response (200)
			self.send_header ('Content-type', f'text/{_STATIC_FILES [self.path]}')
			self.end_headers ()
			self.wfile.write (_FILES [self.path [1:]])

	def do_POST (self):
		global _vars

		request = parse_qs (self.rfile.read (int (self.headers ['Content-Length'])).decode ('utf8'), keep_blank_values = True)
		parser  = sparser.Parser ()

		for key, val in list (request.items ()):
			if len (val) == 1:
				request [key] = val [0]

		if request ['mode'] == 'validate':
			ast, erridx, autocomplete = parser.parse (request ['text'])
			tex = simple = py         = None

			if ast is not None:
				ast    = _ast_remap (ast, {_var_last: _vars [_var_last]}) # just remap last evaluated _
				tex    = sym.ast2tex (ast)
				simple = sym.ast2simple (ast)
				py     = sym.ast2py (ast)

				if os.environ.get ('SYMPAD_DEBUG'):
					print ()
					print ('ast:   ', ast)
					print ('tex:   ', tex)
					print ('simple:', simple)
					print ('py:    ', py)
					print ()

			response = {
				'tex'         : tex,
				'simple'      : simple,
				'py'          : py,
				'erridx'      : erridx,
				'autocomplete': autocomplete,
			}

		else: # mode = 'evaluate'
			try:
				ast, _, _ = parser.parse (request ['text'])

				if ast.is_func and ast.func in {'vars', 'del', 'delall'}: # special admin function?
					if ast.func == 'vars':
						if len (_vars) == 1:
							ast = sym.AST_Text ('\\text{no variables defined}', '', '')
						else:
							ast = AST ('mat', tuple ((v, e) for v, e in filter (lambda ve: ve [0] != _var_last, sorted (_vars.items ()))))

					elif ast.func == 'del':
						try:
							ast = ast.arg.strip_paren ()
							del _vars [ast]
						except KeyError:
							raise NameError (f'variable {sym.ast2simple (ast)!r} is not defined')

					else: # ast.func == 'delall':
						_vars = {_var_last: _vars [_var_last]}
						ast   = sym.AST_Text ('\\text{all variables cleared}', '', '')

				else:
					if ast.is_ass and ast.lhs.is_var: # assignment?
						ast = _ast_remap (ast, {_var_last: _vars [_var_last]}) # just remap last evaluated _
					else:
						ast = _ast_remap (ast, _vars)

					sym.set_precision (ast)

					spt = sym.ast2spt (ast, doit = True)
					ast = sym.spt2ast (spt)

					if not (ast.is_ass and ast.lhs.is_var):
						_vars [_var_last] = ast

					else: # assignment, check for circular references
						new_vars = {**_vars, ast.lhs: ast.rhs}

						try:
							_ast_remap (ast.lhs, new_vars)
						except RecursionError:
							raise RecursionError ("I'm sorry, Dave. I'm afraid I can't do that. (circular reference detected)")

						_vars = new_vars

					if os.environ.get ('SYMPAD_DEBUG'):
						print ()
						print ('spt:        ', repr (spt))
						print ('spt type:   ', type (spt))
						print ('sympy latex:', sp.latex (spt))
						print ()

				response  = {
					'tex'   : sym.ast2tex (ast),
					'simple': sym.ast2simple (ast),
					'py'    : sym.ast2py (ast),
				}

			except Exception:
				response = {'err': ''.join (traceback.format_exception (*sys.exc_info ())).replace ('  ', '&emsp;').strip ().split ('\n')}

		response ['mode'] = request ['mode']
		response ['idx']  = request ['idx']
		response ['text'] = request ['text']

		self.send_response (200)
		self.send_header ("Content-type", "application/json")
		self.end_headers ()
		self.wfile.write (json.dumps (response).encode ('utf8'))

# class ThreadingHTTPServer (ThreadingMixIn, HTTPServer):
# 	pass

#...............................................................................................
_month_name = (None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

if __name__ == '__main__':
	try:
		if 'SYMPAD_RUNNED_AS_WATCHED' not in os.environ:
			args      = [sys.executable] + sys.argv
			first_run = '1'

			while 1:
				ret       = subprocess.run (args, env = {**os.environ, 'SYMPAD_RUNNED_AS_WATCHED': '1', 'SYMPAD_FIRST_RUN': first_run})
				first_run = ''

				if ret.returncode != 0:
					sys.exit (0)

		opts, argv = getopt.getopt (sys.argv [1:], '', ['debug', 'nobrowser'])

		if ('--debug', '') in opts:
			os.environ ['SYMPAD_DEBUG'] = '1'

		if not argv:
			host, port = _DEFAULT_ADDRESS
		else:
			host, port = (re.split (r'(?<=\]):' if argv [0].startswith ('[') else ':', argv [0]) + [_DEFAULT_ADDRESS [1]]) [:2]
			host, port = host.strip ('[]'), int (port)

		watch   = ('sympad.py',) if _RUNNING_AS_SINGLE_SCRIPT else ('lalr1.py', 'sparser.py', 'sym.py', 'server.py')
		tstamps = [os.stat (fnm).st_mtime for fnm in watch]
		httpd   = HTTPServer ((host, port), Handler) # ThreadingHTTPServer ((host, port), Handler)
		thread  = threading.Thread (target = httpd.serve_forever, daemon = True)

		thread.start ()

		def log_message (msg):
			y, m, d, hh, mm, ss, _, _, _ = time.localtime (time.time ())

			sys.stderr.write (f'{httpd.server_address [0]} - - ' \
					f'[{"%02d/%3s/%04d %02d:%02d:%02d" % (d, _month_name [m], y, hh, mm, ss)}] {msg}\n')

		log_message (f'Serving on {httpd.server_address [0]}:{httpd.server_address [1]}')

		if os.environ.get ('SYMPAD_FIRST_RUN') and ('--nobrowser', '') not in opts:
			webbrowser.open (f'http://{httpd.server_address [0] if httpd.server_address [0] != "0.0.0.0" else "127.0.0.1"}:{httpd.server_address [1]}/')

		while 1:
			time.sleep (0.5)

			if [os.stat (fnm).st_mtime for fnm in watch] != tstamps:
				log_message ('Files changed, restarting...')
				sys.exit (0)

	except OSError as e:
		if e.errno != 98:
			raise

		print (f'Port {port} seems to be in use, try specifying different port as a command line parameter, e.g. localhost:8001')

	except KeyboardInterrupt:
		sys.exit (0)

	sys.exit (-1)
