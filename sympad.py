#!/usr/bin/env python
# python 3.6+

# THIS SCRIPT WAS AUTOGENERATIED FROM SOURCE FILES FOUND AT:
# https://github.com/Pristine-Cat/SymPad

# Copyright (c) 2019 Tomasz Pytel
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

_RUNNING_AS_SINGLE_SCRIPT = True


_FILES = {

	'style.css': # style.css

r"""* {
	box-sizing: border-box;
	margin: 0;
	padding: 0;
}

body {
	margin-top: 1em;
	margin-bottom: 6em;
	cursor: default;
}

#Clipboard {
	position: fixed;
	bottom: 0;
	color: transparent;
	border: 0px;
}

#Background {
	position: fixed;
	z-index: -1;
	left: 0;
	top: 0;
}

#Greeting {
	position: fixed;
	left: 50%;
	top: 50%;
	transform: translate(-50%, -50%);
	color: #0007;
}

.GreetingA {
	display: block;
	color: #0007;
	text-decoration: none;
	margin-bottom: 0.5em;
}

#InputBG {
	position: fixed;
	z-index: 2;
	height: 4em;
	bottom: 0;
	left: 0;
	right: 0;
	background-color: white;
}

#Input {
	position: fixed;
	z-index: 3;
	bottom: 2em;
	left: 4em;
	right: 1em;
	border-color: transparent;
	outline-color: transparent;
	background-color: transparent;
}

#InputOverlay {
	z-index: 4;
}

#OverlayGood {
	-webkit-text-fill-color: transparent;
}

#OverlayError {
	-webkit-text-fill-color: #f44;
}

#OverlayAutocomplete {
	-webkit-text-fill-color: #999;
}

.LogEntry {
	width: 100%;
	margin-bottom: 1.5em;
}

.LogMargin {
	display: inline-block;
	height: 100%;
	width: 4em;
	vertical-align: top;
	text-align: right;
	padding-right: 0.5em;
}

.LogBody {
	display: inline-block;
	margin-right: -9999em;
}

.LogWait {
	vertical-align: top;
}

.LogInput {
	margin-bottom: 0.75em;
	width: fit-content;
	cursor: pointer;
}

.LogEval {
	position: relative;
	margin-bottom: 0.25em;
	cursor: pointer;
}

.LogMsg {
	margin-bottom: 0.25em;
}

.LogError {
	margin-bottom: 0.25em;
	color: red;
}

.LogErrorTriange {
	position: absolute;
	left: -1.25em;
	top: 0.25em;
	font-size: 0.7em;
	color: red;
	font-weight: bold;
}
""".encode ("utf8"),

	'script.js': # script.js

r"""// TODO: Multiple spaces screw up overlay text position.
// TODO: Change how left/right arrows interact with autocomplete.
// TODO: Stupid scrollbars...
// TODO: Warning messages on evaluate when SymPy object not understood?
// TODO: Arrow keys in Edge?

var URL              = '/';
var MJQueue          = null;
var MarginTop        = Infinity;
var PreventFocusOut  = true;

var History          = [];
var HistIdx          = 0;
var LogIdx           = 0;
var UniqueID         = 1;

var Validations      = [undefined];
var Evaluations      = [undefined];
var ErrorIdx         = null;
var Autocomplete     = [];

var LastClickTime    = 0;
var NumClicks        = 0;

var GreetingFadedOut = false;

//...............................................................................................
function generateBG () {
	function writeRandomData (data, x0, y0, width, height) {
		let p, d;

		for (let y = y0; y < height; y ++) {
			p = (width * y + x0) * 4;

			for (let x = x0; x < width; x ++) {
				d            = 244 + Math.floor (Math.random () * 12);
				data [p]     = data [p + 1] = d;
				data [p + 2] = d - 8;
				data [p + 3] = 255;
				p            = p + 4;
			}
		}
	}

	let canv    = document.getElementById ('Background');
	canv.width  = window.innerWidth;
	canv.height = window.innerHeight;
	let ctx     = canv.getContext ('2d');
	let imgd    = ctx.getImageData (0, 0, canv.width, canv.height); // ctx.createImageData (width, height);

	writeRandomData (imgd.data, 0, 0, canv.width, canv.height);
	ctx.putImageData (imgd, 0, 0);

	if (window.location.pathname == '/') {
		canv        = $('#InputBG') [0];
		ctx         = canv.getContext ('2d');
		canv.width  = window.innerWidth;

		ctx.putImageData (imgd, 0, 0);
	}
}

//...............................................................................................
function copyInputStyle () {
	JQInput.css ({left: $('#LogEntry1').position ().left})
	JQInput.width ($('#Log').width ());

	let style   = getComputedStyle (document.getElementById ('Input'));
	let overlay = document.getElementById ('InputOverlay');

  for (let prop of style) {
    overlay.style [prop] = style [prop];
	}

	overlay.style ['backgroundColor'] = 'transparent';
}

//...............................................................................................
function scrollToEnd () {
	window.scrollTo (0, document.body.scrollHeight);
}

//...............................................................................................
function resize () {
	copyInputStyle ();
	scrollToEnd ();
	generateBG ();
}

//...............................................................................................
function logResize () {
	// let atEnd  = !(document.documentElement.offsetHeight - document.documentElement.scrollTop - window.innerHeight);
	let margin = Math.max (BodyMarginTop, Math.floor (window.innerHeight - $('body').height () - BodyMarginBottom + 3)); // +3 is fudge factor

	if (margin < MarginTop) {
		MarginTop = margin
		$('body').css ({'margin-top': margin});
	}

	// if (atEnd) {
	// 	scrollToEnd ();
	// }
}

//...............................................................................................
var LastDocHeight = undefined;
var LastWinHeight = undefined;

function monitorStuff () {
	let curDocHeight = $(document).height ();
	let curWinHeight = $(window).height ();

	if (curDocHeight != LastDocHeight || curWinHeight != LastWinHeight) {
		copyInputStyle ();

		window.LastDocHeight = curDocHeight;
		window.LastWinHeight = curWinHeight;
	}

	if (PreventFocusOut) {
		JQInput.focus ();
	}

	setTimeout (monitorStuff, 50);
}

//...............................................................................................
function readyMathJax () {
	window.MJQueue = MathJax.Hub.queue;

	var TEX        = MathJax.InputJax.TeX;
	var PREFILTER  = TEX.prefilterMath;

	TEX.Augment ({
		prefilterMath: function (tex, displaymode, script) {
			return PREFILTER.call (TEX, '\\displaystyle{' + tex + '}', displaymode, script);
		}
	});
}

//...............................................................................................
function reprioritizeMJQueue () {
	let p = MJQueue.queue.pop ();

	if (p !== undefined) {
		MJQueue.queue.splice (0, 0, p);
	}
}

//...............................................................................................
function addLogEntry () {
	LogIdx += 1;

	$('#Log').append (`
			<div class="LogEntry"><div class="LogMargin">${LogIdx}.</div><div class="LogBody" id="LogEntry${LogIdx}"><div class="LogInput" id="LogInput${LogIdx}">
				<img class="LogWait" id="LogInputWait${LogIdx}" src="https://i.gifer.com/origin/3f/3face8da2a6c3dcd27cb4a1aaa32c926_w200.webp" width="16" style="visibility: hidden">
			</div></div></div>`)

	Validations.push (undefined);
	Evaluations.push (undefined);
}

//...............................................................................................
function writeToClipboard (text) {
	PreventFocusOut = false;

	$('#Clipboard').val (text);
	$('#Clipboard').focus ();
	$('#Clipboard').select ();
	document.execCommand ('copy');

	PreventFocusOut = true;

	JQInput.focus ();
}

//...............................................................................................
function copyToClipboard (e, val_or_eval, idx, subidx = 0) {
	let t = performance.now ();

	if ((t - LastClickTime) > 500) {
		NumClicks = 1;
	} else{
		NumClicks += 1;
	}

	LastClickTime = t;
	let resp      = val_or_eval ? Evaluations [idx].math [subidx] : Validations [idx];

	writeToClipboard (NumClicks == 1 ? resp.nat : NumClicks == 2 ? resp.py : resp.tex);

	e.style.color      = 'transparent';
	e.style.background = 'black';

	setTimeout (function () {
		e.style.color      = 'black';
		e.style.background = 'transparent';
	}, 100);
}

//...............................................................................................
function updateOverlay (text, erridx, autocomplete) {
	ErrorIdx     = erridx;
	Autocomplete = autocomplete;

	if (ErrorIdx === null) {
		$('#OverlayGood').text (text);
		$('#OverlayError').text ('');

	} else {
		$('#OverlayGood').text (text.substr (0, ErrorIdx));
		$('#OverlayError').text (text.substr (ErrorIdx));
	}

	$('#OverlayAutocomplete').text (Autocomplete.join (''));
}

//...............................................................................................
function ajaxResponse (resp) {
	if (resp.mode == 'validate') {
		if (Validations [resp.idx] !== undefined && Validations [resp.idx].subidx >= resp.subidx) {
			return; // ignore out of order responses (which should never happen with single threaded server)
		}

		if (resp.tex !== null) {
			Validations [resp.idx] = resp;

			let eLogInput = document.getElementById ('LogInput' + resp.idx);

			let queue              = [];
			[queue, MJQueue.queue] = [MJQueue.queue, queue];

			MJQueue.queue = queue.filter (function (obj, idx, arr) { // remove previous pending updates to same element
				return obj.data [0].parentElement !== eLogInput;
			})

			let eLogInputWait              = document.getElementById ('LogInputWait' + resp.idx);
			eLogInputWait.style.visibility = '';

			let idMath = 'LogInputMath' + UniqueID ++;
			$(eLogInput).append (`<span id="${idMath}" onclick="copyToClipboard (this, 0, ${resp.idx})" style="visibility: hidden">$${resp.tex}$</span>`);
			let eMath  = document.getElementById (idMath);

			MJQueue.Push (['Typeset', MathJax.Hub, eMath, function () {
				if (eMath === eLogInput.children [eLogInput.children.length - 1]) {
					eLogInput.appendChild (eLogInputWait);

					for (let i = eLogInput.children.length - 3; i >= 0; i --) {
						eLogInput.removeChild (eLogInput.children [i]);
					}

					eLogInputWait.style.visibility = 'hidden';
					eMath.style.visibility         = '';

					logResize ();
					scrollToEnd (); // ???
				}
			}]);

			reprioritizeMJQueue ();
		}

		updateOverlay (JQInput.val (), resp.erridx, resp.autocomplete);

	} else { // resp.mode == 'evaluate'
		Evaluations [resp.idx] = resp;

		let eLogEval = document.getElementById ('LogEval' + resp.idx);

		eLogEval.removeChild (document.getElementById ('LogEvalWait' + resp.idx));

		if (resp.err !== undefined) { // error?
			if (resp.err.length > 1) {
				let idLogErrorHidden = 'LogErrorHidden' + resp.idx;
				$(eLogEval).append (`<div id="${idLogErrorHidden}" style="display: none"></div>`);
				var eLogErrorHidden  = document.getElementById (idLogErrorHidden);

				for (let i = 0; i < resp.err.length - 1; i ++) {
					$(eLogErrorHidden).append (`<div class="LogError">${resp.err [i].replace (/  /g, '&emsp;')}</div>`);
				}
			}

			let idLogErrorTriangle = 'LogErrorTriangle' + resp.idx;
			$(eLogEval).append (`<div class="LogError">${resp.err [resp.err.length - 1]}</div><div class="LogErrorTriange" id="LogErrorTriangle${resp.idx}">\u25b7</div>`);
			var eLogErrorTriangle  = document.getElementById (idLogErrorTriangle);

			$(eLogEval).click (function () {
				if (eLogErrorHidden.style.display === 'none') {
					eLogErrorHidden.style.display = 'block';
					eLogErrorTriangle.innerText   = '\u25bd';
				} else {
					eLogErrorHidden.style.display = 'none';
					eLogErrorTriangle.innerText   = '\u25b7';
				}

				logResize ();
			});

			logResize ();
			scrollToEnd ();

		} else { // no error
			if (resp.math !== undefined && resp.math.length) { // math results present?
				for (let subidx in resp.math) {
					let idLogEvalDiv  = `LogEvalDiv${resp.idx}_${subidx}`;
					let idLogEvalMath = `LogEvalMath${resp.idx}_${subidx}`;

					$(eLogEval).append (`<div id="${idLogEvalDiv}" class="LogEval"><span id="${idLogEvalMath}" style="visibility: hidden" onclick="copyToClipboard (this, 1, ${resp.idx}, ${subidx})">$${resp.math [subidx].tex}$</span>
							<img id="LogEvalWait${resp.idx}_${subidx}" class="LogWait" src="https://i.gifer.com/origin/3f/3face8da2a6c3dcd27cb4a1aaa32c926_w200.webp" width="16">
							</div>`);

					let eLogEvalDiv   = document.getElementById (idLogEvalDiv);
					let eLogEvalMath  = document.getElementById (idLogEvalMath);

					MJQueue.Push (['Typeset', MathJax.Hub, eLogEvalMath, function () {
						eLogEvalDiv.removeChild (document.getElementById (`LogEvalWait${resp.idx}_${subidx}`));

						eLogEvalMath.style.visibility = '';

						logResize ();
						scrollToEnd ();
					}]);

					reprioritizeMJQueue ();
				}
			}

			if (resp.msg !== undefined && resp.msg.length) { // message present?
				for (let msg of resp.msg) {
					$(eLogEval).append (`<div class="LogMsg">${msg.replace (/  /g, '&emsp;')}</div>`);
				}

				logResize ();
				scrollToEnd ();
			}
		}
	}
}

//...............................................................................................
function inputting (text, reset = false) {
	if (reset) {
		ErrorIdx     = null;
		Autocomplete = [];

		JQInput.val (text);
	}

	updateOverlay (text, ErrorIdx, Autocomplete);

	$.ajax ({
		url: URL,
		type: 'POST',
		cache: false,
		dataType: 'json',
		success: ajaxResponse,
		data: {
			mode: 'validate',
			idx: LogIdx,
			subidx: UniqueID ++,
			text: text,
		},
	});
}

//...............................................................................................
function inputted (text) {
	$.ajax ({
		url: URL,
		type: 'POST',
		cache: false,
		dataType: 'json',
		success: ajaxResponse,
		data: {
			mode: 'evaluate',
			idx: LogIdx,
			text: text,
		},
	});

	$('#LogEntry' + LogIdx).append (`
			<div class="LogEval" id="LogEval${LogIdx}">
				<img class="LogWait" id="LogEvalWait${LogIdx}" src="https://i.gifer.com/origin/3f/3face8da2a6c3dcd27cb4a1aaa32c926_w200.webp" width="16">
			</div>`);

	History.push (text);

	HistIdx = History.length;

	addLogEntry ();
	logResize ();
	scrollToEnd ();
}

//...............................................................................................
function inputKeypress (e) {
	if (e.which == 13) {
		s = JQInput.val ().trim ();

		if ((s && ErrorIdx === null) || s === '?') {
			if (!GreetingFadedOut) {
				GreetingFadedOut = true;
				$('#Greeting').fadeOut (3000);
			}

			if (s === 'help' || s === '?') {
				window.open (`${URL}help.html`);
				inputting ('', true);

				return false;
			}

			if (Autocomplete.length > 0) {
				s = s + Autocomplete.join ('');
				inputting (s);
			}

			JQInput.val ('');
			updateOverlay ('', null, []);
			inputted (s);

			return false;
		}

	} else if (e.which == 32) {
		if (!JQInput.val ()) {
			return false;
		}
	}

	return true;
}

//...............................................................................................
function inputKeydown (e) {
	if (e.code == 'Escape') {
		e.preventDefault ();

		if (JQInput.val ()) {
			HistIdx = History.length;
			inputting ('', true);

			return false;
		}

	} else if (e.code == 'Tab') {
		e.preventDefault ();
		$(this).focus ();

		return false;

	} else if (e.code == 'ArrowUp') {
		e.preventDefault ();

		if (HistIdx) {
			inputting (History [-- HistIdx], true);

			return false;
		}

	} else if (e.code == 'ArrowDown') {
		e.preventDefault ();

		if (HistIdx < History.length - 1) {
			inputting (History [++ HistIdx], true);

			return false;

		} else if (HistIdx != History.length) {
			HistIdx = History.length;
			inputting ('', true);

			return false;
		}

	} else if (e.code == 'ArrowRight') {
		if (JQInput.get (0).selectionStart === JQInput.val ().length && Autocomplete.length) {
			let text = JQInput.val ();

			if (Autocomplete [0] === ' \\right') {
				text         = text + Autocomplete.slice (0, 2).join ('');
				Autocomplete = Autocomplete.slice (2);

			} else {
				text         = text + Autocomplete [0];
				Autocomplete = Autocomplete.slice (1);
			}

			JQInput.val (text);
			inputting (text);
			// updateOverlay (text, ErrorIdx, Autocomplete);
		}
	}
}

//...............................................................................................
// function inputFocusout (e) {
// 	if (PreventFocusOut) {
// 		e.preventDefault ();
// 		$(this).focus ();

// 		return false;
// 	}
// }

//...............................................................................................
$(function () {
	window.JQInput = $('#Input');

	if (window.location.pathname != '/') {
		generateBG ();
		return;
	}

	let margin       = $('body').css ('margin-top');
	BodyMarginTop    = Number (margin.slice (0, margin.length - 2));
	margin           = $('body').css ('margin-bottom');
	BodyMarginBottom = Number (margin.slice (0, margin.length - 2));

	$('#Clipboard').prop ('readonly', true);
	$('#InputBG') [0].height = $('#InputBG').height ();

	JQInput.keypress (inputKeypress);
	JQInput.keydown (inputKeydown);
	// JQInput.focusout (inputFocusout);
	// JQInput.blur (inputFocusout);

	addLogEntry ();
	logResize ();
	resize ();
	monitorStuff ();
});


// $('#txtSearch').blur(function (event) {
// 	setTimeout(function () { $("#txtSearch").focus(); }, 20);
// });

// document.getElementById('txtSearch').addEventListener('blur', e => {
//   e.target.focus();
// });

// cursor_test = function (element) {
// 	if (!element.children.length && element.innerText == '∥') {
// 		console.log (element, element.classList);
// 		element.innerText = '|';
// 		element.classList.add ('blinking');
// 	}

// 	for (let e of element.children) {
// 		cursor_test (e);
// 	}
// }

// cursor_test (eLogInput.children [0]);
""".encode ("utf8"),

	'index.html': # index.html

r"""<!DOCTYPE html>
<html>
<head>

<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<link rel="icon" href="https://www.sympy.org/static/SymPy-Favicon.ico">
<title>SymPad</title>
<link rel="stylesheet" type="text/css" href="style.css">

<script type="text/javascript" src="https://code.jquery.com/jquery-3.4.1.js" integrity="sha256-WpOohJOqMqqyKL9FccASB9O0KwACQJpFTUBLTYOVvVU=" crossorigin="anonymous"></script>
<script type="text/javascript" src="script.js"></script>
<script type="text/x-mathjax-config">
	MathJax.Hub.Config ({
		messageStyle: "none",
		tex2jax: {inlineMath: [["$","$"], ["\\(","\\)"]]}
	});

	MathJax.Hub.Register.StartupHook ("End", readyMathJax);
</script>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-AMS_CHTML-full"></script>

</head>

<body onresize="resize ()">

<input id="Clipboard">
<canvas id="Background"></canvas>

<div id="Greeting">
	<div align="center">
		<h2>SymPad</h2>
		<h5>v0.4.3</h5>
		<br><br>
		Type '<b>help</b>' or '<b>?</b>' at any time for more information.
		<br>
		- or -
		<br>
		Type or click any of the following to get started:
	</div>
	<br><br>
	<a class="GreetingA" href="javascript:inputting ('cos**-1 x', true)">cos**-1 x</a>
	<a class="GreetingA" href="javascript:inputting ('\\log_2{8}', true)">\log_2{8}</a>
	<a class="GreetingA" href="javascript:inputting ('\\lim_{x\\to\\infty} 1/x', true)">\lim_{x\to\infty} 1/x</a>
	<a class="GreetingA" href="javascript:inputting ('Limit (\\frac1x, x, 0, dir=\'-\')', true)">Limit (\frac1x, x, 0, dir='-')</a>
	<a class="GreetingA" href="javascript:inputting ('\\sum_{n=0}**oo x^n / n!', true)">\sum_{n=0}**oo x^n / n!</a>
	<a class="GreetingA" href="javascript:inputting ('d**6 / dx dy**2 dz**3 x^3 y^3 z^3', true)">d**6 / dx dy**2 dz**3 x^3 y^3 z^3</a>
	<a class="GreetingA" href="javascript:inputting ('Derivative (\\int dx, x)', true)">Derivative (\int dx, x)</a>
	<a class="GreetingA" href="javascript:inputting ('Integral (e^{-x^2}, (x, 0, \\infty))', true)">Integral (e^{-x^2}, (x, 0, \infty))</a>
	<a class="GreetingA" href="javascript:inputting ('\\int_0^\\infty e^{-s t} dt', true)">\int_0^\infty e^{-s t} dt</a>
	<a class="GreetingA" href="javascript:inputting ('{{1,2},{3,4}}**-1', true)">{{1,2},{3,4}}**-1</a>
	<a class="GreetingA" href="javascript:inputting ('\\begin{matrix} A & B \\\\ C & D \\end{matrix} * {x, y}', true)">\<span></span>begin{matrix} A & B \\ C & D \<span></span>end{matrix} * {x, y}</a>
	<a class="GreetingA" href="javascript:inputting ('{{1,2,3},{4,5,6}}.transpose ()', true)">{{1,2,3},{4,5,6}}.transpose ()</a>
	<a class="GreetingA" href="javascript:inputting ('expand {x+1}**4', true)">expand {x+1}**4</a>
	<a class="GreetingA" href="javascript:inputting ('factor (x^3 + 3x^2 + 3x + 1)', true)">factor (x^3 + 3x^2 + 3x + 1)</a>
	<a class="GreetingA" href="javascript:inputting ('series (e^x, x, 0, 5)', true)">series (e^x, x, 0, 5)</a>
	<a class="GreetingA" href="javascript:inputting ('x if 1 &lt; 2 else y', true)">x if 1 &lt; 2 else y</a>

	<br><br>
	<div align="center">
	Copyright (c) 2019 Tomasz Pytel. <a href="https://github.com/Pristine-Cat/SymPad" target="_blank" style="color: #0007">SymPad on GitHub</a>
	</div>
</div>

<div id="Log"></div>

<canvas id="InputBG"></canvas>
<input id="Input" oninput="inputting (this.value)" autofocus>
<div id="InputOverlay"><span id="OverlayGood"></span><span id="OverlayError"></span><span id="OverlayAutocomplete"></span></div>

</body>
</html>""".encode ("utf8"),

	'help.html': # help.html

r"""<!DOCTYPE html>
<html>
<head>

<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<link rel="icon" href="https://www.sympy.org/static/SymPy-Favicon.ico">
<title>SymPad Help</title>
<link rel="stylesheet" type="text/css" href="style.css">

<style>
	body { margin: 3em 4em; }
	h2 { margin: 2em 0 1em 0; }
	h4 { margin: 1.5em 0 0.5em 0; }
	p { margin: 0 0 1.2em 1em; line-height: 150%; }
	i { color: #0008; }
	del { color: red; }
</style>

<script type="text/javascript" src="https://code.jquery.com/jquery-3.4.1.js" integrity="sha256-WpOohJOqMqqyKL9FccASB9O0KwACQJpFTUBLTYOVvVU=" crossorigin="anonymous"></script>
<script type="text/javascript" src="script.js"></script>
<script type="text/x-mathjax-config">
	MathJax.Hub.Config ({
		messageStyle: "none",
		tex2jax: {inlineMath: [["$","$"], ["\\(","\\)"]]}
	});
</script>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-AMS_CHTML-full"></script>

</head>

<body onresize="generateBG ()">

<canvas id="Background"></canvas>

<h1 align="center" style="margin: 0">SymPad</h1>
<h4 align="center" style="margin: 0">v0.4.3</h4>

<h2>Introduction</h2>

<p>
SymPad is a simple single script symbolic calculator / scratchpad using SymPy for the math and MathJax for the display in a browser.
It is a labor of love and grew out of a desire for an easy way to calculate a quick integral while studying some math without having to start a shell every time and import a package or fire up a browser and navigate to a site (technincally that last bit is exactly what happens but the response time is better :)
This desire for simplicity led to the single script option "sympad.py" which I could plop down on my desktop and execute when needed.
User input is intended to be quick, easy and intuitive and is displayed in symbolic form as it is being entered.
Sympad will accept Python expressions, LaTeX formatting, unicode math symbols and a native shorthand intended for quick entry, or a mix of all of these.
The input will be evaluated symbolically or numerically with the results being copy/pasteable in Python or LaTeX formats, so it acts as a translator as well.
</p>
<h4>Quick Start</h4>

<p>
The best way to see what SymPad can do is by doing, so try entering any of the following into SymPad:
</p><p>
cos**-1 x<br>
\log_2{8}<br>
\lim_{x\to\infty} 1/x<br>
Limit (\frac1x, x, 0, dir='-')<br>
\sum_{n=0}**oo x^n / n!<br>
d**6 / dx dy**2 dz**3 x^3 y^3 z^3<br>
Derivative (\int dx, x)<br>
Integral (e^{-x^2}, (x, 0, \infty))<br>
\int_0^\infty e^{-s t} dt<br>
{{1,2},{3,4}}**-1<br>
\<span></span>begin{matrix} A & B \\ C & D \<span></span>end{matrix} * {x, y}<br>
{{1,2,3},{4,5,6}}.transpose ()<br>
expand {x+1}**4<br>
factor (x^3 + 3x^2 + 3x + 1)<br>
series (e^x, x, 0, 5)<br>
x if 1 &lt; 2 else y<br>
</p>

<h4>Multiline examples</h4>

<p>
Enter the lines that follow one by one to see the effect:
</p><p>
1<br>
expand (_(x+1))<br>
expand (_(x+1))<i>&emsp;**(or press the up arrow)</i><br>
expand (_(x+1))<i>&emsp;...</i><br>
</p><p>
Or the following:
</p><p>
a, b = 1, 1<br>
a, b = b, a + b<br>
a, b = b, a + b<i>&emsp;**(or press the up arrow)</i><br>
a, b = b, a + b<i>&emsp;...</i><br>
</p>

<h4>Usage</h4>

<p>
You enter expresstions and they get evaluated.
The expressions may be in normal Pythonic style like "<b>a * (b + sin (x)**2 + 3/4) / 2</b>", LaTeX such as "<b>a\frac{b+\sin^2{x}+\frac34}{2}</b>" or a mix "<b>a * (b + \sin**x{2} + \frac34) / 2</b>".
The input is displayed symbolically as you type.
Input history is supported with the up and down arrows.
SymPad will give some limited options for autocompletion for certain expressions sometimes, this mostly means that you will not have to close parentheses.
</p><p>
The symbolic expressions can be copied to the clipboard in various formats.
Single-click for a simple native format meant to be pasted back into the input field.
A double click-copies the expression in Python format suitable for pasting into a Python shell or source file.
Finally, a triple-click will copy the expression in LaTeX format.
The single-click native and double-click Python formats should always be pasteable back into SymPad whereas the LaTeX format may or may not be depending on what elements are present.
</p>

<h2>Types</h2>

<h4>Numbers</h4>

<p>
Numbers take the standard integer or floating point form or exponential form such as 123, -2.567, 1e+100, 3E-45 or -1.521e22.
The precision for all SymPy Floats used in evaluation is set to the highest precision number present in the equation, so if you ask for the cosine of a number with 50 decimal digits your answer will have at least 50 decimal digits.
</p><p>
Keep in mind that "<b>e</b>" or "<b>E</b>" is the Euler"s number constant $e$ and if you are trying to enter 2 times $e$ plus 22 then do not write it all together as "<b>2e+22</b>" as this will be interpreted to be "<b>2 * 10^22</b>".
Instead, use spaces and/or explicit multiplication: "<b>2 * e + 22</b>".
Imaginary numbers are entered using the imaginary unit "<b>i</b>" or "<b>I</b>" depending on preference, no Pythonic "<b>j</b>" option at the moment but it can be hacked by setting "<b>j = i</b>" in SymPad.
</p>

<h4>Variables</h4>

<p>
Variable names can be a mix of Python and LaTeX format, they can be multi-character but cannot start with an underscore "<b>_</b>" or a number though they may contain those.
Standard identifiers are accepted as well as single Greek letters optionally preceded by a slash such as "<b>\alpha</b>" ($\alpha$), "<b>epsilon</b>" ($\epsilon$) or "<b>\Psi</b>" ($\Psi$).
The Greek letters recognized and rendered in ... Greek ... are only those normally present within LaTeX which can not be visually confused with Latin letters.
Those Greek letters are accepted in unicode as well along with a few mathematical symbols (∞, ≠, ≤, ≥, ∂, ∑, ∫).
</p><p>
The variable names "<b>i</b>", "<b>e</b>" and "<b>\pi</b>" represent their respective mathematical constants $i$, $e$ and $\pi$.
"<b>pi</b>" and "<b>oo</b>" are also available for $\pi$ and $\infty$.
Python's "<b>None</b>", "<b>True</b>" and "<b>False</b>" are also present.
Variable names may be followed by various primes ' such as "<b> var' </b>" ($var'$) or "<b> \omega'' </b>" ($\omega''$).
By default, the lowercase "<b>e</b>" and "<b>i</b>" letters are used to represent Euler's number and the imaginary unit instead of the default SymPy uppercase "<b>E</b>" and "<b>I</b>".
This is objectively prettier, but can be changed via the "<b>$sympyEI (True)</b>" and "<b>$sympyEI (False)</b>" function.
The SymPy constant usage can also be activated via the command line switch "<b>--sympyEI</b>".
</p><p>
Differentials are entered as "<b>dx</b>", "<b>partialx</b>", "<b>\partialx</b>", "<b>\partial x</b>" or "<b>∂x</b>" and are treated as a single variable.
If you want to enter "<b>d</b>" * "<b>x</b>" multiplied implicitly then put a space between them or two spaces between the "<b>\partial</b>" and the "<b>x</b>".
There is nothing special about differential variables other than their specific use in differentiation and integration.
</p><p>
Variables may be assigned values, references to other variables or even entire expressions which will subsequently be substituted for those variables in any future expression evaluation.
They may also be assigned a user function which allows you to use them as macro expression functions, that is covered in the section on functions.
</p>

<h4>Vectors and Matrices</h4>

<p>
These are specified using curly braces with commas.
Vectors are passed as a single level of curlys such as "<b>{1, 2}</b>" or "<b>{x, y, z}</b>" and these are interpreted as column matrices.
Matrices are passed as nested rows of curlys.
A 2x3 matrix would be specified as  "<b>{{1, 2, 3}, {4, 5, 6}}</b>", a 1x3 would be "<b>{{1, 2, 3},}</b>" and a 3x1 would be either "<b>{{1,}, {2,}, {3,}}</b>" or just "<b>{1, 2, 3}</b>" since this is equivalent.
Note the trailing commas which are needed for the same reason as in Python for tuples of one element (otherwise the curlys would be treated as parenteses instead of vectors / matrices).
These can also be entered using LaTeX "<b>\<span></span>begin{(v|b|p|)matrix} \<span></span>end{(v|b|p|)matrix}</b>" format.
</p>

<h4>Piecewise Expressions</h4>

<p>
These are supported and can be entered as SymPy "<b>Piecewise</b>" functions, LaTeX "<b>\<span></span>begin{cases} \<span></span>end{cases}</b>" notation or the native Python-like conditional expressions of the form "<b>a if condition else b</b>".
They may be arbitrarily long - "<b>a if condition1 else b if condition2 else ...</b>" and may leave off the last "<b>else</b>" which is equivalent to a SymPy "<b>Piecewise</b>" function without a terminating "<b>True</b>" condition.
</p>

<h4>Strings</h4>

<p>
These exist for the sole purpose of passing string hints or other arguments to SymPy functions. They work as expected being enclosed by single or double quotes and
supporting escape sequences. For example "<b>Limit (1/x, x, 0, '-')</b>".
</p>

<h4>Lists and Tuples</h4>

<p>
Standard Python bracket enclosed lists and optionally parentheses enclosed tuples are accepted.
Like strings these exist for the purpose of passing parameters to functions like "<b>Matrix ([[1,2],[3,4]])</b>".
</p>

<h2>Operations</h2>

<h4>Addition and Multiplication</h4>

<p>
Addition is addition and subtraction is subtraction: "<b>a + b</b>", "<b>a - b</b>".
Multiplication is explicit with a "<b>*</b>" operator or implicit simply by writing two symbols next to each other with a space in between so that "<b>a * b</b>" is the same as "<b>a b</b>".
There is however a difference between the two in that the implicit version has a higher precedence than the explicit, which means that explicit multiplication will end a limit, sum, derivative or division "<b>/</b>" expression whereas implicit multiplication will not, e.g. "<b>1/x y</b>" = $\frac{1}{x y}$ whereas "<b>1/x*y</b>" = $\frac{1}{x} \cdot y$.
</p><p>
Division also has two operators, the normal "<b>/</b>" which has a fairly low precedence and the LaTeX "<b>\frac</b>" version which has a very high precedence, even higher than exponentiation.
So high in fact that parentheses are not needed if using "<b>\frac</b>" as an exponent as in "<b>x^\frac{1}{2}</b>" = $x^\frac{1}{2}$.
The "<b>\frac</b>" operation also does not need parentheses if using single digit operands or single letter variables (Latin or Greek) such as "<b>\frac12</b>" = $\frac12$ or "<b>\frac\alpha\beta</b>" = $\frac\alpha\beta$.
</p>

<h4>Exponentiation</h4>

<p>
There are two power opearators "<b>^</b>" and "<b>**</b>". They have the same precedence and can be used interchangeably but follow slightly different
parsing rules. The "<b>^</b>" operator follows LaTeX rules which only allow a single positive digit or letter variable (Lating or Greek) without the use
of curly braces whereas the "<b>**</b>" follows Python rules which allow negative values or variables or functions. To illustrate the diffference:
"<b>x**-2</b>" = $x^{-2}$ whereas "<b>x^-2</b>" = $x^-2$ (which makes no sense). Also, "<b>e**ln(x)</b>" will work as expected $e^{\ln(x)}$ whereas
"<b>e^ln(x)</b>" = $e^ln(x)$.
</p>

<h4>Logarithms</h4>

<p>
The natural logarithm of x is specified by "<b>lnx</b>", "<b>\ln x</b>", "<b>log x</b>", "<b>\log{x}</b>". A logarithm in a specific base is specified
by "<b>\log_b x</b>" = $\log_b x$, "<b>\log_{10}(1000)</b>" = $\log_{10} {1000}$ = 3, etc...
</p>

<h4>Roots</h4>

<p>
The square root of x ($\sqrt{x}$) may be entered in any of these forms "<b>sqrtx</b>", "<b>\sqrt x</b>", "<b>sqrt (x)</b>", "<b>\sqrt{x}</b>", with or without the slash.
The cube (or any other) root is similar, $\sqrt[3]x$ = "<b>sqrt[3]x</b>", "<b>sqrt[3] (x)</b>" or "<b>\sqrt[3] {x}</b>".
</p>

<h4>Factorial</h4>

<p>
"<b>4!</b>" = "<b>24</b>", "<b>x!</b>" = "<b>factorial(x)</b>", "<b>(-0.5)!</b>" = "<b>1.77245385090552</b>" and "<b>simplify(x!/x)</b>" = "<b>gamma(x)</b>".
</p>

<h4>Limits</h4>

<p>
To take the limit of an expression "<b>z</b>" as variable "<b>x</b>" approaches "<b>y</b>" enter "<b>\lim_{x \to y} (z)</b>" = $\lim_{x\to y} (z)$.
This will only give the limit if it exists and is the same when approaching from both directions, unlike SymPy which defaults to approaching from the
positive direction. To specify a direction add "<b>^+</b>" or "<b>^-</b>" to the equation as such: "<b>\lim_{x \to 0^+} 1/x</b>" = $\lim_{x\to 0^+}
\frac1x$ = $\infty$ and "<b>\lim_{x \to 0^-} 1/x</b>" = $\lim_{x\to 0^-} \frac1x$ = $-\infty$. Addition and explicit multiplication terminate a limit
expression. Limits may also be entered using the standard SymPy syntax "<b>Limit (expression, variable, to)</b>", this defaults to limit from positive
direction like SymPy, or you may specify a direction "<b>Limit (expression, variable, to, dir='+-')</b>".
</p>

<h4>Sums</h4>

<p>
The summation (finite or infinite) of expression "<b>z</b>" as variable "<b>n</b>" ranges from "<b>a</b>" to "<b>b</b>" is written as "<b>\sum_{n=a}^b
(z)</b>" = $\sum_{n=a}^b (z)$. Iterated sums work as expected, "<b>\sum_{n=1}^3 \sum_{m=1}^n m</b>" = $\sum_{n=1}^3 \sum_{m=1}^n m$ = 10. Addition and
explicit multiplication terminate a sum expression.
Sums may also be entered using the standard SymPy syntax "<b>Sum (expression, (variable, from, to))</b>".
</p>

<h4>Differentiation</h4>

<p>
The derivative of expression "<b>z</b>" with respect to "<b>x</b>" is entered as "<b>d/dx z</b>" or "<b>\frac{d}{dx} z</b>" = $\frac{d}{dx} z$. The
second derivative is "<b>d^2/dx^2 (z)</b>" or "<b>\frac{d^2}{dx^2} (z)</b>" = $\frac{d^2}{dx^2} (z)$. Using "<b>\partial</b>" ($\partial$) is allowed but
must be consistent within the expression. Mixed derivatives are entered as "<b>d^2 / dx dy (z)</b>" or "<b>\partial^2 / \partial x\partial y (z)</b>" =
$\frac{\partial^2}{\partial x\partial y} (z)$. Derivatives may also be entered using the standard SymPy syntax "<b>Derivative (expression, var1, var2,
power2, ...)</b>".
</p>

<h4>Integration</h4>

<p>
The anti-derivative of expression "<b>z</b>" with respect to x is written as "<b>\int z dx</b>" = $\int z\ dx$. The definite integral from "<b>a</b>" to
"<b>b</b>" is "<b>\int_a^b z dx</b>" = $\int_a^b z\ dx$. "<b>\int dx/x</b>" = $\int \frac1x\ dx$. Iterated and improper integrals also work. Integrals
may also be entered using the standard SymPy syntax "<b>Integral (expression, (variable, from, to))</b>".
</p>

<h4>(In)equalities</h4>

<p>
Are parsed from the standard Python "<b>=, ==, !=, &lt;, &lt;=, &gt;, &gt;=</b>" or LaTeX "<b>\ne, \neq, \lt, \le, \gt, \ge</b>" symbols.
Currently only a single comparison is allowed so an expression like "<b>0 &lt;= x &lt;= 2</b>" is not valid.
Note that the "<b>=</b>" and "<b>==</b>" operators are equivalent for SymPy and mapped to the same "<b>Eq</b>" object in expressions but the single "<b>=</b>" operator has a lower precedence than the others and is used by SymPad for variable assignment whereas the double "<b>==</b>" only ever implies comparison.
</p>

<h4>Parentheses</h4>

<p>
Explicit "<b>( )</b>" or implicit curly "<b>{ }</b>" parentheses allow prioritization of lower precedence operations over higher ones as usual and also
delineate an expression as an input to a function. They may be used interchangeably for single expressions, the only difference being that the implicit
version is not drawn if it does not need to be. The case where explicit "<b>( )</b>" parentheses are needed ... explicitly ... is when calling functions
in general and always when calling functions which take multiple parameters like "<b>max(1,2,3)</b>". The curly braces are used as shorthand for vectors
and matrices if commas are present, but that is a different syntactic usage, curlys with no commas are essentially invisible parentheses.
</p>

<h4>Member Access</h4>

<p>
You can access member data or functions of an expression just like in Python with the "<b>.</b>" operator.
If the attribute name following the dot is followed by a parenthesized expression then it will be treated as a function call instead of an implicit multiplication, otherwise it is a data member.
For example, two ways to get the transpose of a matrix are "<b>{{1,2,3},{4,5,6}}.T</b>" and "<b>{{1,2,3},{4,5,6}}.transpose ()</b>".
</p>

<h4>Variable Assignment</h4>

<p>
Using the syntax "<b>var = expression</b>" you can assign some value to be substituted for that variable in all expressions.
For example, doing "<b>x = pi</b>" and then evaluating "<b>cos x</b>" will give you "<b>-1</b>".
Anything can be assigned to any valid variable like mathematical expressions, Python objects like strings or lists, user lambda functions or even references to other variables.
To delete an assignment use the "<b>del var</b>" function, to delete all assignments do "<b>delall</b>" and to see what variables are currently assigned to, use the "<b>vars</b>" function.
</p><p>
Tuple assignment is supported and as in Python the source can be another tuple or a single iterable object like "<b>x, y = 1, 2</b>".
A useless example of iterable assignment would be setting "<b> a, b, c = 'str' </b>" which would give you "<b> a = 's' </b>", "<b> b = 't' </b>" and "<b> c = 'r' </b>".
</p><p>
There are two distinct types of assignment that can occur and you should be aware of the difference between them.
Copy assignment is the standard type of assignment used by default in most computer languages where if you start with "<b>x = 1</b>" and you then enter "<b>y = x</b>" then the value "<b>1</b>" will be copied to the "<b>y</b>" variable.
The value of "<b>y</b>" will be independent of whatever else happens to the variable "<b>x</b>" after this.
</p><p>
The other kind of assignment is a reference assignment which will map the source variable instead of copying its value to the target.
This means that if you have a reference set like "<b>y = x</b>" and the value of "<b>x</b>" changes then the value of "<b>y</b>" will reflect this new value as well.
The reference assignment happens if you try to assign variables which do not exist, so setting "<b>y = x</b>" before "<b>x</b>" has been created will result in a reference.
Otherwise you can force a reference by using the "<b>@()</b>" pseudo-function.
Doing "<b>y = @x</b>" will create a reference to "<b>x</b>" itself instead of copying the value if it exists.
The "<b>@(expr)</b>" function technically prevents variable remapping for the expression it encompasses, so if you have the variable "<b>x = 2</b>" set and you do "<b>@(x)</b>" then you will get "<b>x</b>" and not "<b>2</b>".
</p>

<h2>Functions</h2>
<p>
There are two types of functions made available in SymPad - all the SymPy functions are available directly just by typing their name, as well as user created lambda functions assigned to variables.
In addition, member functions of objects are supported an callable like "<b>Matrix ([1,2,3]).transpose ()</b>".
All functions may take multiple comma-separated arguments and the SymPy functions also optionally take keyword arguments.
</p>

<h4>SymPy Functions</h4>

<p>
Almost all SymPy function and objects from the top level of the SymPy module are made available directly for calling by their name like "<b>tan(x)</b>", the only restriction being they must be longer than a single character and may not begin with an underscore.
This means no "<b>N()</b>", "<b>S()</b>" or "<b>O()</b>" directly, though those and functions and others beginning with an underscore as well as many __builtins__ can still be accessed with the "<b>$</b>" function override escape character, for example "<b>$print ('Hello World...')</b>".
Only the "safe" __builtin__ functions are specifically made available, functions like "<b>eval</b>", "<b>exec</b>" and many more have been left out and are not accessible.
To numerically evaluate the value of "<b>sin (2)</b>" you use the "<b>$</b>" escape character with the "<b>N()</b>" function like "<b>$N (sin (2))</b>", or just use the member function "<b>sin (2).evalf ()</b>".
</p><p>
The standard trigonometric and hyperbolic functions and their inverses can be entered as usual, the forward functions with or without a leading slash: "<b>sin</b>", "<b>\coth</b>".
The inverses are entered as Pythonic functions without a slash like "<b>atan</b>" or "<b>acscsh</b>" and the LaTeX versions take a slash and and are spelled out "<b>\arctan</b>".
The inverses may also be specified using the common mathematical syntax: "<b>\tan^{-1}x</b>" or "<b>cos**-1 x</b>".
This form of exponentiating a function is extended as an input shortcut to all top-level functions so that typing "<b>ln**2x</b>" is a quick way to enter "<b>(ln(x))**2</b>".
This does not apply to member functions or user created lambda functions.
Keep in mind that the "<b>-1</b>" exponent in this context is just a -1 and does not specify the inverse function as it does for the forward trigonometric and hyperbolic functions.
</p><p>
Top-level functions also don't require explicit parentheses in order to allow quick entry like "<b>sqrt 2</b>" or "<b>sin**-1x</b>" but for any parameter more complicated than another function or variable to a power they will be needed.
Functions which take zero or more than one single parameter, as well as member functions such as "<b>{{1, 1}, {0, 1}}.det()</b>" and lambdas always require explicit parentheses.
Many functions which have a common mathematical display style are translated on the fly for rendering in that style.
These include the functions "<b>abs/Abs (x)</b>" which are rendered as the standard bar syntax for absolute value "<b>|x|</b>", the "<b>factorial (x)</b>" function becomes "<b>x!</b>" and "<b>exp (x)</b>" displays as "<b>e^x</b>".
Some other functions which are translated are "<b>Derivative</b>", "<b>diff</b>", "<b>Integral</b>", "<b>integrate</b>", "<b>Limit</b>", "<b>limit</b>", "<b>Matrix</b>", "<b>Piecewise</b>", "<b>pow</b>", "<b>Pow</b>" and "<b>Sum</b>", and more...
</p>

<h4>Lambda Functions</h4>

<p>
User created lambda functions are supported and are specified the same way as Python lambdas - "<b>lambda x, y: (x+y)**2</b>".
In order to make use of them though you must assign them to a variable like "<b>f = lambda x: x**2</b>", now when you call "<b>f(3)</b>" you will get "<b>9</b>" as the result.
When created, lambda functions will copy the global value of any variables which are not lambda arguments and this will be fixed for the life of the lambda.
If you want a lambda to use the value of a global variable at the time the lambda is evaluated, rather than when it is defined, then wrap the instance of the variable in the lambda using the "<b>@()</b>" pseudo-function.
Lambda functions may reference other lambda functions as long as those are defined at the time of creation.
Lambda recursion is currently not supported.
</p><p>
Normally when you enter an expression into SymPad and hit Enter that expression is evaluated and "<b>doit()</b>" is called on it to attempt to symbolically evaluate an answer.
This may not always be desirable, like maybe in a lambda function, since when you enter a lambda function it is evaluated before it is assigned to a variable.
This means that if you do "<b>f = lambda x: \int x dx</b>" you will wind up with a lambda function which is equivalent to "<b>f = lambda x: 1/2 x**2</b>" instead of the integral expression.
In order to prevent evaluation of the integral on assignment and embed the operation itself within the lambda use the "<b>%()</b>" stop evaluation pseudo-function.
This function essentially defers evaluation of an expression for one round.
This will result in an assignment of "<b>f = lambda x: \int x dx</b>" if you define it as "<b>f = lambda x: %(\int x dx)</b>" instead of the result of the integral and this integral itself will be evaluated any time the lambda function is invoked.
</p><p>
This pseudo-function takes an optional count as a second argument.
The default count is 1 round of evaluation, but you may set it to 2 or more to defer evaluation for that many rounds, though I'm not sure if a finite count would be useful for anything.
What could be useful is a count of infinity, this would freeze the expression as it is and never evaluate.
</p>

<h4>Functions, Parentheses and Implicit Multiplication</h4>
<div style="color: red">
<p>This...</p>
</div>

<h2>Notes</h2>

<p>
<b>WARNING!</b> This http server implementation is nowhere near secure, this as well as the posibility of execution of arbitrary Python functions means you should never leave this server open to the internet by serving on an IP address visible to the external world.
</p><p>
There is a special use for the "<b>_</b>" underscore character which is the same as in the Python interactive shell in that it represents the last expression successfully evaluated.
To see this in action type in "<b>1</b>" and hit Enter, then type in "<b>expand ((x+1)*_)</b>" and hit Enter.
Repeat this several times using the up arrow.
</p><p>
Due to mixing operators from Python and LaTeX the grammar may be a little wonky in places so if something doesn't seem to work as it should try wrapping it in parentheses or putting a space between the problematic elements.
</p><p>
There is a namespace collision between the Greek letters "<b>beta</b>", "<b>zeta</b>", "<b>Gamma</b>" and "<b>Lambda</b>" and SymPy functions with those names (well, lowercase SymPy gamma() really, but it is represented normally with the uppercase letter).
This has been resolved in favor of variable names for "<b>beta</b>" and "<b>Lambda</b>", which means that in order to access those functions in SymPy you have to use "<b>$beta()</b>" or "<b>$Lambda()</b>", and in favor of function names for "<b>zeta</b>" and "<b>Gamma</b>".
This means that the LaTeX expression "<b>\zeta x</b>" means the Riemann zeta function of "<b>x</b>" and "<b>\Gamma x</b>" means "<b>gamma (x)</b>".
</p><p>
You can always tell whether SymPad will treat an identifier as a function or a variable by looking at the font which is used for the name, it is different for functions vs. variables.
Also, SymPad will give you an empty set of parentheses as an autocomplete option when it recognizes a function name (this only works for top-level functions).
</p><p>
If you are getting results which are just plain wrong, check to see if you have any variables mapped which would be changing the evaluation.
</p><p>
There are many SymPy objects which SymPad does not understand natively yet.
In any case where such an object is the result of an evalutation then the SymPy LaTeX representation will be used for the displayed answer and the SymPy str version of the element will be used in the native representation string.
This should allow you to continue working with the calculation.
</p>

<br><br>
<div align="center">
Copyright (c) 2019 Tomasz Pytel, All rights reserved.

SymPad on GitHub: <a target="_blank" href="https://github.com/Pristine-Cat/SymPad">https://github.com/Pristine-Cat/SymPad</a>
</div>

</body>
</html>""".encode ("utf8"),
}

import re
import types

#...............................................................................................
class Incomplete (Exception):
	def __init__ (self, red):
		self.red = red

class Token (str):
	def __new__ (cls, str_, text = None, pos = None, grps = None):
		self      = str.__new__ (cls, str_)
		self.text = text or ''
		self.pos  = pos
		self.grp  = () if not grps else grps

		return self

class State (tuple): # easier on the eyes
	def __new__ (cls, *args):
		return tuple.__new__ (cls, args)

	def __init__ (self, *args): # idx = state index, sym = symbol (TOKEN or 'expression'), red = reduction (if present)
		if len (self) == 2:
			self.idx, self.sym = self
		else: # must be 3
			self.idx, self.sym, self.red = self

class Parser:
	_PARSER_TABLES = '' # placeholders so pylint doesn't have a fit
	_PARSER_TOP    = ''
	TOKENS         = {}

	_rec_SYMBOL_NUMTAIL = re.compile (r'(.*[^_\d])(_?\d+)?') # symbol names in code have extra digits at end for uniqueness which are discarded

	def __init__ (self):
		if isinstance (self._PARSER_TABLES, bytes):
			import ast, base64, zlib
			symbols, rules, strules, terms, nterms = ast.literal_eval (zlib.decompress (base64.b64decode (self._PARSER_TABLES)).decode ('utf8'))
		else:
			symbols, rules, strules, terms, nterms = self._PARSER_TABLES

		self.tokgrps = {} # {'token': (groups pos start, groups pos end), ...}
		tokpats      = list (self.TOKENS.items ())
		pos          = 0

		for tok, pat in tokpats:
			l                   = re.compile (pat).groups + 1
			self.tokgrps [tok]  = (pos, pos + l)
			pos                += l

		self.tokre   = '|'.join (f'(?P<{tok}>{pat})' for tok, pat in tokpats)
		self.tokrec  = re.compile (self.tokre)
		self.rules   = [(0, (symbols [-1]))] + [(symbols [r [0]], tuple (symbols [s] for s in (r [1] if isinstance (r [1], tuple) else (r [1],)))) for r in rules]
		self.strules = [[t if isinstance (t, tuple) else (t, 0) for t in (sr if isinstance (sr, list) else [sr])] for sr in strules]
		states       = max (max (max (t [1]) for t in terms), max (max (t [1]) for t in nterms)) + 1
		self.terms   = [{} for _ in range (states)] # [{'symbol': [+shift or -reduce, conflict +shift or -reduce or None], ...}] - index by state num then terminal
		self.nterms  = [{} for _ in range (states)] # [{'symbol': +shift or -reduce, ...}] - index by state num then non-terminal
		self.rfuncs  = [None] # first rule is always None

		for t in terms:
			sym, sts, acts, confs = t if len (t) == 4 else t + (None,)
			sym                   = symbols [sym]

			for st, act in zip (sts, acts):
				self.terms [st] [sym] = (act, None)

			if confs:
				for st, act in confs.items ():
					self.terms [st] [sym] = (self.terms [st] [sym] [0], act)

		for sym, sts, acts in nterms:
			for st, act in zip (sts, acts):
				self.nterms [st] [symbols [sym]] = act

		prods = {} # {('production', ('symbol', ...)): func, ...}

		for name in dir (self):
			obj = getattr (self, name)

			if name [0] != '_' and type (obj) is types.MethodType and obj.__code__.co_argcount >= 1: # 2: allow empty productions
				m = Parser._rec_SYMBOL_NUMTAIL.match (name)

				if m:
					parms = tuple (p if p in self.TOKENS else Parser._rec_SYMBOL_NUMTAIL.match (p).group (1) \
							for p in obj.__code__.co_varnames [1 : obj.__code__.co_argcount])
					prods [(m.group (1), parms)] = obj

		for irule in range (1, len (self.rules)):
			func = prods.get (self.rules [irule] [:2])

			if not func:
				raise NameError (f"no method for rule '{self.rules [irule] [0]} -> {''' '''.join (self.rules [irule] [1])}'")

			self.rfuncs.append (func)

	def tokenize (self, text):
		tokens = []
		end    = len (text)
		pos    = 0

		while pos < end:
			m = self.tokrec.match (text, pos)

			if m is None:
				tokens.append (Token ('$err', text [pos], pos))

				break

			else:
				if m.lastgroup != 'ignore':
					tok  = m.lastgroup
					s, e = self.tokgrps [tok]
					grps = m.groups () [s : e]

					tokens.append (Token (tok, grps [0], pos, grps [1:]))

				pos += len (m.group (0))

		tokens.append (Token ('$end', '', pos))

		return tokens

	#...............................................................................................
	def parse_getextrastate (self):
		return None

	def parse_setextrastate (self, state):
		pass

	def parse_error (self):
		return False # True if state fixed to continue parsing, False to fail

	def parse_success (self, red):
		'NO PARSE_SUCCESS'
		return None # True to contunue checking conflict backtracks, False to stop and return

	def parse (self, src):
		has_parse_success = (self.parse_success.__doc__ != 'NO PARSE_SUCCESS')

		rules, terms, nterms, rfuncs = self.rules, self.terms, self.nterms, self.rfuncs

		tokens = self.tokenize (src)
		tokidx = 0
		cstack = [] # [(action, tokidx, stack, stidx, extra state), ...] # conflict backtrack stack
		stack  = [State (0, None, None)] # [(stidx, symbol, reduction) or (stidx, token), ...]
		stidx  = 0
		rederr = None # reduction function raised exception (SyntaxError or Incomplete)

		while 1:
			if not rederr:
				tok       = tokens [tokidx]
				act, conf = terms [stidx].get (tok, (None, None))

			if rederr or act is None:
				self.tokens, self.tokidx, self.cstack, self.stack, self.stidx, self.tok, self.rederr = \
						tokens, tokidx, cstack, stack, stidx, tok, rederr

				rederr = None

				if tok == '$end' and stidx == 1 and len (stack) == 2 and stack [1] [1] == rules [0] [1]:
					if not has_parse_success:
						return stack [1].red

					if not self.parse_success (stack [1].red) or not cstack:
						return None

				elif self.parse_error ():
					tokidx, stidx = self.tokidx, self.stidx

					continue

				elif not cstack:
					if has_parse_success: # do not raise SyntaxError if parser relies on parse_success
						return None

					# if self.rederr is not None: # THIS IS COMMENTED OUT BECAUSE IS NOT USED HERE AND PYLINT DOESN'T LIKE IT!
					# 	raise self.rederr # re-raise exception from last reduction function if present

					raise SyntaxError ( \
						'unexpected end of input' if tok == '$end' else \
						f'invalid token {tok.text!r}' if tok == '$err' else \
						f'invalid syntax {src [tok.pos : tok.pos + 16]!r}')

				act, tokens, tokidx, stack, stidx, estate = cstack.pop ()
				tok                                       = tokens [tokidx]

				self.parse_setextrastate (estate)

			elif conf is not None:
				cstack.append ((conf, tokens [:], tokidx, stack [:], stidx, self.parse_getextrastate ()))

			if act > 0:
				tokidx += 1
				stidx   = act

				stack.append (State (stidx, tok))

			else:
				rule  = rules [-act]
				rnlen = -len (rule [1])
				prod  = rule [0]

				try:
					red = rfuncs [-act] (*((t [-1] for t in stack [rnlen:]) if rnlen else ()))

				except SyntaxError as e:
					rederr = e or True # why did I do this?

					continue

				except Incomplete as e:
					rederr = e
					red    = e.red

				if rnlen:
					del stack [rnlen:]

				stidx = nterms [stack [-1].idx] [prod]

				stack.append (State (stidx, prod, red))

class lalr1: # for single script
	Incomplete = Incomplete
	Token      = Token
	State      = State
	Parser     = Parser
# Base classes for abstract math syntax tree, tuple based.
#
# ('=', 'rel', lhs, rhs)             - equality of type 'rel' relating Left-Hand-Side and Right-Hand-Side
# ('#', 'num')                       - real numbers represented as strings to pass on maximum precision to sympy
# ('@', 'var')                       - variable name, can take forms: 'x', "x'", 'dx', '\partial x', 'x_2', '\partial x_{y_2}', "d\alpha_{x_{\beta''}'}'''"
# ('.', expr, 'name')                - data member reference
# ('.', expr, 'name', (a1, a2, ...)) - method member call
# ('"', 'str')                       - string (for function parameters like '+' or '-')
# (',', (expr1, expr2, ...))         - comma expression (tuple)
# ('{', expr)                        - invilible parentheses for grouping
# ('(', expr)                        - explicit parentheses
# ('[', expr)                        - brackets
# ('|', expr)                        - absolute value
# ('-', expr)                        - negative of expression, negative numbers are represented with this at least initially
# ('!', expr)                        - factorial
# ('+', (expr1, expr2, ...))         - addition
# ('*', (expr1, expr2, ...))         - multiplication
# ('/', numer, denom)                - fraction numer(ator) / denom(inator)
# ('^', base, exp)                   - power base ^ exp(onent)
# ('log', expr)                      - natural logarithm of expr
# ('log', expr, base)                - logarithm of expr in base
# ('sqrt', expr)                     - square root of expr
# ('sqrt', expr, n)                  - nth root of expr
# ('func', 'func', (a1, a2, ...))    - sympy or regular python function 'func', will be called with sympy expression (',' expr gives multiple arguments)
# ('lim', expr, var, to)             - limit of expr when variable var approaches to from both positive and negative directions
# ('lim', expr, var, to, 'dir')      - limit of expr when variable var approaches to from specified direction dir which may be '+' or '-'
# ('sum', expr, var, from, to)       - summation of expr over variable var from from to to
# ('diff', expr, (var1, ...))        - differentiation of expr with respect to var1 and optional other vars
# ('intg', expr, var)                - anti-derivative of expr (or 1 if expr is None) with respect to differential var ('dx', 'dy', etc ...)
# ('intg', expr, var, from, to)      - definite integral of expr (or 1 if expr is None) with respect to differential var ('dx', 'dy', etc ...)
# ('vec', (e1, e2, ...))             - vector
# ('mat', ((e11, e12, ...), (e21, e22, ...), ...)) - matrix
# ('piece', ((v1, c1), ..., (vn, True?)))          - piecewise expression: v = AST, c = condition AST
# ('lamb', expr, (v1, v2, ...))      - lambda expression: v = ('@', 'var')

# TODO: Add zeta and Gamma unicode character functions.

import re
import types

import sympy as sp

# _SYMPY_OBJECTS = dict ((name, obj) for name, obj in \
# 		filter (lambda no: no [0] [0] != '_' and len (no [0]) >= 2 and not isinstance (no [1], types.ModuleType), sp.__dict__.items ()))
_SYMPY_OBJECTS = dict ((name, obj) for name, obj in filter (lambda no: no [0] [0] != '_', sp.__dict__.items ()))
_SYMPY_FUNCS   = set (no [0] for no in filter (lambda no: len (no [0]) > 1 and callable (no [1]), _SYMPY_OBJECTS.items ()))

#...............................................................................................
class AST (tuple):
	op     = None
	CONSTS = set () # will be filled in after all classes defined

	_rec_identifier = re.compile (r'^[a-zA-Z_]\w*$')

	def __new__ (cls, *args):
		op       = _AST_CLS2OP.get (cls)
		cls_args = tuple (AST (*arg) if arg.__class__ is tuple else arg for arg in args)

		if op:
			args = (op,) + cls_args

		elif args:
			args = cls_args
			cls2 = _AST_OP2CLS.get (args [0])

			if cls2:
				cls      = cls2
				cls_args = cls_args [1:]

		self = tuple.__new__ (cls, args)

		if self.op:
			self._init (*cls_args)

		return self

	def __getattr__ (self, name): # calculate value for nonexistent self.name by calling self._name () and store
		func                 = getattr (self, f'_{name}') if name [0] != '_' else None
		val                  = func and func ()
		self.__dict__ [name] = val

		return val

	def _is_single_unit (self): # is single positive digit, fraction or single non-differential non-subscripted non-primed variable?
		if self.op == '/':
			return True
		elif self.op == '#':
			return len (self.num) == 1
		else:
			return self.is_single_var

	def neg (self, stack = False): # stack means stack negatives ('-', ('-', ('#', '-1')))
		if stack:
			return \
					AST ('-', self)            if not self.is_pos_num else \
					AST ('#', f'-{self.num}')
		else:
			return \
					self.minus                 if self.is_minus else \
					AST ('-', self)            if not self.is_num else \
					AST ('#', self.num [1:])   if self.num [0] == '-' else \
					AST ('#', f'-{self.num}')

	def strip_curlys (self, count = None):
		count = 999999999 if count is None else count

		while self.op == '{' and count:
			self   = self.curly
			count -= 1

		return self

	def remove_curlys (self):
		return \
				self.curly.remove_curlys () \
				if self.is_curly else \
				AST (*tuple (a.remove_curlys () if isinstance (a, AST) else a for a in self))

	def strip_paren (self, count = None):
		count = 999999999 if count is None else count

		while self.op == '(' and count:
			self   = self.paren
			count -= 1

		return self

	def strip_paren_noncomma (self, count = None):
		new = self.strip_paren (count)

		return new if not new.is_comma or not self.is_paren else AST ('(', new)

	def strip (self, count = None):
		count = 999999999 if count is None else count

		while self.op in {'{', '('} and count:
			self   = self [1]
			count -= 1

		return self

	def strip_minus (self, count = None, retneg = False):
		count       = 999999999 if count is None else count
		neg         = lambda ast: ast
		neg.has_neg = False

		while self.op == '-' and count:
			self         = self.minus
			count       -= 1
			neg          = lambda ast, neg = neg: neg (ast.neg (stack = True))
			neg.has_neg  = True

		return (self, neg) if retneg else self

	def strip_lim_sum (self, count = None):
		count = 999999999 if count is None else count

		while self.op in {'lim', 'sum'} and count:
			self   = self [1]
			count -= 1

		return self

	def as_identifier (self, top = True):
		if self.op in {'#', '@', '"'}:
			name = self [1]
		elif not self.is_mul:
			return None

		else:
			try:
				name = ''.join (m.as_identifier () for m in self.muls)
			except TypeError:
				return None

		return name if AST._rec_identifier.match (name) else None

	def vars (self): # return set of unique variables found in tree
		pass ## TODO: This!


	@staticmethod
	def is_int_text (text): # >= 0
		return AST_Num._rec_int.match (text)

	@staticmethod
	def flatcat (op, ast0, ast1): # ,,,/O.o\,,,~~
		if ast0.op == op:
			return \
					AST (op, ast0 [-1] + ast1 [-1]) \
					if ast1.op == op else \
					AST (op, ast0 [-1] + (ast1,))

		else: # ast0.op != op
			return \
					AST (op, (ast0,) + ast1 [-1]) \
					if ast1.op == op else \
					AST (op, (ast0, ast1))

#...............................................................................................
class AST_Eq (AST):
	op, is_eq  = '=', True

	TEX2PY = {'\\ne': '!=', '\\le': '<=', '\\ge': '>=', '\\lt': '<', '\\gt': '>', '\\neq': '!='}
	UNI2PY = {'\u2260': '!=', '\u2264': '<=', '\u2265': '>='}
	ANY2PY = {**UNI2PY, **TEX2PY}
	PY2TEX = {'!=': '\\ne', '<=': '\\le', '>=': '\\ge'} # , '<': '\\lt', '>': '\\gt'}

	def _init (self, rel, lhs, rhs):
		self.rel, self.lhs, self.rhs = rel, lhs, rhs # should be short form

	_is_ass = lambda self: self.rel == '='

class AST_Num (AST):
	op, is_num = '#', True

	_rec_int          = re.compile (r'^-?\d+$')
	_rec_pos_int      = re.compile (r'^\d+$')
	_rec_mant_and_exp = re.compile (r'^(-?\d*\.?\d*)[eE](?:(-\d+)|\+?(\d+))$')

	def _init (self, num):
		self.num = num

	_is_pos_num = lambda self: self.num [0] != '-'
	_is_neg_num = lambda self: self.num [0] == '-'
	_is_pos_int = lambda self: AST_Num._rec_pos_int.match (self.num)

	def _mant_and_exp (self):
		m = AST_Num._rec_mant_and_exp.match (self.num)

		return (self.num, None) if not m else (m.group (1) , m.group (2) or m.group (3))

class AST_Var (AST):
	op, is_var = '@', True

	GREEK       = {'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma', \
			'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega'}
	GREEKUNI    = {'\u03b1', '\u03b2', '\u03b3', '\u03b4', '\u03b5', '\u03b7', '\u03b8', '\u03b9', '\u03ba', '\u03bb', '\u03bc', '\u03bd', '\u03be', '\u03c0', '\u03c1', '\u03c3', \
			'\u03c4', '\u03c5', '\u03c6', '\u03c7', '\u03c8', '\u03c9', '\u0394', '\u0398', '\u0398', '\u039e', '\u03a0', '\u03a3', '\u03a5', '\u03a6', '\u03a8', '\u03a9'}

	TEX2PY      = {**dict ((f'\\{g}', g) for g in GREEK), '\\partial': 'partial', '\\infty': 'oo', \
			'\\overline\\infty': 'zoo', '\\bar\\infty': 'zoo', '\\widetilde\\infty': 'zoo', '\\tilde\\infty': 'zoo'}
	UNI2PY      = {**dict (zip (GREEKUNI, GREEK)), '\u2202': 'partial', '\u221e': 'oo'}
	ANY2PY      = {**UNI2PY, **TEX2PY}
	PY2TEX      = {**dict ((g, f'\\{g}') for g in GREEK), 'partial': '\\partial', 'oo': '\\infty', 'zoo': '\\widetilde\\infty'}

	_rec_groups = re.compile (r'^(?:(d(?!elta|partial))|(partial))?(.*)$')

	def _init (self, var):
		self.var = var

		if AST._rec_identifier.match (var):
			self.__dict__ [f'is_var_{var}'] = True

	_grp                  = lambda self: AST_Var._rec_groups.match (self.var).groups ()
	_is_null_var          = lambda self: not self.var
	_is_long_var          = lambda self: len (self.var) > 1 and self.var not in AST_Var.PY2TEX
	_is_differential      = lambda self: self.grp [0] and self.grp [2]
	_is_diff_solo         = lambda self: self.grp [0] and not self.grp [2]
	_is_diff_any          = lambda self: self.grp [0]
	_is_partial           = lambda self: self.grp [1] and self.grp [2]
	_is_part_solo         = lambda self: self.grp [1] and not self.grp [2]
	_is_part_any          = lambda self: self.grp [1]
	_is_diff_or_part      = lambda self: (self.grp [0] or self.grp [1]) and self.grp [2]
	_is_diff_or_part_solo = lambda self: (self.grp [0] or self.grp [1]) and not self.grp [2]
	_diff_or_part_type    = lambda self: self.grp [0] or self.grp [1] or '' # 'dx' -> 'd', 'partialx' -> 'partial', else ''
	_is_single_var        = lambda self: len (self.var) == 1 or self.var in AST_Var.PY2TEX # is single atomic variable (non-differential, non-subscripted, non-primed)?
	_as_var               = lambda self: AST ('@', self.grp [2]) if self.var else self # 'x', dx', 'partialx' -> 'x'
	_as_diff              = lambda self: AST ('@', f'd{self.grp [2]}') if self.var else self # 'x', 'dx', 'partialx' -> 'dx'

class AST_Attr (AST):
	op, is_attr = '.', True

	def _init (self, obj, attr, args = None):
		self.obj, self.attr, self.args = obj, attr, args

class AST_Str (AST):
	op, is_str = '"', True

	def _init (self, str_):
		self.str_ = str_

class AST_Comma (AST):
	op, is_comma = ',', True

	def _init (self, commas):
		self.commas = commas

	# _len = lambda self: len (self.commas)

class AST_Curly (AST):
	op, is_curly = '{', True

	def _init (self, curly):
		self.curly = curly

	# _len = lambda self: len (self.paren)

class AST_Paren (AST):
	op, is_paren = '(', True

	def _init (self, paren):
		self.paren = paren

	# _len = lambda self: len (self.paren)

class AST_Brack (AST):
	op, is_brack = '[', True

	def _init (self, bracks):
		self.bracks = bracks

	# _len = lambda self: len (self.bracks)

class AST_Abs (AST):
	op, is_abs = '|', True

	def _init (self, abs):
		self.abs = abs

class AST_Minus (AST):
	op, is_minus = '-', True

	def _init (self, minus):
		self.minus = minus

class AST_Fact (AST):
	op, is_fact = '!', True

	def _init (self, fact):
		self.fact = fact

class AST_Add (AST):
	op, is_add = '+', True

	def _init (self, adds):
		self.adds = adds

	# _len = lambda self: len (self.adds)

class AST_Mul (AST):
	op, is_mul = '*', True

	def _init (self, muls):
		self.muls = muls

	def _is_mul_has_abs (self):
		for m in self.muls:
			if m.is_abs:
				return True

	# _len = lambda self: len (self.muls)

class AST_Div (AST):
	op, is_div = '/', True

	def _init (self, numer, denom):
		self.numer, self.denom = numer, denom

class AST_Pow (AST):
	op, is_pow = '^', True

	def _init (self, base, exp):
		self.base, self.exp = base, exp

class AST_Log (AST):
	op, is_log = 'log', True

	def _init (self, log, base = None):
		self.log, self.base = log, base

class AST_Sqrt (AST):
	op, is_sqrt = 'sqrt', True

	def _init (self, rad, idx = None):
		self.rad, self.idx = rad, idx

class AST_Func (AST):
	op, is_func = 'func', True

	# GREEK       = {'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma', \
	# 		'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega', 'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega'}
	# GREEKUNI    = {'\u03b1', '\u03b2', '\u03b3', '\u03b4', '\u03b5', '\u03b6', '\u03b7', '\u03b8', '\u03b9', '\u03ba', '\u03bb', '\u03bc', '\u03bd', '\u03be', '\u03c0', '\u03c1', '\u03c3', \
	# 		'\u03c4', '\u03c5', '\u03c6', '\u03c7', '\u03c8', '\u03c9', '\u0393', '\u0394', '\u0398', '\u0398', '\u039e', '\u03a0', '\u03a3', '\u03a5', '\u03a6', '\u03a8', '\u03a9'}

	SPECIAL         = {'@', '%', 'vars', 'del', 'delall'}
	BUILTINS        = {'max', 'min', 'abs', 'pow', 'str', 'sum'}
	TEXNATIVE       = {'max', 'min', 'arg', 'deg', 'exp', 'gcd', 'ln', 'zeta', 'Gamma'}
	TRIGH           = {'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'sinh', 'cosh', 'tanh', 'coth', 'sech', 'csch'}

	PY_TRIGHINV     = {f'a{f}' for f in TRIGH}
	TEX_TRIGHINV    = {f'arc{f}' for f in TRIGH}
	TEX2PY_TRIGHINV = {f'arc{f}': f'a{f}' for f in TRIGH}

	PY              = SPECIAL | BUILTINS | PY_TRIGHINV | TRIGH | _SYMPY_FUNCS - {'beta', 'Lambda'}
	TEX             = TEXNATIVE | TEX_TRIGHINV | (TRIGH - {'sech', 'csch'})

	_rec_trigh        = re.compile (r'^a?(?:sin|cos|tan|csc|sec|cot)h?$')
	_rec_trigh_inv    = re.compile (r'^a(?:sin|cos|tan|csc|sec|cot)h?$')
	_rec_trigh_noninv = re.compile (r'^(?:sin|cos|tan|csc|sec|cot)h?$')

	def _init (self, func, args):
		self.func, self.args = func, args

		if AST._rec_identifier.match (func):
			self.__dict__ [f'is_func_{func}'] = True

	_is_trigh_func        = lambda self: AST_Func._rec_trigh.match (self.func)
	_is_trigh_func_inv    = lambda self: AST_Func._rec_trigh_inv.match (self.func)
	_is_trigh_func_noninv = lambda self: AST_Func._rec_trigh_noninv.match (self.func)

class AST_Lim (AST):
	op, is_lim = 'lim', True

	def _init (self, lim, lvar, to, dir = None):
		self.lim, self.lvar, self.to, self.dir = lim, lvar, to, dir

class AST_Sum (AST):
	op, is_sum = 'sum', True

	def _init (self, sum, svar, from_, to):
		self.sum, self.svar, self.from_, self.to = sum, svar, from_, to

class AST_Diff (AST):
	op, is_diff = 'diff', True

	def _init (self, diff, dvs):
		self.diff, self.dvs = diff, dvs

	_diff_type = lambda self: '' if not self.dvs else self.dvs [0].diff_or_part_type if self.dvs [0].is_var else self.dvs [0].base.diff_or_part_type

class AST_Intg (AST):
	op, is_intg = 'intg', True

	def _init (self, intg, dv, from_ = None, to = None):
		self.intg, self.dv, self.from_, self.to = intg, dv, from_, to

class AST_Vec (AST):
	op, is_vec = 'vec', True

	def _init (self, vec):
		self.vec = vec

	# _len = lambda self: len (self.vec)

class AST_Mat (AST):
	op, is_mat = 'mat', True

	def _init (self, mat):
		self.mat = mat

	_rows = lambda self: len (self.mat)
	_cols = lambda self: len (self.mat [0]) if self.mat else 0

class AST_Piece (AST):
	op, is_piece = 'piece', True

	def _init (self, pieces):
		self.pieces = pieces

class AST_Lamb (AST):
	op, is_lamb = 'lamb', True

	def _init (self, lamb, vars):
		self.lamb, self.vars = lamb, vars

#...............................................................................................
_AST_OP2CLS = {
	'=': AST_Eq,
	'#': AST_Num,
	'@': AST_Var,
	'.': AST_Attr,
	'"': AST_Str,
	',': AST_Comma,
	'{': AST_Curly,
	'(': AST_Paren,
	'[': AST_Brack,
	'|': AST_Abs,
	'-': AST_Minus,
	'!': AST_Fact,
	'+': AST_Add,
	'*': AST_Mul,
	'/': AST_Div,
	'^': AST_Pow,
	'log': AST_Log,
	'sqrt': AST_Sqrt,
	'func': AST_Func,
	'lim': AST_Lim,
	'sum': AST_Sum,
	'diff': AST_Diff,
	'intg': AST_Intg,
	'vec': AST_Vec,
	'mat': AST_Mat,
	'piece': AST_Piece,
	'lamb': AST_Lamb, # not to be confused with the Greek variable lambda
}

_AST_CLS2OP = dict ((b, a) for (a, b) in _AST_OP2CLS.items ())

for cls in _AST_CLS2OP:
	setattr (AST, cls.__name__ [4:], cls)

AST.OPS      = set (_AST_OP2CLS)
AST.Zero     = AST ('#', '0')
AST.One      = AST ('#', '1')
AST.NegOne   = AST ('#', '-1')
AST.VarNull  = AST ('@', '')
AST.MatEmpty = AST ('func', 'Matrix', ('[', ()))

_CONSTS      = (('E', 'e'), ('I', 'i'), ('Pi', 'pi'), ('Infty', 'oo'), ('CInfty', 'zoo'), ('None_', 'None'), ('True_', 'True'), ('False_', 'False'), ('NaN', 'nan'),
		('Naturals', 'Naturals'), ('Naturals0', 'Naturals0'), ('Integers', 'Integers'), ('Reals', 'Reals'), ('Complexes', 'Complexes'))

for _vp, _vv in _CONSTS:
	ast = AST ('@', _vv)

	AST.CONSTS.add (ast)
	setattr (AST, _vp, ast)

def sympyEI (yes = True):
	AST.CONSTS.difference_update ((AST.E.var, AST.I.var))
	AST.E, AST.I = (AST ('@', 'E'), AST ('@', 'I')) if yes else (AST ('@', 'e'), AST ('@', 'i'))
	AST.CONSTS.update ((AST.E.var, AST.I.var))

class sast: # for single script
	AST     = AST
	sympyEI = sympyEI
# Builds expression tree from text, nodes are nested AST tuples.
#
# Time and interest permitting:
# sets
# assumptions/hints
# importing modules to allow custom code execution
# Proper implementation of vectors with "<b>\vec{x}</b>" and "<b>\hat{i}</b>" variables
# sympy function/variable module prefix
# systems of equations, ODEs, graphical plots (using matplotlib?)...

# TODO: multiple vector weirdness
# TODO: _xlat_func_Integral multiple integrals

import ast as py_ast
from collections import OrderedDict
import os
import re
import sys


def _FUNC_name (FUNC):
	return AST.Func.TEX2PY_TRIGHINV.get (FUNC.grp [1], FUNC.grp [1]) if FUNC.grp [1] else \
			FUNC.grp [0] or FUNC.grp [2] or FUNC.grp [3].replace ('\\', '') or FUNC.text

def _ast_from_tok_digit_or_var (tok, i = 0):
	return AST ('#', tok.grp [i]) if tok.grp [i] else \
			AST ('@', AST.Var.ANY2PY.get (tok.grp [i + 2].replace (' ', ''), tok.grp [i + 1]) if tok.grp [i + 2] else tok.grp [i + 1])

def _ast_func_tuple_args (ast):
	ast = ast.strip ()

	return ast.commas if ast.is_comma else (ast,)

def _expr_lambda (lhs, expr):
	if lhs.is_var:
		if lhs.is_var_lambda:
			return AST ('lamb', expr, ())

	elif lhs.is_mul:
		if lhs.muls [-1].is_var:
			if lhs.muls [-1].is_var_lambda:
				return AST ('*', lhs.muls [:-1] + (('lamb', expr, ()),))

			if lhs.muls [-2].is_var_lambda:
				ast = AST ('lamb', expr, (lhs.muls [-1],))

				return ast if len (lhs.muls) == 2 else AST ('*', lhs.muls [:-2] + (ast,))

	elif lhs.is_comma:
		commas = lhs.commas
		ast    = None

		for imul in range (len (commas) - 1, -1, -1):
			if commas [imul].is_var:
				if commas [imul].is_var_lambda:
					ast = AST ('lamb', expr, commas [imul + 1:])

					break

				continue

			if commas [imul].is_mul:
				if commas [imul].muls [-1].is_var and commas [imul].muls [-2].is_var_lambda:
					ast = AST ('lamb', expr, (commas [imul].muls [-1],) + commas [imul + 1:])

					if len (commas [imul].muls) > 2:
						ast = AST ('*', commas [imul].muls [:-2] + (ast,))

					break

		if ast:
			return ast if imul == 0 else AST (',', commas [:imul] + (ast,))

	raise SyntaxError ('invalid lambda expression')

def _expr_mapsto (lhs, expr):
	lhs = lhs.strip ()

	if lhs.is_var:
		return AST ('lamb', expr, (lhs,))

	if lhs.is_comma:
		for var in lhs.commas:
			if not var.is_var:
				break

		else:
			return AST ('lamb', expr, lhs.commas)

	raise SyntaxError ('invalid LaTeX \\mapsto expression')

def _expr_mul_imp (lhs, rhs, user_funcs = {}):
	last      = lhs.muls [-1] if lhs.is_mul else lhs
	arg, wrap = _expr_func_reorder (rhs, strip = 0)
	ast       = None

	if last.is_attr: # {x.y} * () -> x.y(), x.{y.z} -> {x.y}.z
		if last.args is None:
			if arg.is_paren:
				ast = wrap (AST ('.', last.obj, last.attr, _ast_func_tuple_args (arg)))
			elif rhs.is_attr:
				ast = AST ('.', _expr_mul_imp (last, rhs.obj), rhs.attr)

	elif last.is_pow: # {x^y.z} * () -> x^{y.z()}
		if last.exp.is_attr and last.exp.args is None:
			if arg.is_paren:
				ast = AST ('^', last.base, wrap (AST ('.', last.exp.obj, last.exp.attr, _ast_func_tuple_args (arg))))
			elif rhs.is_attr:
				ast = AST ('^', last.base, ('.', _expr_mul_imp (last.exp, rhs.obj), rhs.attr))

	elif last.is_var:
		if last.var in user_funcs:
			if arg.is_paren:
				ast = wrap (AST ('func', last.var, _ast_func_tuple_args (arg)))

	if ast:
		return AST ('*', lhs.muls [:-1] + (ast,)) if lhs.is_mul else ast

	return AST.flatcat ('*', lhs, rhs)

def _expr_diff (ast): # convert possible cases of derivatives in ast: ('*', ('/', 'd', 'dx'), expr) -> ('diff', expr, 'dx')
	def _interpret_divide (ast):
		if ast.numer.is_diff_or_part_solo:
			p = 1
			v = ast.numer

		elif ast.numer.is_pow and ast.numer.base.is_diff_or_part_solo and ast.numer.exp.remove_curlys ().is_pos_int:
			p = int (ast.numer.exp.remove_curlys ().num)
			v = ast.numer.base

		else:
			return None

		ast_dv_check = (lambda n: n.is_differential) if v.is_diff_solo else (lambda n: n.is_partial)

		ns = ast.denom.muls if ast.denom.is_mul else (ast.denom,)
		ds = []
		cp = p

		for i in range (len (ns)):
			n = ns [i]

			if ast_dv_check (n):
				dec = 1
			elif n.is_pow and ast_dv_check (n.base) and n.exp.remove_curlys ().is_pos_int:
				dec = int (n.exp.remove_curlys ().num)
			else:
				return None

			cp -= dec

			if cp < 0:
				return None # raise SyntaxError?

			ds.append (n)

			if not cp:
				if i == len (ns) - 1:
					return AST ('diff', None, tuple (ds))
				elif i == len (ns) - 2:
					return AST ('diff', ns [-1], tuple (ds))
				else:
					return AST ('diff', AST ('*', ns [i + 1:]), tuple (ds))

		return None # raise SyntaxError?

	# start here
	if ast.is_div: # this part handles d/dx
		diff = _interpret_divide (ast)

		if diff and diff [1]:
			return diff

	elif ast.is_mul: # this part needed to handle \frac{d}{dx}
		tail = []
		end  = len (ast.muls)

		for i in range (end - 1, -1, -1):
			if ast.muls [i].is_div:
				diff = _interpret_divide (ast.muls [i])

				if diff:
					if diff.expr:
						if i < end - 1:
							tail [0 : 0] = ast.muls [i + 1 : end]

						tail.insert (0, diff)

					elif i < end - 1:
						tail.insert (0, AST ('diff', ast.muls [i + 1] if i == end - 2 else AST ('*', ast.muls [i + 1 : end]), diff.dvs))

					else:
						continue

					end = i

		if tail:
			tail = tail [0] if len (tail) == 1 else AST ('*', tuple (tail))

			return tail if end == 0 else AST.flatcat ('*', ast.muls [0], tail) if end == 1 else AST.flatcat ('*', AST ('*', ast.muls [:end]), tail)

	return ast

def _ast_strip_tail_differential (ast):
	if ast.is_differential or ast.is_null_var: # null_var is for autocomplete
		return None, ast

	if ast.is_intg:
		if ast.intg is not None:
			ast2, neg = ast.intg.strip_minus (retneg = True)
			ast2, dv  = _ast_strip_tail_differential (ast2)

			if dv:
				return \
						(AST ('intg', neg (ast2), dv, *ast [3:]), ast.dv) \
						if ast2 else \
						(AST ('intg', neg (AST.One), dv, *ast [3:]), ast.dv) \
						if neg.has_neg else \
						(AST ('intg', None, dv, *ast [3:]), ast.dv)

	elif ast.is_diff:
		ast2, neg = ast.diff.strip_minus (retneg = True)
		ast2, dv  = _ast_strip_tail_differential (ast2)

		if dv:
			return \
					(AST ('diff', neg (ast2), ast.dvs), dv) \
					if ast2 else \
					(neg (AST ('/', ('@', ast.diff_type or 'd'), ast.dvs [0])), dv) \
					if len (ast.dvs) == 1 else \
					(neg (AST ('/', ('@', ast.diff_type or 'd'), ('*', ast.dvs))), dv)
			# raise NotImplementedError ('changing differential to ordinary fraction')

	elif ast.is_div:
		ast2, neg = ast.denom.strip_minus (retneg = True)
		ast2, dv  = _ast_strip_tail_differential (ast2)

		if dv and ast2:
			return AST ('/', ast.numer, neg (ast2)), dv

		ast2, neg = ast.numer.strip_minus (retneg = True)

		if dv:
			return AST ('/', neg (ast2) if ast2 else neg (AST.One), ast.denom), dv

	elif ast.is_mul:
		ast2, neg = ast.muls [-1].strip_minus (retneg = True)
		ast2, dv  = _ast_strip_tail_differential (ast2)

		if dv:
			return \
					(AST ('*', ast.muls [:-1] + (neg (ast2),)), dv) \
					if ast2 else \
					(neg (AST ('*', ast.muls [:-1])), dv) \
					if len (ast.muls) > 2 else \
					(neg (ast.muls [0]), dv)

	elif ast.is_add:
		ast2, neg = ast.adds [-1].strip_minus (retneg = True)
		ast2, dv  = _ast_strip_tail_differential (ast2)

		if dv and ast2:
			return AST ('+', ast.adds [:-1] + (neg (ast2),)), dv

	return ast, None

def _expr_int (ast, from_to = ()): # find differential for integration if present in ast and return integral ast
	ast, neg = ast.strip_minus (retneg = True)
	ast, dv  = _ast_strip_tail_differential (ast)

	if dv:
		return \
				AST ('intg', neg (ast), dv, *from_to) \
				if ast else \
				AST ('intg', neg (AST.One), dv, *from_to) \
				if neg.has_neg else \
				neg (AST ('intg', None, dv, *from_to))

	raise SyntaxError ('integration expecting a differential')

_xlat_func_Limit_dirs = {'+': ('+',), '-': ('-',), '+-': ()}

def _xlat_func_Derivative (ast): # translate function 'Derivative' to native ast representation for pretty rendering
	if ast.is_null_var:
		return AST ('diff', ast, (AST.VarNull,))
	elif not ast.is_comma:
		raise lalr1.Incomplete (AST ('diff', ast, (AST.VarNull,)))
	elif len (ast.commas) == 0:
		raise lalr1.Incomplete (AST ('diff', AST.VarNull, (AST.VarNull,)))
	elif len (ast.commas) == 1:
		raise lalr1.Incomplete (AST ('diff', ast.commas [0], (AST.VarNull,)))

	commas = list (ast.commas [:0:-1])
	ds     = []

	while commas:
		d = commas.pop ().as_diff

		if commas and commas [-1].is_num:
			ds.append (AST ('^', d, commas.pop ()))
		else:
			ds.append (d)

	return AST ('diff', ast.commas [0], AST (*ds))

def _xlat_func_Integral (ast): # translate function 'Integral' to native ast representation for pretty rendering
	if not ast.is_comma:
		return AST ('intg', ast, ast.as_diff if ast.is_var else AST.VarNull)
	elif len (ast.commas) == 0:
		ast = AST ('intg', AST.VarNull, AST.VarNull)
	elif len (ast.commas) == 1:
		ast = AST ('intg', ast.commas [0], AST.VarNull)

	else:
		ast2 = ast.commas [1].strip (1)

		if not ast2.is_comma:
			return AST ('intg', ast.commas [0], ast2.as_diff)
		elif len (ast2.commas) == 3:
			return AST ('intg', ast.commas [0], ast2.commas [0].as_diff, ast2.commas [1], ast2.commas [2])
		else:
			ast = AST (*(('intg', ast.commas [0], ast2.commas [0].as_diff) + ast2.commas [1:] + (AST.VarNull, AST.VarNull)) [:5])

	raise lalr1.Incomplete (ast)

def _xlat_func_Limit (ast): # translate function 'Limit' to native ast representation for pretty rendering
	if ast.is_null_var:
		return AST ('lim', ast, AST.VarNull, AST.VarNull)
	elif not ast.is_comma:
		raise lalr1.Incomplete (AST ('lim', ast, AST.VarNull, AST.VarNull))

	commas = ast.commas
	l      = len (commas)

	if l == 0:
		ast = AST ('lim', AST.VarNull, AST.VarNull, AST.VarNull)
	elif l == 1:
		ast = AST ('lim', commas [0], AST.VarNull, AST.VarNull)
	elif l == 2:
		ast = AST ('lim', commas [0], commas [1], AST.VarNull)
	elif l == 3:
		return AST ('lim', commas [0], commas [1], commas [2], '+')
	elif commas [3].is_str:
		return AST ('lim', *(commas [:3] + _xlat_func_Limit_dirs.get (commas [3].str_, ('+',))))
	elif commas [3].is_ass and commas [3].lhs.as_identifier () == 'dir' and commas [3].rhs.is_str:
		return AST ('lim', *(commas [:3] + _xlat_func_Limit_dirs.get (commas [3].rhs.str_, ('+',))))
	else:
		ast = AST ('lim', commas [0], commas [1], commas [2])

	if l and commas [-1].is_null_var:
		return ast

	raise lalr1.Incomplete (ast)

def _xlat_func_Matrix (ast):
	if ast.is_brack and ast.bracks:
		if not ast.bracks [0].is_brack: # single layer or brackets, column matrix?
			return AST ('vec', ast.bracks)

		elif ast.bracks [0].bracks:
			rows = [ast.bracks [0].bracks]
			cols = len (rows [0])

			for row in ast.bracks [1 : -1]:
				if len (row.bracks) != cols:
					break

				rows.append (row.bracks)

			else:
				l = len (ast.bracks [-1].bracks)

				if l <= cols:
					if len (ast.bracks) > 1:
						rows.append (ast.bracks [-1].bracks + (AST.VarNull,) * (cols - l))

					if l != cols:
						raise lalr1.Incomplete (AST ('mat', tuple (rows)))

					return \
							AST ('mat', tuple (rows)) \
							if cols > 1 else \
							AST ('vec', tuple (r [0] for r in rows))

	return AST ('func', 'Matrix', (ast,))

def _xlat_func_Piecewise (ast):
	pcs = []

	if ast.is_comma and ast.commas and ast.commas [0].strip_paren ().is_comma:
		for c in ast.commas [:-1]:
			c = c.strip_paren ()

			if not c.is_comma or len (c.commas) != 2:
				raise SyntaxError ('expecting tuple of length 2')

			pcs.append (c.commas)

		ast = ast.commas [-1].strip_paren ()

	pcs = tuple (pcs)

	if not ast.is_comma:
		raise lalr1.Incomplete (AST ('piece', pcs + ((ast, AST.VarNull),)))
	if len (ast.commas) == 0:
		raise lalr1.Incomplete (AST ('piece', pcs + ()))

	if not ast.commas [0].is_comma:
		if len (ast.commas) == 1:
			raise lalr1.Incomplete (AST ('piece', pcs + ((ast.commas [0], AST.VarNull),)))
		if len (ast.commas) == 2:
			return AST ('piece', pcs + ((ast.commas [0], True if ast.commas [1] == AST.True_ else ast.commas [1]),))
			# return AST ('piece', pcs + ((ast.commas [0], True if ast.commas [1].stip_curlys ().strip_paren () == AST.True_ else ast.commas [1]),))

		raise SyntaxError ('invalid tuple length')

	raise RuntimeError ()

def _xlat_func_Pow (ast):
	if not ast.is_comma:
		raise lalr1.Incomplete (AST ('^', ast, AST.VarNull))
	elif len (ast.commas) == 0:
		raise lalr1.Incomplete (AST ('^', AST.VarNull, AST.VarNull))
	elif len (ast.commas) == 1:
		raise lalr1.Incomplete (AST ('^', ast.commas [0], AST.VarNull))

	elif len (ast.commas) == 2:
		ast = AST ('^', ast.commas [0], ast.commas [1])

		if ast.exp.is_null_var:
			raise lalr1.Incomplete (ast)
		else:
			return ast

	raise SyntaxError ('too many parameters')

def _xlat_func_Sum (ast): # translate function 'Sum' to native ast representation for pretty rendering
	if ast.is_null_var:
		return AST ('sum', ast, AST.VarNull, AST.VarNull, AST.VarNull)
	elif not ast.is_comma:
		raise lalr1.Incomplete (AST ('sum', ast, AST.VarNull, AST.VarNull, AST.VarNull))

	commas = ast.commas

	if len (commas) == 0:
		raise lalr1.Incomplete (AST ('sum', AST.VarNull, AST.VarNull, AST.VarNull, AST.VarNull))
	elif len (commas) == 1:
		ast = AST ('sum', commas [0], AST.VarNull, AST.VarNull, AST.VarNull)

	else:
		ast2 = commas [1].strip_paren (1)

		if not ast2.is_comma:
			ast = AST ('sum', commas [0], ast2, AST.VarNull, AST.VarNull)
		elif len (ast2.commas) == 3:
			return AST ('sum', commas [0], ast2.commas [0], ast2.commas [1], ast2.commas [2])

		else:
			commas = ast2.commas
			ast    = AST (*(('sum', ast.commas [0], *commas) + (AST.VarNull, AST.VarNull, AST.VarNull)) [:5])

	if commas [-1].is_null_var:
		return ast

	raise lalr1.Incomplete (ast)

# eye(2).a -> ('.', ('func', 'eye', (('.', ('(', ('#', '2')), 'a'),)), 'a')
# eye((2).a) -> ('func', 'eye', (('.', ('(', ('#', '2')), 'a'),))

def _expr_func (iparm, *args, strip = 0): # rearrange ast tree for explicit parentheses like func (x)^y to give (func (x))^y instead of func((x)^y)
	def astarg (arg):
		return (_ast_func_tuple_args (arg) if args [0] == 'func' else arg.strip (strip)),

	if args [iparm].is_fact:
		if args [iparm].fact.is_paren:
			return AST ('!', args [:iparm] + astarg (args [iparm].fact) + args [iparm + 1:])

	elif args [iparm].is_pow:
		if args [iparm].base.is_paren:
			return AST ('^', args [:iparm] + astarg (args [iparm].base) + args [iparm + 1:], args [iparm].exp)

	elif args [iparm].is_attr:
		if args [iparm].obj.is_paren:
			if args [0] != 'func':
				return AST ('.', args [:iparm] + (args [iparm].strip (strip),) + args [iparm + 1:], *args [iparm] [2:])
			else:
				return AST ('.', args [:iparm] + (_ast_func_tuple_args (args [iparm].obj),) + args [iparm + 1:], *args [iparm] [2:])

	return AST (*(args [:iparm] + astarg (args [iparm]) + args [iparm + 1:]))

def _expr_func_reorder (ast, strip):
	ast = _expr_func (1, None, ast, strip = strip)

	return \
			(ast [1], lambda a: a) \
			if ast.op is None else \
			(ast [1] [1], lambda a: AST (ast.op, a, *ast [2:]))

def _expr_func_xlat (_xlat_func, ast): # rearrange ast tree for a given function translation like 'Derivative' or 'Limit'
	ast, wrap = _expr_func_reorder (ast, strip = None) # strip all parentheses

	return wrap (_xlat_func (ast))

_FUNC_AST_XLAT = {
	'Abs'       : lambda expr: _expr_func (1, '|', expr, strip = 1),
	'abs'       : lambda expr: _expr_func (1, '|', expr, strip = 1),
	'Derivative': lambda expr: _expr_func_xlat (_xlat_func_Derivative, expr),
	'diff'      : lambda expr: _expr_func_xlat (_xlat_func_Derivative, expr),
	'exp'       : lambda expr: _expr_func (2, '^', AST.E, expr, strip = 1),
	'factorial' : lambda expr: _expr_func (1, '!', expr, strip = 1),
	'Gamma'     : lambda expr: _expr_func (2, 'func', 'gamma', expr, strip = 1),
	'Integral'  : lambda expr: _expr_func_xlat (_xlat_func_Integral, expr),
	'integrate' : lambda expr: _expr_func_xlat (_xlat_func_Integral, expr),
	'Limit'     : lambda expr: _expr_func_xlat (_xlat_func_Limit, expr),
	'limit'     : lambda expr: _expr_func_xlat (_xlat_func_Limit, expr),
	'Matrix'    : lambda expr: _expr_func_xlat (_xlat_func_Matrix, expr),
	'ln'        : lambda expr: _expr_func (1, 'log', expr),
	'Piecewise' : lambda expr: _expr_func_xlat (_xlat_func_Piecewise, expr),
	'Pow'       : lambda expr: _expr_func_xlat (_xlat_func_Pow, expr),
	'pow'       : lambda expr: _expr_func_xlat (_xlat_func_Pow, expr),
	'Sum'       : lambda expr: _expr_func_xlat (_xlat_func_Sum, expr),
}

def _expr_func_func (FUNC, expr_func_arg):
	func = _FUNC_name (FUNC) if isinstance (FUNC, lalr1.Token) else FUNC
	xlat = _FUNC_AST_XLAT.get (func)
	ast  = _expr_func (2, 'func', func, expr_func_arg)

	if not xlat:
		return ast

	args = ast.args if ast.is_func else ast [1].args
	arg  = args [0] if len (args) == 1 else AST (',', args)
	ast2 = xlat (AST ('(', arg))

	return ast2 if ast.is_func else AST (ast.op, ast2, *ast [2:])

def _expr_mat (expr_mat_rows):
	return \
			AST.MatEmpty \
			if not expr_mat_rows else \
			AST ('mat', expr_mat_rows) \
			if len (expr_mat_rows [0]) > 1 else  \
			AST ('vec', tuple (c [0] for c in expr_mat_rows))

def _expr_curly (ast): # convert curly expression to vector or matrix if appropriate
	if ast.op != ',':
		return AST ('{', ast)
	elif not ast.commas: # empty {}?
		return AST.VarNull

	c = sum (bool (c.is_vec) for c in ast.commas)

	if c == len (ast.commas) and len (set (len (c.vec) for c in ast.commas)) == 1:
		return \
				AST ('mat', tuple (c.vec for c in ast.commas)) \
				if len (ast.commas [0].vec) > 1 else \
				AST ('vec', tuple (c.vec [0] for c in ast.commas))

	return AST ('vec', ast.commas) # raise SyntaxError ('invalid matrix syntax')


#...............................................................................................
class Parser (lalr1.Parser):
	_USER_FUNCS = set () # set or dict of variable names to be translated into 'func' ASTs if variable followed by parentheses

	def set_user_funcs  (self, user_funcs):
		self._USER_FUNCS = user_funcs

	_PARSER_TABLES = \
			b'eJztXWuP3LaS/TMLZAZQAxJfkvzNcZxcY/3ItZ1gFwPDcBxnEWycZG3n7i4W979vnaqSSJHqh2a6Z7pnBsNpSRQfxWIdPopF6uziq0cvnr54/lX11b98+P1nujx9/O1runz/8OXj50/p5sl3z1+8fPz20Q8vn/47PX778uEjvTR6NXT9+vF3bx89fPX4ld4/' \
			b'e/ha776Otz/G2+/lllNFLs+ePP+B41J6/wqPV69f4veHr+n3+Q/P6PfHh/B58vz1d6DyyTN+zb9/f4m0nr7Ai29/eA76vubAj148e/ZwKMzLIT/cPHz2/ZAbHr/5+umrpw9f/Y1uHz//RqnH3dfx9sd4q9S/fPLd3wavofCP/46fp68ea6qvhRAiACGfPfz+' \
			b'1esXyP81l+/xvz16OrwGO7958uOTbxD10TcvXjMXtNCc7PdPmUdPvqUfToXYg1jv33368OXtH5/e/vzTb5+/vPtEXh/+589Pbz//9eeH8eGXv35///bdp/+IL38abj+++/L2/R+/pY+f/vjv7PHz8Pz+3ecPnz+/nz7+OX0cnt79FG+/fIm0vHv/Zbj/M+YE' \
			b'EiN5H4fb334db3/9fYz38a/f3v76ccz3H7HYv8eoP//6j+H2y4dPifcvvwz3P3169/4/P4zJ/v5h5ND7vz799r9pdnSTMGUs2M8/Twofaf3wX2PJKJOxwL9+eP9hfKCq+z0m+ufnL3+MxX738aef3w1PY1pjXn98/Phu8vD5qzfVxdnKNZVrziu5Mbix1crx' \
			b'tanOTGVCtWoq29LN+ejLftFj1eKmMfLjyaNx56lX41Iv3CJiLT9OXtAdpcVBWmTceM2YPAdf9Rs9Vk3Pd0RTR7FNZbtz9Vg1llMFBdZW1pzrIz3xnUO4CrlKcqOHPNkhHkVwgxdu6c7wv6H87bk8rzjNRv2Fhmpl1FOePdFvmXH94EFl4Dsi3tScUi0/jtI2' \
			b'mnj0AhujL25Rb/TvK9tXK38uz3SDEL38OPGmO2Ix7sgfOYNFUnLyCMlDKxd4IB4qAyUXovURtBNzmqm/Kx+7qZcvHl2deq1Mx6ym7E2rd2dcbGVqrTKGajODF24Rn1gBviBTFwMM3vFxZZhDnmunhrjL4ypwAPI3TUXiheoylBmKX4GBjYj8mhCAkG92DEiF' \
			b'mgZcGc490H9bOTtQRTXDLKEEBBSoR6pvm0KD3g3eowf4Ah8XfRrx8dHHiE8YfEgomeut/CToANj4JsgPA0MqhZ5wizs/vDzXR3oaXkgeTn5cN5Z99OpTL9yCMVZ+qNrOz+MtwgSRjCEKRJg5BYbzDTcjdmi+pGUgP8Hg+Oi4buyASiontymdiJZHMStIk3At' \
			b'9VYPeuZsO/kh0TvXZwIdF57eNJyuPnlpRagAJBJROCD1ImcsvSoZYYACeZ65ZoSCPibgYB8z5ENPjlnY9FUz3rR6Q1wa7wQ8REl/Tl3CRV2RNFK2BEfiNsGFRI1+fOVD5dsqmCrYqvNVF6qurbqu6vqqr6ue2NyhDMiYgeBZXqliKBSJbXBV8FUIVaBEuipQ' \
			b'S9NWbVe1PdUGit2ZqqOmxYAfVCwSvqamh5qeaqql2qPBQSNP2eOZ8q+rrgGovKs8EUispXzqKjRVH6qecGQAJUfC5YkbaENJ8HpT9VSmALGguiRYUOwqoDukJ2IGFbQBK9BA4dkEuVj2RsOGRzxRGKtPXl4Sh9ib2ARvSeksaOBOEgwSp5EwTnPrOJu7yvyz' \
			b'TjlH9NxpNnQqKj0LRy8iSSUTIbH8WspUlkYKMZKf0y4kv5GGg4W330tqtaTmG4GPiDVX51mndDcs+WjsKFFqf9HcVObutjVnTRCmSTW3wq12YFfHPBQqibhIzD6pmHA2ZegVBeICA907jGFq/VnaW1e1vmqJcFO1tmrrqm3uMlPCPVNKprT3TCmZ0t0zJe8v' \
			b'gnYUcjFy6awMJJ125zJYsNIPWyODT6YUoWoNXevws/YaTfw7jn3kfctZNxAvg/JORzJeyuD5be+q3mvVjhV5op3pmdda8p2UUGo+1DqzkLruhRu9jqGdziyYKTSx9vVRlIUIk9pzPhImlXUk5AkbXZuQR2RQ3BqIb46FTBGFnmt5QiDe9gIFO8xibauI0eZg' \
			b'QMzdHqJREc35pLgjL6TcwpH50t+C8qO0otQAGy7LiJNnA5Wbyr8PARAOnlr5qah3GgYdw+DuNoOB5R+qyDvNBne3i99xZxgV31TAO90rgJAJP3p+puLdabZYZsuVh6/p8gcNSC0zl9XHdL0ds7aLM0bQ6Rejuw3FwOoDi1ijUyGZP5lGF/SMzIga1a1kq4At' \
			b'V+WJFv0CawqnSz4WQrjmpMmYWT99I4ussuiQNNrQwXPMVgK3ErU1Q63KLLmth+cmrXUoq5FYaOXSSVqWmyho1sDS02Bgra0rc6dQFngZ/00X6/pBx8Y82ic1fVRmGVFmGVFmGTC9F6a7oc6lQmUxycaeVrpf6Wlv/eDszPXKMm6WjkKmnNMKYogdj34R+jsh' \
			b'rD0uwghSqrLrj6USqb2s633DGypS1UwaUUEa0TxKEzRpn70223S1ak7DQ2/Lj2awigHY8XpiZsN6izQWMcmmfXaQWPfrsDOj+MZMeeXSR0wF7blMAZN6wIzIqlmKlZlQ+tbqW2KILXoTSaiwcJjxxTjN6jjNyAAN8407bSjCw1Ijw9I7rKOApFiRFCtjAsW3' \
			b'1TGekcEdZit3HN/t3RaUIP1JEHkJ2jJZaZlOYo37AhMMeyITDJ5Z2Nuit8HUx+gExcoExcoEhS7DUC4kD24yXMEg3cj6tpV1ZO4sdfbYc0N+FMXE2I8HY4IKouRcRk3uXGfOb3h+7dg+Gb9Eg9MBgLu7C2YYkljVFU0GUa0MqqI6oZ6+t8LLE2l/iEBXjOOI' \
			b'WCeQcAIJp3N2p5N1d0xTLqBNZdurbPthxCCy7Vm2vQq1n5lkoHqkxF5K7O+y9p9i3eHyQ8C96B6DdhBBZCOIbIShG6ho8Kn8CknXQBFbjdierD72AgVupcAt40hU5mrLHvAu0zGiwJ1wqpOInYbtTpsN/QmTTxSdLvmQnV5NIWu1hazPZf/WRQ34USslFKB1' \
			b'AUVjkgEbUFSjwNtQCJ5xqsT5p/yQtk5KlpYAbHDMgA5NWWQYt4op26RhTMuK+WnLnGb2E3vAP7aCTCwNpeDEqJr8mKnkh3KgICgJmIjiYE0LZcLqFZausKqFFS1sV0Pbg01s2MFG5WuwtwocRvMJK2GYCMP6Fx0fej3YDKIOscsIe4Ows4c3GVI4GJNCFw09' \
			b'NHb6cAtOfrBPxTAHlqjY9YbFGZj6w7IdhtxYccFiC9ZhsAjT0juofaDzgTUzhkTY7oLmHTWMHU8wZ4Uta99RrWJjsMfeYGyFdLyBFjtL4UU+AZsnW/knMVtRV4P9tbyHEts04Y/NoX0Mlv6T1K1avKP/DltDkQG2X9bYqF7Dp8Yu0xp7Wemp4wfsyqU8PPYM' \
			b'05VIXWFHaw/SWtlcPWbiZzP2kwv2OeOW+LASCcIDSuCUCqdFwS5ZkryVw37XGnljKyo/DPE8+MSb1Skxk+TEiSoTsT21183S2LGPVxXvSR+IbPEPP0oqJP4BTMcVe7sbSQ37sR12c2ObK2+JBe2U5CRv7BnGDugevPaSKrYgUwJdUj3OKomgH4mDVMqUILUK' \
			b'9Zvq/3z3AAEJAQ9WAEN4gLAEhAcQDAIDexv1btn7n1AaoXXI2oasVZAm4YptQAeIC76nyN6E6gzNjN5NyM0QmyN1I0pzZCaoZDSuQ+EGCM5BT2F3OIjxcQIDakq8bMJKjhIBxlpQ5GDIQbAJALnYJyIPUZ8RcR5Rkay2Sd/FXabunxz7LnuF7stG6ZVZm4zK' \
			b't3dlXjts0bPqmooofUTmm0Tsw7RPm3bovImjRim7EhHclw0oaK/Yb1E47DmAfX+BDDfThw0Iadb0X2nfRf6wS2DEUDgsnmOZe4Ie1CtNc3oGCgBB1AXZ6d8PQCFx78e/JagBTlLQZLgRH3hmAOpn/pCt7WMcjSkQ4ztBGcL1nnHWM9I4fSeXoNEQKAdeH6EG' \
			b'mI0Q40JnMBNGRKhFevqy04F3AjuhiCqYgxc9Diet8OOAk9TT3sb2D9As9dTZsOw6+wCQJxmhq/knL0IyVvsEreFYcDoP0uayOL3NGEWvEMA/lLCWLk27Mz5khkEq71K3BKmcbIJU7ogiUmOaGVLLXCcU2IIuABaJBnlIe0ZFLefSy8XJJQyRc8xyGnOg1XcZ' \
			b'bAe+ROBGumaAKzmOwNWAqPZ6DrkDhwS7HHSSwQx2ZzDr8v71yBF7D9cCriLeKNoUq82I1SZ3i7Ca9arNtFeNaeZY3egYq5mXdK5NswaojQBV+tdG+leNWQC1WQdUCZ8DVZmSAHUkag6o0x5WA6LCZ7vYgT0KVOlkkwx2A6q/E0C97eNfzKECT2L8FKx+BKvP' \
			b'3SKw+gysfgrWMc0crEWuEwpsQdcAVj+CFbcDVL1A1QtUvUB1jFqg1a9Dq4TP0apcSdA6es6h1U/RKgG5xmfRqvxRtHpBa8xg2ZA43KP2NqCW9TtQOrRT1I46VXmXukWobTPUtlPUjmnmqC1ynVBgC7oG1EatKh/Ip6gVtSpf5IULSdQCte061Er4HLXKlQS1' \
			b'Y9JzqG2nqJWAqPF2FrXKH0VtK6iNGSxDbXuP2tuA2o5lvYOboLYbUdvlbhFquwy13RS1Y5o5aotcJxTYgq4BtV1EbRdR2wlqO0FtJ6gdoxao7dahVsLnqFWuJKgdk55D7VTlqwFR490sapU/itpOUBszWIba7l5VfJvga1gNhYoTHRQuRCBfxFNALCFStwTE' \
			b'JtNEmakmKqaZgbjMNSfCFqQpjk3UROFWcWxED2VED2VEDxWj5jg261RRGj7D8cCYiOOY9AyOzVQVpQGxdW5WFTWwSHBsRBWVZLAMx/09jm8VjnnKi5qSKS+fdt5Ueui5GSe+EiJ1i3CcTXzNdOIb08xxXOTa6CabMYYtaBuAHCe/Jk5+jUx+jUx+jUx+Y9QC' \
			b'yOsmvxo+B7JyJgHy6DkH5OnkVwN6K+FLICuPFMgy+U0yWAbkpr5H8q1CcmCpZ8dIDoLkIEgOI5JD7hYhOWRIDlMkj2nmSC5yzYmwBWkDkKPVBG4HIAcBchAgBwHyGLUAclgHZAmfA1kZkwB5THoOyGEKZAkIIIdZICuLFMhBgBwzWAjk5h7ItwrIrM9CHYk+' \
			b'i63NGrnUVbQUlBCpWwTkTKtlplqtmGYO5CLXnAhbkDYAOSq2TFRsqb2gEcWWEcVWjFoAeZ1iS8PnQFbGJEAek54D8lSxpQEB5FnF1sAiBbIotpIMFgL53pzqdgGZVVyoIFFxGdFyyedX+KJA7nK3CMiZostMFV0xzRzIRa45EbYgbQBy1HWZqOsyousyousy' \
			b'ouuKUQsgr9N1afgcyMqYBMhj0nNAnuq6NCCAPKvrGlikQBZdV5LBQiDbCOTm9LHcZscL311EN6LqNeAh7vEZFMOg5gu324P22uRukfbaZNprM9Vej2nm2usi15wIW5A2KLBNVGAbBnXDX3PrRJEtlsp8kQAuJEkUimyzBtwaPldkK4MSRfaY9Jwi20wV2RIQ' \
			b'UmBmFdlKviqyjSiyYwYLwT1vlDXZrXNaS1CXscm66haddSjeA4LxhSpe3ui29c+WOzPeEJouQbXio52zzd2Vtgog/sSW0oz/RQdd5Dyhwha0DUDGboKOizEx0UII3Wwg2QXJWky5ss7ZTvCLpGL/LJnl/bPyZrrlAF4zAJ50zZY3H6Bm61n4aspD34zaBJ+r' \
			b'lQA5Fn8C5N494KYsdHS1DFxfWkAfX6eMTcX7tYa+7Z0y78ACG1FrTkbaTkbaTkbabgSzy92ikbbLsOwyLNdDojmSi2wzF6RjzmmDebQMuF0ccLsIaCcDbicDbtlDFGMXmHbrBtwSPge08icZcI9Jzw243RTVEtBbCV+CWglWUMvuoiSDhX1yYcl1fMC+nznv' \
			b'DmnLq1L8GVjGs5VVKSurUnZclZIQqVuCZ5utStnpqlRMM4NzmWtOhC1I077ZxkUpGxelrCxKWVmUsrIoFaPmQLbrFqU0fAbkgTERyDHpGSDb6aKUBsTxSbOLUgOLBMhWFqWSDBYCuTDuOhCQk3MB7uF8cDjz0pRlx3CWpSkrS1N2XJqyIXeL4JwtTfUCZ+zJ' \
			b'xcEQnYA6wN+WC1Rl3jkptiBwAHVcoLJxgcrKApWVBSorC1QxagHqdQtUGj4HtbInAfWY9ByopwtUGtBbCV+CWt4PoJYFqiSDhaC+t/26VXB2bPsF5ovtlxPbLye2X260/ZKH1C2Bs8tsv9zU9iummQG5zDUnwhakKZBdtP1y0fbLie2XE9svJ7ZfMWoOZLfO' \
			b'9kvDZ0AeGBOBHJOeAbKb2n5pQC9ffy+BPLBIgOzE9ivJYCGQ742/DgVkVbXeEKB5kyJqQDYpOjkiQ9VhbtyqKH6pWwTobKuim25VjGnmgN7mGNCZlwI67lbE7QBo2avoZK+ik72KMWoB6HXbFTV8DmhlTALoMeneDXc5rKebFodAVmKVsFZGKaxl02KSzTJY' \
			b'm8IS7DA7Kvasxd7hFKpDoHVnlfVekMkqajBxqqJ2o35a3qVuESYz9bSbqqcLKBaZTTK2BTkDDm1VHHzjojp69uwbZ9fBTlLOYadlT2A3ErFB+zyEsLMwk5cDzKzAbEx2x73BprDPuofXscCL9UxQBvgpvEYNk7xL3SJ4ZRom5zfDq8hskrEtyBng5Wfg5bfA' \
			b'a50SSVPO4aVlT+A1em6Cl4aYh5e8HOAlqqOY7K7wKqym7uF1LPBiS0Zo2dopvEYbRnmXukXwymwYXbsZXkVmk4xtQc4Ar3YGXu0WeK0zU9SUc3hp2RN4jURsgpeGmIeXvBzgJcaJMdld4WXvxHbbW62v4XPdMOPppzAcD3VzhVsEwz6DYT+d2I1p5nicyziG' \
			b'tqWX4rGvZs+gcXLGm8KSL2OxC3yuO+FNw+f4VKYk+ByJmtPS9FOYSkBM5/pZpCrRitRekBoz2BGp96dFnTpSPWtWwd16glQ/6lTlXeqWINVnOlU/1anGNDOklrlOKLAFXcMZwfU8Ur2oVL2oVL2oVDVmcV7wOn2qhs+QOjAlIjUSNYNUP9WnakCI9aw+dWCP' \
			b'INWLPjXJYEek3o3jom41Ulll6vkrEROkjspSeZe6RUjNlKV+qiyNaeZI3egYqZmXInXNuW5edKVedKVedKUas0DqOkWphs+RqkxJkDoSNYfUqYpUA0KsZ1WkA3sUqaIiTTLYEamhPI07tR90p2D9u69zVPlMf3o/OQE8BXXYk3HwruCuFwC8vQzIw4bDxMmh' \
			b'MsSiIT9V3I82DRImdVeyH0b8tB0YE5052Z/J9zMUeLFmyL06lqSVPsw1BmLS4MWkwYtJg0Yuj40DpWF6yH9i4zB7grmmlTcUyrapabH6zrUU0dgBdc+tRaiGE879rMUDDjofOKlNhlg9RPbkTQZ782+HX7QeLJUtXbjtaKuLw5/jv6dD/N0WCGfQLSDbb1Et' \
			b'bVIrtdX2z2vg7PnjOdN/v+f5u6uc6b/twxZbPmex9TMWi79fQUXJxb4+iOTj21buiD9i4ds1sp/L/Zy8b/mOzA19yKLRjSdH/DELsPgKH7ToC+EtB3r7Et5wJI33ooZ7W6Pd8Pac0xBmv19hBsNu5Osssu2tH4V6GM1mwk2M2zIgGacwe/zWWDf9lFgoPyW2' \
			b'RNx3nW7sONXYKPowbgv7b78Xfv/r0B8mauxopgEWrdpcE7AYCukRHeu/3rXrl7s2wELorS/Z1lPiO43P3T4/tUU1uOw7enserGwaqONLhTu1+c1+hD4R+Gv6+lZj59p5s2Utd78DF6go1g9edmzv147WXY/xOH/vx+wm3ntv6mlOGgZp99fS4C/QLW1s8KGI' \
			b'd9fb8N9Yow+5j2c/sLrWXlPjXy7aXKbxXxkohMEnc9lOgPBiLb7SyHixO+Nlj92Buy6MXBEfGFVe96BIsdFeUWW6qH+AXPp9YaHdpu8scNC6RTiAHo2xcBUMGC8fKjW1XG03QsLtBomwV0gkn2O+Np3Osc8Prh8KKQyaZGPUteh6FsLg6hAIhej73US/PYzo' \
			b'9/eifyyif+Ve4MhFvy1EP+wm+nuaL+Qzhfpe9I9F9M0tF/2uEP1rWbKF7n+w27j6CkCDU/nonTGHW8raeQl3f0J/UIFPp9r7WgHg9T5WodVLBf8KKwENf1B6l5lu6x5QZizl5QrtYaQc2iA3UQgdrmlfY2N0Kf3P9TXth9fzQDy6VNdz0CYdn3Ob0+9cRq9z' \
			b'VX1OX10cpenNgc0OJm11fZn22sK48KYF+CrNMovDoQwM0lYY5oRztqebRNSr/QwMZtRwpuv5Y9/1vcAua3KPo6m90gAia1YbPgnyGk0H1jSjUIj0NUtlcxCpbNYLps2slK9JPLceR7yrCaNjW4xjEVex5G43iSy/zm19F4vuJVvZLacD72C/iMOe+WBvLkbR' \
			b'3JoHhFiWZHMvyactyR3/b5Tk7rQluVNJ7jZLsq0u2iruG2tYcBsW2UReRVjbbNsVS9CM5EAyUmnoHNU0z2W7WK2NqqJQl42br8Ox/rhuQtwPxBOEGeaBOSlDgoN5DtXY7oWM4DMAnOw326HQAyRyGHDhWaguWfiGv1GgAhrGYLsxxJc8cSNb/BK22JIzzVFw' \
			b'p5lCeODQgMorcyks4VLZhEvjvVPLvQsjt7XIcy3xuEupvyqzQXHdl+2mvFrQVu5SK9tawZnWb/gwR91PW7m2qMMbmAGt3bF6IFXq+tnOjAjM967oh29uVjO7A3SvM5hSdMrO0jqaXssEprsXo81ihHo5vtlx+vkRdjciR4aaIyyw9A9WEKL6wUrapv5eqLYI' \
			b'1VGqXFKh6pnGIxIqyiYVqpvT+h2rXMEi72i1ecfQ70GImmMUomtahx7HzKGafgJsk1Bdu4q4NZdprswexQqJbRiI8wCy0u9rbfusFtWRCtzNL1fcpMytkzNUy0ksR6QN2OGWH3ZrxCwfSt4EnvvyJLbt+IXjM5E9ieIF5ubhzTndna34iF05lsXU+fErm89M' \
			b'4S1YMKEfTQjUKgw2HXJkCL78ib3m2LHbYgsXTDQHJ8eiuOw/McpRP4kG/SqlhHiwIotxULqVOXQxKN3L/DFx9tDEUQsx8wczkOSJNzsH3sg2CSUbkZlQd2hCqbEq/qDBl2s383b8YwL9oQn01fwflhjWvmv5HRMYDk1gqC71x8S1U+KK05b0FPLx9KTNJyZN' \
			b'j0vC9nXekmn0OKQgC2hzBZocq+uq8RgiPoJoOGrIp8cLvUFPKX8krm2VPKSunfnLgnCo+ThzYTJ/ZmN36Druqkv9MXH9YesYivC5aq67PVY1+oXDOaiUMy+MWC6TGHO8qQ/ehbpq304oTzp/LKO2exAZfEjmhqQmVOLkWzbj4+UdBsNXT2WtkzrYOHJxdjtC' \
			b'18oQuDeVIyxJzzvm4kZnujnfEH2lOPY2iRQmY6fkpAo2juJ2kahWPyq9q1xhwnoFN0w2N4aSovlbJV19dVJOqiBsGWDsLmDC7R3FbIZ/0JAMrkvul7pBwbElVKamYGa0t0keoW46JSdV0B2PPJrqJpywob9Vkmirk3KigqqPRxJddRNO2HCrJhVQuJ+Skyow' \
			b'J1AF43c7d66Krjo21wQilOaaG0NJldg9Nw79pomf26WN6Ks9OlTtjC/RvSaGcMXtpK3aH2PslDksc+sYhMW19a7f+HZ3129JU/jkj5lPrjoCJ3zaNjm5UT6F6gic8OmkVwLwhYdtTha75X+X8Hl0rGkPSeDrU+vCUcFjhsV7Yfa2GcpRMxtmBUfthMcHXvY4' \
			b'MI9tddxOVrG3zW+Om8euOm4nPG5Omse+Om4nPMbxrjCDaZXndnjW9zi7j1kCPyzUqPzjYLOkKhqOhHMoOz52rMZZjxIyzIb0VeIkYFsERBUgcKhS1wSN0CVWPFDRaxF6/lalyMRYt22DUNAjIKSPRlpdLdYeNX+Ny/OWHdktI1uMaqn3Xo1CSCabDsxoOlgN' \
			b'nf8/lorl2w==' 

	_PARSER_TOP             = 'expr_commas'
	_PARSER_CONFLICT_REDUCE = {'BAR'}

	_VAR_TEX_XLAT = {
		r'\mathbb{R}'  : 'Reals',
		r'\mathbb{C}'  : 'Complexes',
		r'\mathbb{N}'  : 'Naturals',
		r'\mathbb{N}_0': 'Naturals0',
		r'\mathbb{Z}'  : 'Integers',
	}

	_UPARTIAL = '\u2202'
	_USUM     = '\u2211'
	_UINTG    = '\u222b'
	_LETTER   = fr'[a-zA-Z]'
	_LETTERU  = fr'[a-zA-Z_]'

	_TEXGREEK = '(?:' + '|'.join (reversed (sorted (f'\\\\{g}' for g in AST.Var.GREEK))) + ')'
	_TEXXLAT  = '(?:' + '|'.join (reversed (sorted (x.replace ('\\', '\\\\') for x in _VAR_TEX_XLAT))) + ')'
	_VARPY    = fr'(?:{_LETTER}(?:\w|\\_)*)'
	_VARTEX   = fr'(?:{_TEXGREEK}|{_TEXXLAT}|\\partial|(?:(?:\\overline|\\bar|\\widetilde|\\tilde)\s*)?\\infty)'
	_VARTEX1  = fr'(?:(\d)|({_LETTER})|({_VARTEX}))'
	_VARUNI   = fr'(?:{"|".join (AST.Var.UNI2PY)})'
	_VAR      = fr'(?:{_VARPY}|{_VARTEX}|{_VARUNI})'

	_STR      = r'\'(?:\\.|[^\'])*\'|"(?:\\.|[^"])*["]'

	_FUNCPY   = f"(?:{'|'.join (reversed (sorted (AST.Func.PY - {'@', '%'})))})"
	_FUNCTEX  = f"(?:{'|'.join (reversed (sorted (AST.Func.TEX)))})"

	TOKENS    = OrderedDict ([ # order matters
		('SQRT',          r'sqrt\b|\\sqrt(?!{_LETTER})'),
		('LOG',           r'log\b|\\log(?!{_LETTER})'),
		('FUNC',         fr'(@|\%|{_FUNCPY}(?!\w|\\_))|\\({_FUNCTEX})(?!{_LETTERU})|\$({_LETTERU}\w*)|\\operatorname\s*{{\s*(@|\\\%|{_LETTER}(?:\w|\\_)*)\s*}}'),
		('LIM',          fr'\\lim(?!{_LETTER})'),
		('SUM',          fr'\\sum(?:\s*\\limits)?(?!{_LETTER})|{_USUM}'),
		('INTG',         fr'\\int(?:\s*\\limits)?(?!{_LETTER})|{_UINTG}'),
		('LEFT',         fr'\\left(?!{_LETTER})'),
		('RIGHT',        fr'\\right(?!{_LETTER})'),
		('CDOT',         fr'\\cdot(?!{_LETTER})'),
		('TO',           fr'\\to(?!{_LETTER})'),
		('MAPSTO',       fr'\\mapsto(?!{_LETTER})'),
		('BEG_MAT',       r'\\begin\s*{\s*matrix\s*}'),
		('END_MAT',       r'\\end\s*{\s*matrix\s*}'),
		('BEG_BMAT',      r'\\begin\s*{\s*bmatrix\s*}'),
		('END_BMAT',      r'\\end\s*{\s*bmatrix\s*}'),
		('BEG_VMAT',      r'\\begin\s*{\s*vmatrix\s*}'),
		('END_VMAT',      r'\\end\s*{\s*vmatrix\s*}'),
		('BEG_PMAT',      r'\\begin\s*{\s*pmatrix\s*}'),
		('END_PMAT',      r'\\end\s*{\s*pmatrix\s*}'),
		('BEG_CASES',     r'\\begin\s*{\s*cases\s*}'),
		('END_CASES',     r'\\end\s*{\s*cases\s*}'),
		('FRAC2',        fr'\\frac\s*{_VARTEX1}\s*{_VARTEX1}'),
		('FRAC1',        fr'\\frac\s*{_VARTEX1}'),
		('FRAC',          r'\\frac'),
		('IF',            r'if(?!{_LETTERU})'),
		('ELSE',          r'else(?!{_LETTERU})'),
		('NUM',           r'(?:(\d*\.\d+)|(\d+)\.?)([eE][+-]?\d+)?'),
		('VAR',          fr"(?:(\\partial\s?|{_UPARTIAL})({_VAR})|({_VAR}))('*)"),
		('ATTR',         fr'\.(?:({_LETTERU}\w*)|\\operatorname\s*{{\s*({_LETTER}(?:\w|\\_)*)\s*}})'),
		('STR',          fr"(?<!{_LETTERU}|')({_STR})|\\text\s*{{\s*({_STR})\s*}}"),
		# ('PRIMES',        r"'+"),
		('SUB1',         fr'_{_VARTEX1}'),
		('SUB',           r'_'),
		('CARET1',       fr'\^{_VARTEX1}'),
		('CARET',         r'\^'),
		('DBLSTAR',       r'\*\*'),
		('PARENL',        r'\('),
		('PARENR',        r'\)'),
		('CURLYL',        r'{'),
		('CURLYR',        r'}'),
		('BRACKL',        r'\['),
		('BRACKR',        r'\]'),
		('BAR',           r'\|'),
		('PLUS',          r'\+'),
		('MINUS',         r'-'),
		('STAR',          r'\*'),
		('INEQ',         fr'==|!=|\\neq?|<=|\\le|<|\\lt|>=|\\ge|>|\\gt|{"|".join (AST.Eq.UNI2PY)}'),
		('EQ',            r'='),
		('DIVIDE',        r'/'),
		('EXCL',          r'!'),
		('AMP',           r'&'),
		('COLON',         r':'),
		('DBLSLASH',      r'\\\\'),
		('COMMA',         r','),
		('IGNORE_CURLY',  r'\\underline|\\mathcal|\\mathbb|\\mathfrak|\\mathsf|\\mathbf|\\textbf'),
		('ignore',        r'\\,|\\:|\\?\s+|\\text\s*{\s*[^}]*\s*}'),
	])

	def expr_commas_1   (self, expr_comma, COMMA):                              return expr_comma if expr_comma.is_comma else AST (',', (expr_comma,))
	def expr_commas_2   (self, expr_comma):                                     return expr_comma
	def expr_commas_3   (self):                                                 return AST (',', ())
	def expr_comma_1    (self, expr_comma, COMMA, expr):                        return AST.flatcat (',', expr_comma, expr)
	def expr_comma_2    (self, expr):                                           return expr

	def expr            (self, expr_eq):                                        return expr_eq

	def expr_eq_1       (self, expr_lambda1, EQ, expr_lambda2):                 return AST ('=', '=', expr_lambda1, expr_lambda2)
	def expr_eq_2       (self, expr_lambda):                                    return expr_lambda

	def expr_lambda_1   (self, expr_commas, COLON, expr_eq):                    return _expr_lambda (expr_commas, expr_eq)
	def expr_lambda_2   (self, expr_mapsto):                                    return expr_mapsto

	def expr_mapsto_1   (self, expr_paren, MAPSTO, expr_eq):                    return _expr_mapsto (expr_paren, expr_eq)
	def expr_mapsto_2   (self, expr_piece):                                     return expr_piece

	def expr_piece_1     (self, expr_ineq, IF, expr, ELSE, expr_lambda):
		return \
				AST ('piece', ((expr_ineq, expr),) + expr_lambda.pieces) \
				if expr_lambda.is_piece else \
				AST ('piece', ((expr_ineq, expr), (expr_lambda, True)))

	def expr_piece_2     (self, expr_ineq, IF, expr):                           return AST ('piece', ((expr_ineq, expr),))
	def expr_piece_3     (self, expr_ineq):                                     return expr_ineq

	def expr_ineq_2     (self, expr_add1, INEQ, expr_add2):                     return AST ('=', AST.Eq.ANY2PY.get (INEQ.text, INEQ.text), expr_add1, expr_add2)
	def expr_ineq_3     (self, expr_add):                                       return expr_add

	def expr_add_1      (self, expr_add, PLUS, expr_mul_exp):                   return AST.flatcat ('+', expr_add, expr_mul_exp)
	def expr_add_2      (self, expr_add, MINUS, expr_mul_exp):                  return AST.flatcat ('+', expr_add, expr_mul_exp.neg (stack = True))
	def expr_add_3      (self, expr_mul_exp):                                   return expr_mul_exp

	def expr_mul_exp_1  (self, expr_mul_exp, CDOT, expr_neg):                   return AST.flatcat ('*', expr_mul_exp, expr_neg)
	def expr_mul_exp_2  (self, expr_mul_exp, STAR, expr_neg):                   return AST.flatcat ('*', expr_mul_exp, expr_neg)
	def expr_mul_exp_3  (self, expr_neg):                                       return expr_neg

	def expr_neg_1      (self, MINUS, expr_neg):                                return expr_neg.neg (stack = True)
	def expr_neg_2      (self, expr_diff):                                      return expr_diff

	def expr_diff       (self, expr_div):                                       return _expr_diff (expr_div)

	def expr_div_1      (self, expr_div, DIVIDE, expr_mul_imp):                 return AST ('/', expr_div, expr_mul_imp)
	def expr_div_2      (self, expr_div, DIVIDE, MINUS, expr_mul_imp):          return AST ('/', expr_div, expr_mul_imp.neg (stack = True))
	def expr_div_3      (self, expr_mul_imp):                                   return expr_mul_imp

	def expr_mul_imp_1  (self, expr_mul_imp, expr_int):                         return _expr_mul_imp (expr_mul_imp, expr_int, self._USER_FUNCS)
	def expr_mul_imp_2  (self, expr_int):                                       return expr_int

	def expr_int_1      (self, INTG, expr_sub, expr_super, expr_add):           return _expr_int (expr_add, (expr_sub, expr_super))
	def expr_int_2      (self, INTG, expr_add):                                 return _expr_int (expr_add)
	def expr_int_3      (self, expr_lim):                                       return expr_lim

	def expr_lim_1      (self, LIM, SUB, CURLYL, expr_var, TO, expr, CURLYR, expr_neg):                           return AST ('lim', expr_neg, expr_var, expr)
	def expr_lim_2      (self, LIM, SUB, CURLYL, expr_var, TO, expr, caret_or_dblstar, PLUS, CURLYR, expr_neg):   return AST ('lim', expr_neg, expr_var, expr, '+')
	def expr_lim_3      (self, LIM, SUB, CURLYL, expr_var, TO, expr, caret_or_dblstar, MINUS, CURLYR, expr_neg):  return AST ('lim', expr_neg, expr_var, expr, '-')
	def expr_lim_6      (self, expr_sum):                                                                         return expr_sum

	def expr_sum_1      (self, SUM, SUB, CURLYL, expr_var, EQ, expr, CURLYR, expr_super, expr_neg):               return AST ('sum', expr_neg, expr_var, expr, expr_super)
	def expr_sum_2      (self, expr_func):                                                                        return expr_func

	def expr_func_1     (self, SQRT, expr_func_arg):                            return _expr_func (1, 'sqrt', expr_func_arg)
	def expr_func_2     (self, SQRT, BRACKL, expr, BRACKR, expr_func_arg):      return _expr_func (1, 'sqrt', expr_func_arg, expr)
	def expr_func_3     (self, LOG, expr_func_arg):                             return _expr_func (1, 'log', expr_func_arg)
	def expr_func_4     (self, LOG, expr_sub, expr_func_arg):                   return _expr_func (1, 'log', expr_func_arg, expr_sub)
	def expr_func_5     (self, FUNC, expr_func_arg):                            return _expr_func_func (FUNC, expr_func_arg)
	def expr_func_6     (self, FUNC, expr_super, expr_func_arg):
		func = _FUNC_name (FUNC)

		return \
				AST ('^', _expr_func_func (FUNC, expr_func_arg), expr_super) \
				if expr_super.remove_curlys () != AST.NegOne or not AST ('func', func, ()).is_trigh_func_noninv else \
				_expr_func_func (f'a{func}', expr_func_arg)

	def expr_func_8     (self, expr_pow):                                       return expr_pow

	def expr_func_arg_1 (self, expr_func):                                      return expr_func
	def expr_func_arg_2 (self, MINUS, expr_func):                               return expr_func.neg (stack = True)

	def expr_pow_1      (self, expr_pow, expr_super):                           return AST ('^', expr_pow, expr_super)
	def expr_pow_2      (self, expr_fact):                                      return expr_fact

	def expr_fact_1     (self, expr_fact, EXCL):                                return AST ('!', expr_fact)
	def expr_fact_2     (self, expr_attr):                                      return expr_attr

	def expr_attr_1     (self, expr_attr, ATTR):                                return AST ('.', expr_attr, ATTR.grp [0] or ATTR.grp [1])
	def expr_attr_2     (self, expr_abs):                                       return expr_abs

	def expr_abs_1      (self, LEFT, BAR1, expr_commas, RIGHT, BAR2):           return AST ('|', expr_commas)
	def expr_abs_2      (self, BAR1, expr_commas, BAR2):                        return AST ('|', expr_commas)
	def expr_abs_3      (self, expr_paren):                                     return expr_paren

	def expr_paren_1    (self, LEFT, PARENL, expr_commas, RIGHT, PARENR):       return AST ('(', expr_commas)
	def expr_paren_2    (self, PARENL, expr_commas, PARENR):                    return AST ('(', expr_commas)
	def expr_paren_3    (self, IGNORE_CURLY, CURLYL, expr, CURLYR):             return AST ('{', expr)
	def expr_paren_4    (self, expr_frac):                                      return expr_frac

	def expr_frac_1     (self, FRAC, expr_cases1, expr_cases2):                 return AST ('/', expr_cases1.remove_curlys (), expr_cases2.remove_curlys ())
	def expr_frac_2     (self, FRAC1, expr_cases):                              return AST ('/', _ast_from_tok_digit_or_var (FRAC1), expr_cases.remove_curlys ())
	def expr_frac_3     (self, FRAC2):                                          return AST ('/', _ast_from_tok_digit_or_var (FRAC2), _ast_from_tok_digit_or_var (FRAC2, 3))
	def expr_frac_4     (self, expr_cases):                                     return expr_cases

	def expr_cases_1    (self, BEG_CASES, expr_casess, END_CASES):              return AST ('piece', expr_casess) # translate this on the fly?
	def expr_cases_2    (self, expr_mat):                                       return expr_mat
	def expr_casess_1   (self, expr_casessp, DBLSLASH):                         return expr_casessp
	def expr_casess_2   (self, expr_casessp):                                   return expr_casessp
	def expr_casessp_1  (self, expr_casessp, DBLSLASH, expr_casessc):           return expr_casessp + (expr_casessc,)
	def expr_casessp_2  (self, expr_casessc):                                   return (expr_casessc,)
	def expr_casessc_1  (self, expr_commas1, AMP, expr_commas2):                return (expr_commas1, expr_commas2)
	def expr_casessc_2  (self, expr_commas, AMP):                               return (expr_commas, True)

	def expr_mat_1      (self, LEFT, BRACKL, BEG_MAT, expr_mat_rows, END_MAT, RIGHT, BRACKR):  return _expr_mat (expr_mat_rows) # translate these on the fly?
	def expr_mat_2      (self, BEG_MAT, expr_mat_rows, END_MAT):                               return _expr_mat (expr_mat_rows)
	def expr_mat_3      (self, BEG_BMAT, expr_mat_rows, END_BMAT):                             return _expr_mat (expr_mat_rows)
	def expr_mat_4      (self, BEG_VMAT, expr_mat_rows, END_VMAT):                             return _expr_mat (expr_mat_rows)
	def expr_mat_5      (self, BEG_PMAT, expr_mat_rows, END_PMAT):                             return _expr_mat (expr_mat_rows)
	def expr_mat_6      (self, expr_curly):                                                    return expr_curly
	def expr_mat_rows_1 (self, expr_mat_row, DBLSLASH):                         return expr_mat_row
	def expr_mat_rows_2 (self, expr_mat_row):                                   return expr_mat_row
	def expr_mat_rows_3 (self):                                                 return ()
	def expr_mat_row_1  (self, expr_mat_row, DBLSLASH, expr_mat_col):           return expr_mat_row + (expr_mat_col,)
	def expr_mat_row_2  (self, expr_mat_col):                                   return (expr_mat_col,)
	def expr_mat_col_1  (self, expr_mat_col, AMP, expr_commas):                 return expr_mat_col + (expr_commas,)
	def expr_mat_col_2  (self, expr_commas):                                    return (expr_commas,)

	def expr_curly_1    (self, CURLYL, expr_commas, CURLYR):                    return _expr_curly (expr_commas)
	def expr_curly_2    (self, expr_bracket):                                   return expr_bracket

	def expr_bracket_1  (self, LEFT, BRACKL, expr_commas, RIGHT, BRACKR):       return AST ('[', expr_commas.commas if expr_commas.is_comma else (expr_commas,))
	def expr_bracket_2  (self, BRACKL, expr_commas, BRACKR):                    return AST ('[', expr_commas.commas if expr_commas.is_comma else (expr_commas,))
	def expr_bracket_3  (self, expr_term):                                      return expr_term

	def expr_term_1     (self, STR):                                            return AST ('"', py_ast.literal_eval (STR.grp [0] or STR.grp [1]))
	def expr_term_2     (self, SUB):                                            return AST ('@', '_') # for last expression variable
	def expr_term_3     (self, expr_num):                                       return expr_num
	def expr_term_4     (self, expr_var):                                       return expr_var

	def expr_num        (self, NUM):                                            return AST ('#', NUM.text) if NUM.grp [0] or NUM.grp [2] else AST ('#', NUM.grp [1])
	def expr_var        (self, VAR):
		var = \
				'partial' + AST.Var.ANY2PY.get (VAR.grp [1], VAR.grp [1].replace ('\\_', '_')) \
				if VAR.grp [0] else \
				self._VAR_TEX_XLAT [VAR.grp [2]] \
				if VAR.grp [2] in self._VAR_TEX_XLAT else \
				AST.Var.ANY2PY.get (VAR.grp [2].replace (' ', ''), VAR.grp [2].replace ('\\_', '_'))

		return AST ('@', var + '_prime' * len (VAR.grp [3]))

	def expr_sub_1      (self, SUB, expr_frac):                                 return expr_frac
	def expr_sub_2      (self, SUB1):                                           return _ast_from_tok_digit_or_var (SUB1)

	def expr_super_1    (self, DBLSTAR, expr_func):                             return expr_func
	def expr_super_2    (self, DBLSTAR, MINUS, expr_func):                      return expr_func.neg (stack = True)
	def expr_super_3    (self, CARET, expr_frac):                               return expr_frac
	def expr_super_4    (self, CARET1):                                         return _ast_from_tok_digit_or_var (CARET1)

	def caret_or_dblstar_1 (self, DBLSTAR):                                     return '**'
	def caret_or_dblstar_2 (self, CARET):                                       return '^'

	#...............................................................................................
	_AUTOCOMPLETE_SUBSTITUTE = { # autocomplete means autocomplete AST tree so it can be rendered, not necessarily expression
		'CARET1'             : 'CARET',
		'SUB1'               : 'SUB',
		'FRAC2'              : 'FRAC',
		'FRAC1'              : 'FRAC',
		'expr_super'         : 'CARET',
		'caret_or_doublestar': 'CARET',
	}

	_AUTOCOMPLETE_CONTINUE = {
		'RIGHT' : ' \\right',
		'COMMA' : ',',
		'PARENL': '(',
		'PARENR': ')',
		'CURLYR': '}',
		'BRACKR': ']',
		'BAR'   : '|',
	}

	def _insert_symbol (self, sym, tokinc = 0):
		tokidx       = self.tokidx
		self.tokidx += tokinc

		for sym in ((sym,) if isinstance (sym, str) else sym):
			if sym in self.TOKENS:
				self.tokens.insert (tokidx, lalr1.Token (self._AUTOCOMPLETE_SUBSTITUTE.get (sym, sym), '', self.tok.pos))

				if self.autocompleting:
					if sym in self._AUTOCOMPLETE_CONTINUE:
						self.autocomplete.append (self._AUTOCOMPLETE_CONTINUE [sym])
					else:
						self.autocompleting = False

			else:
				self.tokens.insert (tokidx, lalr1.Token (self._AUTOCOMPLETE_SUBSTITUTE.get (sym, 'VAR'), '', self.tok.pos, ('', '', '', '')))
				self._mark_error ()

			tokidx += 1

		return True # for convenience

	def _mark_error (self, sym_ins = None, tokinc = 0, at = None):
		self.autocompleting = False

		if self.erridx is None:
			self.erridx = self.tokens [self.tokidx].pos if at is None else at

		if sym_ins is not None:
			return self._insert_symbol (sym_ins, tokinc)

	def _parse_autocomplete_expr_commas (self, rule, pos):
		idx = -pos + (self.stack [-pos].sym == 'LEFT')

		if self.stack [idx].sym != 'CURLYL':
			if self.tokens [self.tokidx - 1] == 'COMMA':
				self._mark_error ()

			if self.stack [idx - 1].sym == 'LEFT':
				return self._insert_symbol ('RIGHT')

			return self._insert_symbol ('PARENR' if self.stack [idx].sym == 'PARENL' else 'BRACKR')

		# vector or matrix potentially being entered
		if self.stack [idx - 1].sym == 'CURLYL':
			if self.stack [-1].red.is_null_var:
				return self._mark_error (('CURLYR', 'CURLYR'))
			elif not self.stack [-1].red.is_comma:
				return self._insert_symbol (('COMMA', 'CURLYR', 'COMMA', 'CURLYR'), 1)
			elif len (self.stack [-1].red.commas) == 1 or self.tokens [self.tokidx - 1] != 'COMMA':
				return self._insert_symbol (('CURLYR', 'COMMA', 'CURLYR'))
			else:
				return self._mark_error (('CURLYR', 'CURLYR'))

		if self.stack [-3].sym != 'COMMA' or self.stack [-4].sym != 'expr_comma' or self.stack [-5].sym != 'CURLYL':
			if self.stack [-1].red.is_vec:
				return self._insert_symbol (('COMMA', 'CURLYR'), 1)
			elif self.stack [-1].red.is_comma:
				if len (self.stack [-1].red.commas) == 1 or self.tokens [self.tokidx - 1] != 'COMMA':
					return self._insert_symbol ('CURLYR')
				else:
					return self._mark_error ('CURLYR')

		else:
			cols = \
					len (self.stack [-4].red.vec)             if self.stack [-4].red.is_vec else \
					len (self.stack [-4].red.commas [0].vec)  if self.stack [-4].red.is_comma and self.stack [-4].red.commas [0].is_vec else \
					None

			if cols is not None:
				vec             = self.stack [-1].red.commas if self.stack [-1].red.is_comma else (self.stack [-1].red,)
				self.stack [-1] = lalr1.State (self.stack [-1].idx, self.stack [-1].sym, AST (',', vec + (AST.VarNull,) * (cols - len (vec))))

				return self._mark_error (('CURLYR', 'CURLYR')) if len (vec) != cols else self._insert_symbol (('CURLYR', 'CURLYR'))

		return self._insert_symbol ('CURLYR')

	def _parse_autocomplete_expr_int (self):
		s               = self.stack [-1]
		self.stack [-1] = lalr1.State (s.idx, s.sym, AST ('*', (s.red, AST.VarNull)))
		expr_vars       = set ()

		if self.autocompleting:
			stack = [s [2]]

			while stack:
				ast = stack.pop ()

				if ast.is_var:
					if not (ast.is_differential or ast.is_part_any):
						expr_vars.add (ast.var)
				else:
					stack.extend (filter (lambda a: isinstance (a, tuple), ast))

		expr_vars = expr_vars - {'_'} - {ast.var for ast in AST.CONSTS}

		if len (expr_vars) == 1:
			self.autocomplete.append (f' d{expr_vars.pop ()}')
		else:
			self._mark_error ()

		return True

	def parse_getextrastate (self):
		return (self.autocomplete [:], self.autocompleting, self.erridx)

	def parse_setextrastate (self, state):
		self.autocomplete, self.autocompleting, self.erridx = state

	def parse_error (self): # add tokens to continue parsing for autocomplete if syntax allows
		if isinstance (self.rederr, lalr1.Incomplete):
			self.parse_results.append ((self.rederr.red, self.tok.pos, []))

			return False

		if self.tok != '$end':
			self.parse_results.append ((None, self.tok.pos, []))

			return False

		if self.tokidx and self.tokens [self.tokidx - 1] == 'LEFT':
			for irule, pos in self.strules [self.stidx]:
				if self.rules [irule] [1] [pos] == 'PARENL':
					break
			else:
				raise RuntimeError ('could not find left parenthesis rule')

		else:
			irule, pos = self.strules [self.stidx] [0]

		rule = self.rules [irule]

		if pos == 1 and rule == ('expr_func', ('FUNC', 'expr_func_arg')):
			return self._insert_symbol (('PARENL', 'PARENR'))

		if pos and rule [1] [pos - 1] == 'expr_commas':
			return self._parse_autocomplete_expr_commas (rule, pos)

		if pos >= len (rule [1]): # end of rule
			if rule [0] == 'expr_int': # TODO: Fix this!
				return self._parse_autocomplete_expr_int ()

			return False

		return self._insert_symbol (rule [1] [pos])

	def parse_success (self, red):
		self.parse_results.append ((red, self.erridx, self.autocomplete))

		return True # continue parsing if conflict branches remain to find best resolution

	def parse (self, text):
		if not text.strip ():
			return (AST.VarNull, 0, [])

		self.parse_results  = [] # [(reduction, erridx, autocomplete), ...]
		self.autocomplete   = []
		self.autocompleting = True
		self.erridx         = None

		lalr1.Parser.parse (self, text)

		if not self.parse_results:
			return (None, 0, [])

		rated = sorted ((r is None, -e if e is not None else float ('-inf'), len (a), i, (r, e, a)) \
				for i, (r, e, a) in enumerate (self.parse_results))

		if os.environ.get ('SYMPAD_DEBUG'):
			rated = list (rated)
			print (file = sys.stderr)
			for res in rated:
				res = res [-1]
				res = (res [0].remove_curlys (),) + res [1:] if isinstance (res [0], AST) else res
				print ('parse:', res, file = sys.stderr)
			print (file = sys.stderr)

		res = next (iter (rated)) [-1]

		return (res [0].remove_curlys (),) + res [1:] if isinstance (res [0], AST) else res

class sparser: # for single script
	Parser = Parser

if __name__ == '__main__' and not _RUNNING_AS_SINGLE_SCRIPT: ## DEBUG!
	p = Parser ()
	a = p.parse (r"\int 2x*-dx")
	print (a)
# Convert between internal AST and sympy expressions and write out LaTeX, simple and python code

# TODO: MatrixSymbol ('A', 2, 2)**n
# TODO: ImageSet(Lambda(n, 2 n pi + pi/2), Integers)
# TODO: PurePoly(lambda**4 - 11*lambda**3 + 29*lambda**2 + 35*lambda - 150, lambda, domain='ZZ')
# TODO: sequence(factorial(k), (k,1,oo))

import re
import sympy as sp

sp.numbers   = sp.numbers # medication for pylint
sp.boolalg   = sp.boolalg
sp.fancysets = sp.fancysets


_SYMPY_FLOAT_PRECISION = None
_USER_FUNCS            = set () # set or dict of user function names

_OPS                   = AST.OPS | {'Text'}
_NOPS                  = lambda ops: _OPS - ops

class AST_Text (AST): # for displaying elements we do not know how to handle, only returned from SymPy processing, not passed in
	op = 'text'

	def _init (self, tex, nat = None, py = None):
		self.tex, self.nat, self.py = tex, (tex if nat is None else nat), (tex if py is None else py)

class ExprDontDoIt (sp.Expr): # prevent doit() evaluation of expression a single time
	def doit (self, *args, **kwargs):
		return self.args [0] if self.args [1] == 1 else ExprDontDoIt (self.args [0], self.args [1] - 1)

def _tuple2ast_func_args (args):
	return args [0] if len (args) == 1 else AST (',', args)

def _ast_is_neg (ast):
	return ast.is_minus or ast.is_neg_num or (ast.is_mul and _ast_is_neg (ast.muls [0]))

def _ast_func_call (func, args):
	kw     = {}
	pyargs = []

	for arg in args:
		if arg.is_ass and arg.lhs.is_var:
			name = arg.lhs.as_identifier ()

			if name is not None:
				kw [name] = ast2spt (arg.rhs)
				continue

		pyargs.append (ast2spt (arg))

	return func (*pyargs, **kw)

def _trail_comma (obj):
	return ',' if len (obj) == 1 else ''

#...............................................................................................
def ast2tex (ast): # abstract syntax tree -> LaTeX text
	return _ast2tex_funcs [ast.op] (ast)

def _ast2tex_wrap (obj, curly = None, paren = None):
	s = ast2tex (obj) if isinstance (obj, AST) else str (obj)

	if (obj.op in paren) if isinstance (paren, set) else paren:
		return f'\\left({s} \\right)'

	if (obj.op in curly) if isinstance (curly, set) else curly:
		return f'{{{s}}}'

	return s

def _ast2tex_curly (ast):
	# return _ast2tex_wrap (ast, not ast.is_single_unit)
	return \
			f'{ast2tex (ast)}'                    if ast.is_single_unit else \
			f'{{{ast2tex (ast)}}}'                if not ast.is_comma else \
			f'{{\\left({ast2tex (ast)}\\right)}}'

def _ast2tex_paren (ast, ops = {}):
	return _ast2tex_wrap (ast, 0, not (ast.is_paren or (ops and ast.op not in ops)))
	# return ast2tex (ast) if ast.is_paren or (ops and ast.op not in ops) else f'\\left({ast2tex (ast)} \\right)'

def _ast2tex_paren_mul_exp (ast, ret_has = False, also = {'=', '+', 'lamb'}):
	if ast.is_mul:
		s, has = _ast2tex_mul (ast, True)
	else:
		s, has = ast2tex (ast), ast.op in also

	s = _ast2tex_wrap (s, 0, has) # f'\\left({s} \\right)' if has else s

	return (s, has) if ret_has else s

def _ast2tex_eq_hs (ast, hs, lhs = True):
	return _ast2tex_wrap (hs, 0, (hs.is_lamb or hs.is_ass or (lhs and hs.is_piece)) if ast.is_ass else {'=', 'piece', 'lamb'})

def _ast2tex_num (ast):
	m, e = ast.mant_and_exp

	return m if e is None else f'{m} \\cdot 10^{_ast2tex_curly (AST ("#", e))}'

_ast2tex_var_xlat = {'Naturals', 'Naturals0', 'Integers', 'Reals', 'Complexes'}

def _ast2tex_var (ast):
	if not ast.var:
		return '{}' # Null var

	if ast.var in _ast2tex_var_xlat:
		return sp.latex (getattr (sp, ast.var))

	v = ast.as_var.var
	p = ''

	while v [-6:] == '_prime':
		v, p = v [:-6], p + "'"

	n = v.replace ('_', '\\_')
	t = AST.Var.PY2TEX.get (n)

	return ( \
			t or n            if not ast.diff_or_part_type else
			f'd{t or n}'			if ast.is_diff_any else
			'\\partial'       if ast.is_part_solo else
			f'\\partial{t}'   if t else
			f'\\partial {n}'
	) + p

def _ast2tex_attr (ast):
	a = ast.attr.replace ('_', '\\_')
	a = a if ast.args is None else f'\\operatorname{{{a}}}{_ast2tex_paren (_tuple2ast_func_args (ast.args))}'

	return f'{_ast2tex_paren (ast.obj, {"=", "#", ",", "-", "+", "*", "/", "lim", "sum", "intg", "piece"})}.{a}'

def _ast2tex_mul (ast, ret_has = False):
	t   = []
	p   = None
	has = False

	for n in ast.muls:
		# s = _ast2tex_paren (n) if n.is_add or (n.is_piece and n is not ast.muls [-1]) or (p and _ast_is_neg (n)) else ast2tex (n)
		s = _ast2tex_wrap (n, \
				_ast_is_neg (n) or (n.is_intg and n is not ast.muls [-1]) or (n.strip_lim_sum ().is_intg and n is not ast.muls [-1]), \
				n.op in {'=', '+', "lamb"} or (n.is_piece and n is not ast.muls [-1]))

		if p and (n.op in {'!', '#', 'mat'} or n.is_null_var or p.op in {'lim', 'sum', 'diff', 'intg', 'mat'} or \
				(n.is_pow and n.base.is_pos_num) or (n.op in {'/', 'diff'} and p.op in {'#', '/'}) or _ast_is_neg (n) or \
				(p.is_div and (p.numer.is_diff_or_part_solo or (p.numer.is_pow and p.numer.base.is_diff_or_part_solo)))):
			t.append (f' \\cdot {s}')
			has = True

		elif p and (p.op in {'sqrt'} or \
				p.is_diff_or_part_solo or n.is_diff_or_part_solo or p.is_diff_or_part or n.is_diff_or_part or \
				(p.is_long_var and n.op not in {'(', '['}) or (n.is_long_var and p.op not in {'(', '['})):
			t.append (f'\\ {s}')
		else:
			t.append (f'{"" if not p else " "}{s}')

		p = n

	return (''.join (t), has) if ret_has else ''.join (t)

def _ast2tex_pow (ast, trighpow = True):
	# b = _ast2tex_curly (ast.base) if ast.base.is_mat else ast2tex (ast.base) # TODO: REMOVE
	b = _ast2tex_wrap (ast.base, {'mat'}, not (ast.base.op in {'@', '"', '(', '|', 'func', 'mat'} or ast.base.is_pos_num))
	p = _ast2tex_curly (ast.exp)

	if ast.base.is_trigh_func_noninv and ast.exp.is_single_unit and trighpow:
		i = len (ast.base.func) + (15 if ast.base.func in {'sech', 'csch'} else 1)

		return f'{b [:i]}^{p}{b [i:]}'

	return f'{b}^{p}'

	# if ast.base.op in {'@', '(', '|', 'mat'} or ast.base.is_pos_num: # TODO: REMOVE
	# 	return f'{b}^{p}'

	# return f'\\left({b} \\right)^{p}'

def _ast2tex_log (ast):
	return \
			f'\\ln{_ast2tex_paren (ast.log)}' \
			if ast.base is None else \
			f'\\log_{_ast2tex_curly (ast.base)}{_ast2tex_paren (ast.log)}'

_ast2tex_func_xlat = {
	'diag': True,
	'eye': True,
	'gamma': '\\Gamma',
	'ones': True,
	'zeros': True,
	'zeta': '\\zeta',
}

def _ast2tex_func (ast):
	act = _ast2tex_func_xlat.get (ast.func)

	if act is not None:
		try:
			if act is True:
				return ast2tex (spt2ast (_ast_func_call (getattr (sp, ast.func), ast.args)))

			return f'{act}{_ast2tex_paren (_tuple2ast_func_args (ast.args))}'

		except:
			pass

	if ast.is_trigh_func:
		n = (f'\\operatorname{{{ast.func [1:]}}}^{{-1}}' \
				if ast.func in {'asech', 'acsch'} else \
				f'\\{ast.func [1:]}^{{-1}}') \
				if ast.func [0] == 'a' else \
				(f'\\operatorname{{{ast.func}}}' if ast.func in {'sech', 'csch'} else f'\\{ast.func}')

		return f'{n}{_ast2tex_paren (_tuple2ast_func_args (ast.args))}'

	return \
			f'\\{ast.func}{_ast2tex_paren (_tuple2ast_func_args (ast.args))}' \
			if ast.func in AST.Func.TEX else \
			'\\operatorname{' + ast.func.replace ('_', '\\_').replace ('%', '\\%') + f'}}{_ast2tex_paren (_tuple2ast_func_args (ast.args))}'

def _ast2tex_lim (ast):
	s = ast2tex (ast.to) if ast.dir is None else (_ast2tex_pow (AST ('^', ast.to, AST.Zero), trighpow = False) [:-1] + ast.dir)

	return f'\\lim_{{{ast2tex (ast.lvar)} \\to {s}}} {_ast2tex_paren_mul_exp (ast.lim)}'

def _ast2tex_sum (ast):
	return f'\\sum_{{{ast2tex (ast.svar)} = {ast2tex (ast.from_)}}}^{_ast2tex_curly (ast.to)} {_ast2tex_paren_mul_exp (ast.sum)}' \

_rec_diff_var_single_start = re.compile (r'^d(?=[^_])')

def _ast2tex_diff (ast):
	ds = set ()
	p  = 0

	for n in ast.dvs:
		if n.is_var:
			p += 1

			if n.var:
				ds.add (n)

		else: # n = ('^', ('@', 'diff or part'), ('#', 'int'))
			p += int (n.exp.num)
			ds.add (n.base)

	if not ds:
		return f'\\frac{{d}}{{}}{_ast2tex_paren (ast.diff)}'

	dv = next (iter (ds))

	if len (ds) == 1 and not dv.is_partial:
		return f'\\frac{{d{"" if p == 1 else f"^{p}"}}}{{{" ".join (ast2tex (n) for n in ast.dvs)}}}{_ast2tex_paren (ast.diff)}'

	else:
		s = ''.join (_rec_diff_var_single_start.sub (r'\\partial ', ast2tex (n)) for n in ast.dvs)

		return f'\\frac{{\\partial{"" if p == 1 else f"^{p}"}}}{{{s}}}{_ast2tex_paren (ast.diff)}'

def _ast2tex_intg (ast):
	if ast.from_ is None:
		return \
				f'\\int \\ {ast2tex (ast.dv)}' \
				if ast.intg is None else \
				f'\\int {_ast2tex_wrap (ast.intg, {"diff"}, {"=", "lamb"})} \\ {ast2tex (ast.dv)}'
	else:
		return \
				f'\\int_{_ast2tex_curly (ast.from_)}^{_ast2tex_curly (ast.to)} \\ {ast2tex (ast.dv)}' \
				if ast.intg is None else \
				f'\\int_{_ast2tex_curly (ast.from_)}^{_ast2tex_curly (ast.to)} {_ast2tex_wrap (ast.intg, {"diff"}, {"=", "lamb"})} \\ {ast2tex (ast.dv)}'

_ast2tex_funcs = {
	'=': lambda ast: f'{_ast2tex_eq_hs (ast, ast.lhs)} {AST.Eq.PY2TEX.get (ast.rel, ast.rel)} {_ast2tex_eq_hs (ast, ast.rhs, False)}',
	'#': _ast2tex_num,
	'@': _ast2tex_var,
	'.': _ast2tex_attr,
	'"': lambda ast: f'\\text{{{repr (ast.str_)}}}',
	',': lambda ast: f'{", ".join (ast2tex (c) for c in ast.commas)}{_trail_comma (ast.commas)}',
	'(': lambda ast: f'\\left({ast2tex (ast.paren)} \\right)',
	'[': lambda ast: f'\\left[{", ".join (ast2tex (b) for b in ast.bracks)} \\right]',
	'|': lambda ast: f'\\left|{ast2tex (ast.abs)} \\right|',
	'-': lambda ast: f'-{_ast2tex_wrap (ast.minus, {"#", "-", "*"}, {"=", "+", "lamb"})}',
	'!': lambda ast: _ast2tex_wrap (ast.fact, {'^'}, (ast.fact.op not in {'#', '@', '"', '(', '|', '!', '^', 'vec', 'mat'} or ast.fact.is_neg_num)) + '!',
	'+': lambda ast: ' + '.join (_ast2tex_wrap (n, n.strip_lim_sum ().is_intg and n is not ast.adds [-1], \
			(n.op in ("piece", "lamb") and n is not ast.adds [-1]) or n.op in {'=', 'lamb'}) for n in ast.adds).replace (' + -', ' - '),
	'*': _ast2tex_mul,
	'/': lambda ast: f'\\frac{{{_ast2tex_wrap (ast.numer, 0, (ast.numer.base.is_diff_or_part_solo and ast.numer.exp.remove_curlys ().is_pos_int) if ast.numer.is_pow else ast.numer.is_diff_or_part_solo)}}}{{{ast2tex (ast.denom)}}}',
	'^': _ast2tex_pow,
	'log': _ast2tex_log,
	'sqrt': lambda ast: f'\\sqrt{{{ast2tex (ast.rad.strip_paren_noncomma (1))}}}' if ast.idx is None else f'\\sqrt[{ast2tex (ast.idx)}]{{{ast2tex (ast.rad.strip_paren_noncomma (1))}}}',
	'func': _ast2tex_func,
	'lim': _ast2tex_lim,
	'sum': _ast2tex_sum,
	'diff': _ast2tex_diff,
	'intg': _ast2tex_intg,
	'vec': lambda ast: '\\begin{bmatrix} ' + r' \\ '.join (ast2tex (e) for e in ast.vec) + ' \\end{bmatrix}',
	'mat': lambda ast: '\\begin{bmatrix} ' + r' \\ '.join (' & '.join (ast2tex (e) for e in row) for row in ast.mat) + f'{" " if ast.mat else ""}\\end{{bmatrix}}',
	'piece': lambda ast: '\\begin{cases} ' + r' \\ '.join (f'{ast2tex (p [0])} & \\text{{otherwise}}' if p [1] is True else f'{ast2tex (p [0])} & \\text{{for}}\\: {ast2tex (p [1])}' for p in ast.pieces) + ' \\end{cases}',
	'lamb': lambda ast: f'{ast2tex (ast.vars [0] if len (ast.vars) == 1 else AST ("(", (",", ast.vars)))} \\mapsto {_ast2tex_wrap (ast.lamb, 0, ast.lamb.is_ass or ast.lamb.is_lamb)}',

	'text': lambda ast: ast.tex,
}

#...............................................................................................
def ast2nat (ast): # abstract syntax tree -> simple text
	return _ast2nat_funcs [ast.op] (ast)

def _ast2nat_wrap (obj, curly = None, paren = None):
	s = ast2nat (obj) if isinstance (obj, AST) else str (obj)

	if (obj.op in paren) if isinstance (paren, set) else paren:
		return f'({s})'

	if (obj.op in curly) if isinstance (curly, set) else curly:
		return f'{{{s}}}'

	return s

def _ast2nat_curly (ast, ops = {}):
	return _ast2nat_wrap (ast, ops if ops else (ast.is_div or not ast.is_single_unit or (ast.is_var and ast.var in AST.Var.PY2TEX)))
	# if ops:
	# 	return f'{{{ast2nat (ast)}}}' if ast.op in ops else ast2nat (ast)

	# return f'{{{ast2nat (ast)}}}' if not ast.is_single_unit or (ast.is_var and ast.var in AST.Var.PY2TEX) else ast2nat (ast)

def _ast2nat_paren (ast, ops = {}):
	return _ast2nat_wrap (ast, 0, not (ast.is_paren or (ops and ast.op not in ops)))
	# return ast2nat (ast) if ast.is_paren or (ops and ast.op not in ops) else f'({ast2nat (ast)})'

def _ast2nat_curly_mul_exp (ast, ret_has = False, also = {}):
	if ast.is_mul:
		s, has = _ast2nat_mul (ast, True)
	else:
		s, has = ast2nat (ast), False

	has = has or ((ast.op in also) if isinstance (also, set) else also)
	s   = _ast2nat_wrap (s, has)

	return (s, has) if ret_has else s
	# s = f'{{{s}}}' if has else s

	# return (s, has) if ret_has else s

def _ast2nat_eq_hs (ast, hs, lhs = True):
	return _ast2nat_wrap (hs, 0, (hs.is_ass or (lhs and hs.op in {'piece', 'lamb'})) if ast.is_ass else {'=', 'piece', 'lamb'})

def _ast2nat_mul (ast, ret_has = False):
	t   = []
	p   = None
	has = False

	for n in ast.muls:
		# s = _ast2nat_paren (n)   if n.is_add or (p and _ast_is_neg (n)) or (n.is_piece and n is not ast.muls [-1]) else \
		# 		f'{{{ast2nat (n)}}}' if n.is_piece else \
		# 		ast2nat (n)

		# s = _ast2tex_wrap (n, \
		# 		_ast_is_neg (n) or (n.is_intg and n is not ast.muls [-1]), \
		# 		n.op in {'=', '+', "lamb"} or (n.is_piece and n is not ast.muls [-1]))
		s = _ast2nat_wrap (n, \
				_ast_is_neg (n) or n.is_piece or (n.strip_lim_sum ().is_intg and n is not ast.muls [-1]), \
				n.op in {'=', '+', 'lamb'} or (n.is_piece and n is not ast.muls [-1]))
#				(n.op in {'piece', 'lamb'} and n is not ast.muls [-1]) or n.is_add or (p and _ast_is_neg (n)))

		# if p and (n.op in {'!', '#', 'mat'} or n.is_null_var or p.op in {'lim', 'sum', 'diff', 'intg', 'mat'} or \
		# 		(n.is_pow and n.base.is_pos_num) or (n.op in {'/', 'diff'} and p.op in {'#', '/'}) or _ast_is_neg (n) or \
		# 		(p.is_div and (p.numer.is_diff_or_part_solo or (p.numer.is_pow and p.numer.base.is_diff_or_part_solo)))):
		# 	t.append (f' \\cdot {s}')
		# 	has = True
		if p and (n.op in {'!', '#', 'lim', 'sum', 'intg'} or n.is_null_var or p.op in {'lim', 'sum', 'diff', 'intg'} or \
				(n.is_pow and n.base.is_pos_num) or \
				n.op in {'/', 'diff'} or p.strip_minus ().op in {'/', 'diff'}):
			t.append (f' * {s}')
			has = True

		# elif p and (p.op in {'sqrt'} or \
		# 		p.is_diff_or_part_solo or n.is_diff_or_part_solo or p.is_diff_or_part or n.is_diff_or_part or \
		# 		(p.is_long_var and n.op not in {'(', '['}) or (n.is_long_var and p.op not in {'(', '['})):
		# 	t.append (f'\\ {s}')
		elif p and (p.is_diff_or_part_solo or \
				(n.op not in {'#', '(', '|', '^'} or p.op not in {'#', '(', '|'})):
			t.append (f' {s}')

		# else:
		# 	t.append (f'{"" if not p else " "}{s}')
		else:
			t.append (s)

		p = n

	return (''.join (t), has) if ret_has else ''.join (t)

def _ast2nat_div (ast):
	n, ns = (_ast2nat_wrap (ast.numer, 1), True) if _ast_is_neg (ast.numer) else \
		(_ast2nat_wrap (ast.numer, 0, 1), True) if ((ast.numer.base.is_diff_or_part_solo and ast.numer.exp.remove_curlys ().is_pos_int) if ast.numer.is_pow else ast.numer.is_diff_or_part_solo) else \
		_ast2nat_curly_mul_exp (ast.numer, True, {'=', '+', '/', 'lim', 'sum', 'diff', 'intg', 'piece', 'lamb'})

	d, ds = (_ast2nat_wrap (ast.denom, 1), True) if _ast_is_neg (ast.denom) else _ast2nat_curly_mul_exp (ast.denom, True, {'=', '+', '/', 'lim', 'sum', 'diff', 'intg', 'piece', 'lamb'})
	s     = ns or ds or ast.numer.strip_minus ().op not in {'#', '@', '*'} or ast.denom.strip_minus ().op not in {'#', '@', '*'}

	return f'{n}{" / " if s else "/"}{d}'

def _ast2nat_pow (ast, trighpow = True):
	# b = _ast2tex_curly (ast.base) if ast.base.is_mat else ast2tex (ast.base) # TODO: REMOVE

		# b = _ast2tex_wrap (ast.base, {'mat'}, not (ast.base.op in {'@', '"', '(', '|', 'func', 'mat'} or ast.base.is_pos_num))
		# p = _ast2tex_curly (ast.exp)

		# if ast.base.is_trigh_func_noninv and ast.exp.is_single_unit and trighpow:
		# 	i = len (ast.base.func) + (15 if ast.base.func in {'sech', 'csch'} else 1)

		# 	return f'{b [:i]}^{p}{b [i:]}'

		# return f'{b}^{p}'

	# if ast.base.op in {'@', '(', '|', 'mat'} or ast.base.is_pos_num: # TODO: REMOVE
	# 	return f'{b}^{p}'

	# return f'\\left({b} \\right)^{p}'


	# b = ast2nat (ast.base)
	# p = f'{{{ast2nat (ast.exp)}}}' if ast.exp.strip_minus ().op in {'+', '*', '/', 'lim', 'sum', 'diff', 'intg', 'piece'} else ast2nat (ast.exp)
	b = _ast2nat_wrap (ast.base, 0, not (ast.base.op in {'@', '"', '(', '|', 'mat'} or ast.base.is_pos_num))
	p = _ast2nat_wrap (ast.exp, ast.exp.strip_minus ().op in {'=', '+', '*', '/', 'lim', 'sum', 'diff', 'intg', 'piece', 'lamb'}, {","})

	if ast.base.is_trigh_func_noninv and ast.exp.is_single_unit and trighpow:
		i = len (ast.base.func)

		return f'{b [1 : i + 1]}**{p}{b [i + 1 : -1]}'

	return f'{b}**{p}'

	# if ast.base.op in {'@', '(', '|', 'mat'} or ast.base.is_pos_num:
	# 	return f'{b}**{p}'

	# return f'({b})**{p}'

def _ast2nat_log (ast):
	return \
			f'ln{_ast2nat_paren (ast.log)}' \
			if ast.base is None else \
			f'\\log_{_ast2nat_curly (ast.base)}{_ast2nat_paren (ast.log)}'

def _ast2nat_func (ast):
	if ast.is_trigh_func:
		return f'{ast.func}{_ast2nat_paren (_tuple2ast_func_args (ast.args))}'

	return \
			f'{ast.func}{_ast2nat_paren (_tuple2ast_func_args (ast.args))}' \
			if ast.func in AST.Func.PY or ast.func in _USER_FUNCS else \
			f'${ast.func}{_ast2nat_paren (_tuple2ast_func_args (ast.args))}'

def _ast2nat_lim (ast):
	# s = _ast2nat_wrap (ast.to, {'piece'}) if ast.dir is None else ast2nat (AST ('^', ast [3], AST.Zero)) [:-1] + ast [4]
	s = _ast2nat_wrap (ast.to, {'piece'}) if ast.dir is None else (_ast2nat_pow (AST ('^', ast.to, AST.Zero), trighpow = False) [:-1] + ast.dir)

	return f'\\lim_{{{ast2nat (ast.lvar)} \\to {s}}} {_ast2nat_curly_mul_exp (ast.lim, False, ast.lim.op in {"=", "+", "piece", "lamb"} or ast.lim.is_mul_has_abs)}'

def _ast2nat_sum (ast):
	return f'\\sum_{{{ast2nat (ast.svar)}={_ast2nat_curly (ast.from_, {"piece"})}}}^{_ast2nat_curly (ast.to)} {_ast2nat_curly_mul_exp (ast.sum, False, ast.sum.op in {"=", "+", "piece", "lamb"} or ast.sum.is_mul_has_abs)}' \

def _ast2nat_diff (ast):
	p = 0

	for n in ast.dvs:
		if n.is_var:
			d  = n.diff_or_part_type
			p += 1
		else: # n = ('^', ('@', 'differential'), ('#', 'int'))
			d  = n.base.diff_or_part_type
			p += int (n.exp.num)

	return f'{d.strip () if d else "d"}{"" if p == 1 else f"^{p}"} / {" ".join (ast2nat (n) for n in ast.dvs)} {_ast2nat_paren (ast.diff)}'

def _ast2nat_intg (ast):
	if ast.from_ is None:
		return \
				f'\\int {ast2nat (ast.dv)}' \
				if ast.intg is None else \
				f'\\int {_ast2nat_wrap (ast.intg, ast.intg.op in {"diff", "piece"} or ast.intg.is_mul_has_abs, {"=", "lamb"})} {ast2nat (ast.dv)}'
	else:
		return \
				f'\\int_{_ast2nat_curly (ast.from_)}^{_ast2nat_curly (ast.to)} {ast2nat (ast.dv)}' \
				if ast.intg is None else \
				f'\\int_{_ast2nat_curly (ast.from_)}^{_ast2nat_curly (ast.to)} {_ast2nat_wrap (ast.intg, ast.intg.op in {"diff", "piece"} or ast.intg.is_mul_has_abs, {"=", "lamb"})} {ast2nat (ast.dv)}'

_ast2nat_funcs = {
	'=': lambda ast: f'{_ast2nat_eq_hs (ast, ast.lhs)} {AST.Eq.PY2TEX.get (ast.rel, ast.rel)} {_ast2nat_eq_hs (ast, ast.rhs, False)}',
	'#': lambda ast: ast.num,
	'@': lambda ast: ast.var,
	'.': lambda ast: f'{_ast2nat_paren (ast.obj, {"=", "#", ",", "-", "+", "*", "/", "lim", "sum", "intg", "piece", "lamb"})}.{ast.attr}' \
			if ast.args is None else f'{ast2nat (ast.obj)}.{ast.attr}{_ast2nat_paren (_tuple2ast_func_args (ast.args))}',
	'"': lambda ast: repr (ast.str_),
	',': lambda ast: f'{", ".join (ast2nat (c) for c in ast.commas)}{_trail_comma (ast.commas)}',
	'(': lambda ast: f'({ast2nat (ast.paren)})',
	'[': lambda ast: f'[{", ".join (ast2nat (b) for b in ast.bracks)}]',
	'|': lambda ast: f'{{|{ast2nat (ast.abs)}|}}',
	'-': lambda ast: f'-{_ast2nat_wrap (ast.minus, {"#", "-", "*", "piece"}, {"=", "+", "lamb"})}',
	# '!': lambda ast: f'{_ast2nat_paren (ast.fact)}!' if (ast.fact.op not in {'#', '@', '(', '|', '!', '^', 'vec', 'mat'} or ast.fact.is_neg_num) else f'{ast2nat (ast.fact)}!',
	'!': lambda ast: _ast2nat_wrap (ast.fact, {'^'}, ast.fact.op not in {'#', '@', '"', '(', '|', '!', '^', 'vec', 'mat'} or ast.fact.is_neg_num) + '!',
	'+': lambda ast: ' + '.join (_ast2nat_wrap (n, n.op in {'intg', 'piece'} or (n.strip_lim_sum ().is_intg and n is not ast.adds [-1]), \
			(n.op in ('piece', 'lamb') and n is not ast.adds [-1]) or n.op in {'=', 'lamb'}) for n in ast.adds).replace (' + -', ' - '),
	'*': _ast2nat_mul,
	'/': _ast2nat_div,
	'^': _ast2nat_pow,
	'log': _ast2nat_log,
	# 'sqrt': lambda ast: f'sqrt{_ast2nat_paren (ast.rad)}' if ast.idx is None else f'\\sqrt[{ast2nat (ast.idx)}]{{{ast2nat (ast.rad.strip_paren (1))}}}',
	'sqrt': lambda ast: f'sqrt{_ast2nat_paren (ast.rad)}' if ast.idx is None else f'\\sqrt[{ast2tex (ast.idx)}]{{{ast2tex (ast.rad.strip_paren_noncomma (1))}}}',
	'func': _ast2nat_func,
	'lim': _ast2nat_lim,
	'sum': _ast2nat_sum,
	'diff': _ast2nat_diff,
	'intg': _ast2nat_intg,
	'vec': lambda ast: f'{{{", ".join (ast2nat (e) for e in ast.vec)}{_trail_comma (ast.vec)}}}',
	'mat': lambda ast: ('{' + ', '.join (f'{{{", ".join (ast2nat (e) for e in row)}{_trail_comma (row)}}}' for row in ast.mat) + f'{_trail_comma (ast.mat)}}}') if ast.mat else 'Matrix([])',
	'piece': lambda ast: ' else '.join (f'{_ast2nat_curly (p [0], {"=", "piece", "lamb"})}' if p [1] is True else f'{_ast2nat_curly (p [0], {"=", "piece", "lamb"})} if {_ast2nat_curly (p [1], {"piece", "lamb"})}' for p in ast.pieces),
	'lamb': lambda ast: f'lambda{" " + ", ".join (v.var for v in ast.vars) if ast.vars else ""}: {_ast2nat_wrap (ast.lamb, 0, {"=", "lamb"})}',

	'text': lambda ast: ast.nat,
}

#...............................................................................................
def ast2py (ast): # abstract syntax tree -> Python code text
	return _ast2py_funcs [ast.op] (ast)

def _ast2py_curly (ast):
	return \
			_ast2py_paren (ast) \
			if ast.strip_minus ().op in {',', '+', '*', '/'} or (ast.is_log and ast.base is not None) else \
			ast2py (ast)

def _ast2py_paren (ast):
	return ast2py (ast) if ast.is_paren else f'({ast2py (ast)})'

def _ast2py_div (ast):
	n = _ast2py_curly (ast.numer)
	d = _ast2py_curly (ast.denom)

	return f'{n}{" / " if ast.numer.strip_minus ().op not in {"#", "@"} or ast.denom.strip_minus ().op not in {"#", "@"} else "/"}{d}'

def _ast2py_pow (ast):
	b = _ast2py_paren (ast.base) if _ast_is_neg (ast.base) else _ast2py_curly (ast.base)
	e = _ast2py_curly (ast.exp)

	return f'{b}**{e}'

def _ast2py_log (ast):
	return \
			f'log{_ast2py_paren (ast.log)}' \
			if ast.base is None else \
			f'log{_ast2py_paren (ast.log)} / log{_ast2py_paren (ast.base)}' \

def _ast2py_lim (ast):
	return \
		f'''Limit({ast2py (ast.lim)}, {ast2py (ast.lvar)}, {ast2py (ast.to)}''' \
		f'''{", dir='+-'" if ast.dir is None else ", dir='-'" if ast.dir == '-' else ""})'''

def _ast2py_diff (ast):
	args = sum ((
			(ast2py (n.as_var),) \
			if n.is_var else \
			(ast2py (n.base.as_var), str (n.exp.num)) \
			for n in ast.dvs \
			), ())

	return f'Derivative({ast2py (ast.diff)}, {", ".join (args)})'

def _ast2py_intg (ast):
	if ast.from_ is None:
		return \
				f'Integral(1, {ast2py (ast.dv.as_var)})' \
				if ast.intg is None else \
				f'Integral({ast2py (ast.intg)}, {ast2py (ast.dv.as_var)})'
	else:
		return \
				f'Integral(1, ({ast2py (ast.dv.as_var)}, {ast2py (ast.from_)}, {ast2py (ast.to)}))' \
				if ast.intg is None else \
				f'Integral({ast2py (ast.intg)}, ({ast2py (ast.dv.as_var)}, {ast2py (ast.from_)}, {ast2py (ast.to)}))'

_ast2py_funcs = {
	'=': lambda ast: f'{_ast2py_paren (ast.lhs) if (ast.is_eq and ast.lhs.is_lamb) else ast2py (ast.lhs)} {ast.rel} {ast2py (ast.rhs)}',
	'#': lambda ast: ast.num,
	'@': lambda ast: ast.var,
	'.': lambda ast: f'{ast2py (ast.obj)}.{ast.attr}' if ast.args is None else f'{ast2py (ast.obj)}.{ast.attr}{_ast2py_paren (_tuple2ast_func_args (ast.args))}',
	'"': lambda ast: repr (ast.str_),
	',': lambda ast: f'{", ".join (ast2py (parm) for parm in ast.commas)}{_trail_comma (ast.commas)}',
	'(': lambda ast: f'({ast2py (ast.paren)})',
	'[': lambda ast: f'[{", ".join (ast2py (b) for b in ast.bracks)}]',
	'|': lambda ast: f'abs({ast2py (ast.abs)})',
	'-': lambda ast: f'-{_ast2py_paren (ast.minus)}' if ast.minus.is_add else f'-{ast2py (ast.minus)}',
	'!': lambda ast: f'factorial({ast2py (ast.fact)})',
	'+': lambda ast: ' + '.join (ast2py (n) for n in ast.adds).replace (' + -', ' - '),
	'*': lambda ast: '*'.join (_ast2py_paren (n) if n.is_add else ast2py (n) for n in ast.muls),
	'/': _ast2py_div,
	'^': _ast2py_pow,
	'log': _ast2py_log,
	'sqrt': lambda ast: f'sqrt{_ast2py_paren (ast.rad)}' if ast.idx is None else ast2py (AST ('^', ast.rad.strip_paren (1), ('/', AST.One, ast.idx))),
	'func': lambda ast: f'{ast.func}{_ast2py_paren (_tuple2ast_func_args (ast.args))}',
	'lim': _ast2py_lim,
	'sum': lambda ast: f'Sum({ast2py (ast.sum)}, ({ast2py (ast.svar)}, {ast2py (ast.from_)}, {ast2py (ast.to)}))',
	'diff': _ast2py_diff,
	'intg': _ast2py_intg,
	'vec': lambda ast: 'Matrix([' + ', '.join (f'[{ast2py (e)}]' for e in ast.vec) + '])',
	'mat': lambda ast: 'Matrix([' + ', '.join (f'[{", ".join (ast2py (e) for e in row)}]' for row in ast.mat) + '])',
	'piece': lambda ast: 'Piecewise(' + ', '.join (f'({ast2py (p [0])}, {True if p [1] is True else ast2py (p [1])})' for p in ast.pieces) + ')',
	'lamb': lambda ast: f'lambda{" " + ", ".join (v.var for v in ast.vars) if ast.vars else ""}: {ast2nat (ast.lamb)}',

	'text': lambda ast: ast.py,
}

#...............................................................................................
# Potentially bad __builtins__: eval, exec, globals, locals, vars, hasattr, getattr, setattr, delattr, exit, help, input, license, open, quit, __import__
_builtins_dict               = __builtins__ if isinstance (__builtins__, dict) else __builtins__.__dict__ # __builtins__.__dict__ if __name__ == '__main__' else __builtins__
_ast2spt_func_builtins_names = ['abs', 'all', 'any', 'ascii', 'bin', 'callable', 'chr', 'dir', 'divmod', 'format', 'hash', 'hex', 'id',
		'isinstance', 'issubclass', 'iter', 'len', 'max', 'min', 'next', 'oct', 'ord', 'pow', 'print', 'repr', 'round', 'sorted', 'sum', 'bool',
		'bytearray', 'bytes', 'complex', 'dict', 'enumerate', 'filter', 'float', 'frozenset', 'property', 'int', 'list', 'map', 'object', 'range',
		'reversed', 'set', 'slice', 'str', 'tuple', 'type', 'zip']

_ast2spt_func_builtins       = dict (no for no in filter (lambda no: no [1], ((n, _builtins_dict.get (n)) for n in _ast2spt_func_builtins_names)))

class ast2spt:
	def __new__ (cls, ast):
		self    = super ().__new__ (cls)
		self.kw = {}

		spt     = self._ast2spt (ast)

		if callable (getattr (spt, 'doit', None)): # and spt.__class__ != sp.Piecewise
			try:
				spt = spt.doit ()
				spt = sp.piecewise_fold (spt) # prevent SymPy infinite piecewise recursion
			except TypeError:
				pass

		return spt

	def _ast2spt (self, ast): # abstract syntax tree -> sympy tree (expression)
		return self._ast2spt_funcs [ast.op] (self, ast)

	_ast2spt_consts = { # 'e' and 'i' dynamically set on use from AST.E or I
		'pi'   : sp.pi,
		'oo'   : sp.oo,
		'zoo'  : sp.zoo,
		'None' : None,
		'True' : sp.boolalg.true,
		'False': sp.boolalg.false,
		'nan'  : sp.nan,
	}

	def _ast2spt_var (self, ast):
		spt = {**self._ast2spt_consts, AST.E.var: sp.E, AST.I.var: sp.I}.get (ast.var, None)

		if spt is None:
			if len (ast.var) > 1 and ast.var not in {'beta', 'Lambda'}:
				spt = getattr (sp, ast.var, None)

			if spt is None:
				spt = sp.Symbol (ast.var, **self.kw)

		return spt

	def _ast2spt_attr (self, ast):
		mbr = getattr (self._ast2spt (ast.obj), ast.attr)

		return mbr if ast.args is None else _ast_func_call (mbr, ast.args)

	def _ast2spt_func (self, ast):
		if ast.func == '@': # special reference meta-function
			return self._ast2spt (ast.args [0])

		if ast.func == '%': # special stop evaluation meta-function
			self.kw ['evaluate'] = False

			return ExprDontDoIt (self._ast2spt (ast.args [0]), self._ast2spt (ast.args [1]) if len (ast.args) > 1 else sp.S.One)

		func = getattr (sp, ast.func, _ast2spt_func_builtins.get (ast.func))

		if func is None:
			raise NameError (f'function {ast.func!r} is not defined')

		return _ast_func_call (func, ast.args)

	def _ast2spt_diff (self, ast):
		args = sum ((
				(self._ast2spt (n.as_var),) \
				if n.is_var else \
				(self._ast2spt (n.base.as_var), sp.Integer (n.exp.num)) \
				for n in ast.dvs \
				), ())

		return sp.Derivative (self._ast2spt (ast [1]), *args, **self.kw)

	def _ast2spt_intg (self, ast):
		if ast.from_ is None:
			return \
					sp.Integral (1, self._ast2spt (ast.dv.as_var)) \
					if ast.intg is None else \
					sp.Integral (self._ast2spt (ast.intg), self._ast2spt (ast.dv.as_var))
		else:
			return \
					sp.Integral (1, (self._ast2spt (ast.dv.as_var), self._ast2spt (ast.from_), self._ast2spt (ast.to))) \
					if ast.intg is None else \
					sp.Integral (self._ast2spt (ast [1]), (self._ast2spt (ast.dv.as_var), self._ast2spt (ast.from_), self._ast2spt (ast.to)))

	_ast2spt_eq = {
		'=':  sp.Eq,
		'==': sp.Eq,
		'!=': sp.Ne,
		'<':  sp.Lt,
		'<=': sp.Le,
		'>':  sp.Gt,
		'>=': sp.Ge,
	}

	_ast2spt_funcs = {
		'=': lambda self, ast: self._ast2spt_eq [ast.rel] (self._ast2spt (ast.lhs), self._ast2spt (ast.rhs)),
		'#': lambda self, ast: sp.Integer (ast [1]) if ast.is_int_text (ast.num) else sp.Float (ast.num, _SYMPY_FLOAT_PRECISION),
		'@': _ast2spt_var,
		'.': _ast2spt_attr,
		'"': lambda self, ast: ast.str_,
		',': lambda self, ast: tuple (self._ast2spt (p) for p in ast.commas),
		'(': lambda self, ast: self._ast2spt (ast.paren),
		'[': lambda self, ast: [self._ast2spt (b) for b in ast.bracks],
		'|': lambda self, ast: sp.Abs (self._ast2spt (ast.abs), **self.kw),
		'-': lambda self, ast: -self._ast2spt (ast.minus),
		'!': lambda self, ast: sp.factorial (self._ast2spt (ast.fact), **self.kw),
		'+': lambda self, ast: sp.Add (*(self._ast2spt (n) for n in ast.adds), **self.kw),
		'*': lambda self, ast: sp.Mul (*(self._ast2spt (n) for n in ast.muls), **self.kw),
		'/': lambda self, ast: sp.Mul (self._ast2spt (ast.numer), sp.Pow (self._ast2spt (ast.denom), -1), **self.kw),
		'^': lambda self, ast: sp.Pow (self._ast2spt (ast.base), self._ast2spt (ast.exp), **self.kw),
		'log': lambda self, ast: sp.log (self._ast2spt (ast.log), **self.kw) if ast.base is None else sp.log (self._ast2spt (ast.log), self._ast2spt (ast.base), **self.kw),
		'sqrt': lambda self, ast: sp.Pow (self._ast2spt (ast.rad), sp.Pow (2, -1), **self.kw) if ast.idx is None else sp.Pow (self._ast2spt (ast.rad), sp.Pow (self._ast2spt (ast.idx), -1, **self.kw), **self.kw),
		'func': _ast2spt_func,
		'lim': lambda self, ast: (sp.Limit if ast.dir else sp.limit) (self._ast2spt (ast.lim), self._ast2spt (ast.lvar), self._ast2spt (ast.to), dir = ast.dir or '+-'),
		'sum': lambda self, ast: sp.Sum (self._ast2spt (ast.sum), (self._ast2spt (ast.svar), self._ast2spt (ast.from_), self._ast2spt (ast.to))),
		'diff': _ast2spt_diff,
		'intg': _ast2spt_intg,
		'vec': lambda self, ast: sp.Matrix ([[self._ast2spt (e)] for e in ast.vec], **self.kw),
		'mat': lambda self, ast: sp.Matrix ([[self._ast2spt (e) for e in row] for row in ast.mat], **self.kw),
		'piece': lambda self, ast: sp.Piecewise (*tuple ((self._ast2spt (p [0]), True if p [1] is True else self._ast2spt (p [1])) for p in ast.pieces), **self.kw),
		'lamb': lambda self, ast: sp.Lambda (tuple (self._ast2spt (v) for v in ast.vars), self._ast2spt (ast.lamb)),
	}

#...............................................................................................
def spt2ast (spt): # sympy tree (expression) -> abstract syntax tree
	for cls in spt.__class__.__mro__:
		func = _spt2ast_funcs.get (cls)

		if func:
			return func (spt)

		if cls is sp.Function:
			if len (spt.args) == 1:
				return _spt2ast_Function1 (spt)

			break

	tex = sp.latex (spt)

	if tex [0] == '<' and tex [-1] == '>': # for Python repr style of objects <class something>
		tex = '\\text{' + tex.replace ("<", "&lt;").replace (">", "&gt;").replace ("\n", "") + '}'

	return AST_Text (tex, str (spt), str (spt))

_rec_num_deconstructed = re.compile (r'^(-?)(\d*[^0.e])?(0*)(?:(\.)(0*)(\d*[^0e])?(0*))?(?:([eE])([+-]?\d+))?$') # -101000.000101000e+123 -> (-) (101) (000) (.) (000) (101) (000) (e) (+123)

def _spt2ast_num (spt):
	m = _rec_num_deconstructed.match (str (spt))
	g = [g or '' for g in m.groups ()]

	if g [5]:
		return AST ('#', ''.join (g [:6] + g [7:]))

	e = len (g [2]) + (int (g [8]) if g [8] else 0)

	return AST ('#', \
			f'{g [0]}{g [1]}e+{e}'     if e >= 16 else \
			f'{g [0]}{g [1]}{"0" * e}' if e >= 0 else \
			f'{g [0]}{g [1]}e{e}')

def _spt2ast_MatrixBase (spt):
	return \
			AST ('mat', tuple (tuple (spt2ast (e) for e in spt [row, :]) for row in range (spt.rows))) \
			if spt.cols > 1 else \
			AST ('vec', tuple (spt2ast (e) for e in spt)) \
			if spt.rows > 1 else \
 			spt2ast (spt [0])

def _spt2ast_Add (spt):
	args = spt._sorted_args

	for arg in args:
		if isinstance (arg, sp.Order):
			break
	else:
		args = args [::-1]

	return AST ('+', tuple (spt2ast (arg) for arg in args))

def _spt2ast_Mul (spt):
	if spt.args [0] == -1:
		return AST ('-', spt2ast (sp.Mul (*spt.args [1:])))

	if spt.args [0].is_negative and isinstance (spt, sp.Number):
		return AST ('-', spt2ast (sp.Mul (-spt.args [0], *spt.args [1:])))

	numer = []
	denom = []

	for arg in spt.args:
		if isinstance (arg, sp.Pow) and arg.args [1].is_negative:
			denom.append (spt2ast (sp.Pow (arg.args [0], -arg.args [1])))
		else:
			numer.append (spt2ast (arg))

	if not denom:
		return AST ('*', tuple (numer)) if len (numer) > 1 else numer [0]

	if not numer:
		return AST ('/', AST.One, AST ('*', tuple (denom)) if len (denom) > 1 else denom [0])

	return AST ('/', AST ('*', tuple (numer)) if len (numer) > 1 else numer [0], \
			AST ('*', tuple (denom)) if len (denom) > 1 else denom [0])

def _spt2ast_Pow (spt):
	if spt.args [1].is_negative:
		return AST ('/', AST.One, spt2ast (sp.Pow (spt.args [0], -spt.args [1])))

	if spt.args [1] == 0.5:
		return AST ('sqrt', spt2ast (spt.args [0]))

	return AST ('^', spt2ast (spt.args [0]), spt2ast (spt.args [1]))

def _spt2ast_MatPow (spt):
	try: # compensate for some MatPow.doit() != mat**pow
		return spt2ast (spt.args [0] ** spt.args [1])
	except:
		return AST ('^', spt2ast (spt.args [0]), spt2ast (spt.args [1]))

def _spt2ast_Function1 (spt):
	return AST ('func', spt.__class__.__name__, (spt2ast (spt.args [0]),)) # TODO: Multiple arguments?!?

def _spt2ast_Integral (spt):
	return \
			AST ('intg', spt2ast (spt.args [0]), AST ('@', f'd{spt2ast (spt.args [1] [0]) [1]}'), spt2ast (spt.args [1] [1]), spt2ast (spt.args [1] [2])) \
			if len (spt.args [1]) == 3 else \
			AST ('intg', spt2ast (spt.args [0]), AST ('@', f'd{spt2ast (spt.args [1] [0]) [1]}'))

_spt2ast_funcs = {
	ExprDontDoIt: lambda spt: AST ('func', '%', (spt2ast (spt.args [0]), spt2ast (spt.args [1]))),

	None.__class__: lambda spt: AST.None_,
	True.__class__: lambda spt: AST.True_,
	False.__class__: lambda spt: AST.False_,
	int: lambda spt: AST ('#', str (spt)),
	str: lambda spt: AST ('"', spt),
	tuple: lambda spt: AST ('(', (',', tuple (spt2ast (e) for e in spt))),
	list: lambda spt: AST ('[', tuple (spt2ast (e) for e in spt)),
	bool: lambda spt: AST.True_ if spt else AST.False_,
	sp.Tuple: lambda spt: spt2ast (spt.args),

	sp.Integer: _spt2ast_num,
	sp.Float: _spt2ast_num,
	sp.Rational: lambda spt: AST ('/', ('#', str (spt.p)), ('#', str (spt.q))) if spt.p >= 0 else AST ('-', ('/', ('#', str (-spt.p)), ('#', str (spt.q)))),
	sp.matrices.MatrixBase: _spt2ast_MatrixBase,
	sp.numbers.ImaginaryUnit: lambda ast: AST.I,
	sp.numbers.Pi: lambda spt: AST.Pi,
	sp.numbers.Exp1: lambda spt: AST.E,
	sp.numbers.Infinity: lambda spt: AST.Infty,
	sp.numbers.NegativeInfinity: lambda spt: AST ('-', AST.Infty),
	sp.numbers.ComplexInfinity: lambda spt: AST.Infty, # not exactly but whatever
	sp.numbers.NaN: lambda spt: AST.NaN,
	sp.Symbol: lambda spt: AST ('@', spt.name),

	sp.boolalg.BooleanTrue: lambda spt: AST.True_,
	sp.boolalg.BooleanFalse: lambda spt: AST.False_,
	sp.Eq: lambda spt: AST ('=', '=', spt2ast (spt.args [0]), spt2ast (spt.args [1])),
	sp.Ne: lambda spt: AST ('=', '!=', spt2ast (spt.args [0]), spt2ast (spt.args [1])),
	sp.Lt: lambda spt: AST ('=', '<', spt2ast (spt.args [0]), spt2ast (spt.args [1])),
	sp.Le: lambda spt: AST ('=', '<=', spt2ast (spt.args [0]), spt2ast (spt.args [1])),
	sp.Gt: lambda spt: AST ('=', '>', spt2ast (spt.args [0]), spt2ast (spt.args [1])),
	sp.Ge: lambda spt: AST ('=', '>=', spt2ast (spt.args [0]), spt2ast (spt.args [1])),

	sp.fancysets.Complexes: lambda spt: AST.Complexes,

	sp.Add: _spt2ast_Add,
	sp.Mul: _spt2ast_Mul,
	sp.Pow: _spt2ast_Pow,
	sp.MatPow: _spt2ast_MatPow,

	sp.Abs: lambda spt: AST ('|', spt2ast (spt.args [0])),
	sp.arg: lambda spt: AST ('func', 'arg', (spt2ast (spt.args [0]),)),
	sp.exp: lambda spt: AST ('^', AST.E, spt2ast (spt.args [0])),
	sp.factorial: lambda spt: AST ('!', spt2ast (spt.args [0])),
	sp.Function: _spt2ast_Function1,
	sp.functions.elementary.trigonometric.TrigonometricFunction: _spt2ast_Function1,
	sp.functions.elementary.hyperbolic.HyperbolicFunction: _spt2ast_Function1,
	sp.functions.elementary.trigonometric.InverseTrigonometricFunction: _spt2ast_Function1,
	sp.functions.elementary.hyperbolic.InverseHyperbolicFunction: _spt2ast_Function1,
	sp.log: lambda spt: AST ('log', spt2ast (spt.args [0])) if len (spt.args) == 1 else AST ('log', spt2ast (spt.args [0]), spt2ast (spt.args [1])),
	sp.Min: lambda spt: AST ('func', 'Min', ((spt2ast (spt.args [0]) if len (spt.args) == 1 else spt2ast (spt.args)),)),
	sp.Max: lambda spt: AST ('func', 'Max', ((spt2ast (spt.args [0]) if len (spt.args) == 1 else spt2ast (spt.args)),)),

	sp.Sum: lambda spt: AST ('sum', spt2ast (spt.args [0]), spt2ast (spt.args [1] [0]), spt2ast (spt.args [1] [1]), spt2ast (spt.args [1] [2])),
	sp.Integral: _spt2ast_Integral,

	sp.Order: lambda spt: AST ('func', 'O', ((spt2ast (spt.args [0]) if spt.args [1] [1] == 0 else spt2ast (spt.args)),)),
	sp.Piecewise: lambda spt: AST ('piece', tuple ((spt2ast (t [0]), True if isinstance (t [1], sp.boolalg.BooleanTrue) else spt2ast (t [1])) for t in spt.args)),
	sp.Lambda: lambda spt: AST ('lamb', spt2ast (spt.args [1]), tuple (spt2ast (v) for v in spt.args [0])),
}

#...............................................................................................
def set_precision (ast): # recurse through ast to set sympy float precision according to longest string of digits found
	global _SYMPY_FLOAT_PRECISION

	prec  = 15
	stack = [ast]

	while stack:
		ast = stack.pop ()

		if not isinstance (ast, AST):
			pass # nop
		elif ast.is_num:
			prec = max (prec, len (ast.num)) # will be a little more than number of digits to compensate for falling precision with some calculations
		else:
			stack.extend (ast [1:])

	_SYMPY_FLOAT_PRECISION = prec if prec > 15 else None

def set_user_funcs (user_funcs):
	global _USER_FUNCS

	_USER_FUNCS = user_funcs

class sym: # for single script
	AST_Text       = AST_Text
	set_precision  = set_precision
	set_user_funcs = set_user_funcs
	ast2tex        = ast2tex
	ast2nat        = ast2nat
	ast2py         = ast2py
	ast2spt        = ast2spt
	spt2ast        = spt2ast

# if __name__ == '__main__' and not _RUNNING_AS_SINGLE_SCRIPT: ## DEBUG!
# 	ast = AST ('+', (('@', '1'), ('@', '2')))
# 	res = ast2spt (ast)
# 	print (res)
#!/usr/bin/env python
# python 3.6+

# TODO: Working directory.
# TODO: Exception prevents restart on file date change or too much time?

import getopt
import io
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


_SYMPAD_FIRST_RUN         = os.environ.get ('SYMPAD_FIRST_RUN')
_SYMPAD_CHILD             = os.environ.get ('SYMPAD_CHILD')

_VAR_LAST = '_'

if _SYMPAD_CHILD: # sympy slow to import if not precompiled so don't do it for watcher process as is unnecessary there
	import sympy as sp

	_sys_stdout = sys.stdout
	_parser     = sparser.Parser ()
	_vars       = {_VAR_LAST: AST.Zero} # This is individual session STATE! Threading can corrupt this! It is GLOBAL to survive multiple Handlers.

_DEFAULT_ADDRESS = ('localhost', 8000)

_STATIC_FILES    = {'/style.css': 'css', '/script.js': 'javascript', '/index.html': 'html', '/help.html': 'html'}

_HELP = f"""
usage: {os.path.basename (sys.argv [0])} [--help] [--debug] [--nobrowser] [--sympyEI] [host:port]
"""

#...............................................................................................
# class ThreadingHTTPServer (ThreadingMixIn, HTTPServer):
# 	pass

class RealityRedefinitionError (NameError):	pass
class CircularReferenceError (RecursionError): pass
class AE35UnitError (Exception): pass

def _ast_remap (ast, map_):
	if not isinstance (ast, AST) or (ast.is_func and ast.func == '@'): # non-AST or stop remap
		return ast

	if ast.is_var and ast.var in map_: # variable
		ast = map_ [ast.var]

		return AST ('func', '%', (ast,)) if ast.is_lamb else _ast_remap (ast, map_)

	if ast.is_func and ast.func in map_: # user function
		lamb = map_ [ast.func]

		if lamb.is_lamb:
			if len (ast.args) != len (lamb.vars):
				raise TypeError (f"lambda function '{ast.func}()' takes {len (lamb.vars)} argument(s)")

			ast = _ast_remap (lamb.lamb, dict (zip ((v.var for v in lamb.vars), ast.args)))

	if ast.is_lamb: # do not remap lambda owned vars within lambda, they belong to the lambda
		lvars = {v.var for v in ast.vars}
		map_  = {v: a for v, a in filter (lambda va: va [0] not in lvars, map_.items ())}

		return AST (*(_ast_remap (a, map_) if a not in ast.vars else a for a in ast))

	return AST (*(_ast_remap (a, map_) for a in ast))

def _ast_prepare_ass (ast): # check and prepare for simple or tuple assignment
	vars = None

	if ast.is_ass:
		if ast.lhs.is_var: # simple assignment?
			ast, vars = ast.rhs, [ast.lhs.var]

	elif ast.is_comma: # tuple assignment? ('x, y = y, x' comes from parser as ('x', 'y = y', 'x')) so restructure
		lhss = []
		itr  = iter (ast.commas)

		for c in itr:
			if c.is_var:
				lhss.append (c.var)
			elif not c.is_ass or not c.lhs.is_var:
				break

			else:
				t    = (c.rhs,) + tuple (itr)
				ast  = t [0] if len (t) == 1 else AST (',', t)
				vars = lhss + [c.lhs.var]

	if vars:
		for var in vars: # trying to change a fundemental law of the universe?
			if AST ('@', var) in AST.CONSTS:
				raise RealityRedefinitionError ('The only thing that is constant is change - Heraclitus, except for constants, they never change - Me.')

	return _ast_remap (ast, _vars), vars

def _ast_execute_ass (ast, vars): # execute assignment if it was detected
	def _set_vars (vars):
		try: # check for circular references
			_ast_remap (AST (',', tuple (('@', v) for v in vars)), {**_vars, **vars})
		except RecursionError:
			raise CircularReferenceError ("I'm sorry, Dave. I'm afraid I can't do that.") from None

		_vars.update (vars)

	if not vars: # no assignment
		_vars [_VAR_LAST] = ast

		return [ast]

	if len (vars) == 1: # simple assignment
		_set_vars ({vars [0]: ast})

		asts = [AST ('=', '=', ('@', vars [0]), ast)]

	else: # tuple assignment
		ast  = ast.strip_paren ()
		asts = ast.commas if ast.is_comma else tuple (sym.spt2ast (a) for a in sym.ast2spt (ast))

		if len (vars) < len (asts):
			raise ValueError (f'too many values to unpack (expected {len (vars)})')
		if len (vars) > len (asts):
			raise ValueError (f'not enough values to unpack (expected {len (vars)}, got {len (asts)})')

		_set_vars (dict (zip (vars, asts)))

		asts = [AST ('=', '=', ('@', vars [i]), asts [i]) for i in range (len (vars))]

	user_funcs = {va [0] for va in filter (lambda va: va [1].is_lamb, _vars.items ())}

	sym.set_user_funcs (user_funcs)
	_parser.set_user_funcs (user_funcs)

	return asts

def _admin_vars (ast):
	if len (_vars) == 1:
		return 'No variables defined.'

	asts = []

	for v, e in sorted (_vars.items ()):
		if v != _VAR_LAST:
			asts.append (AST ('=', '=', ('@', v), e))
			# if e.is_lamb:
			# 	asts.append (AST ('=', '=', ('func', v, e.vars), e.lamb))
			# else:
			# 	asts.append (AST ('=', '=', ('@', v), e))

	return asts

def _admin_del (ast):
	arg = ast.args [0] if ast.args else AST.VarNull

	try:
		del _vars [arg.var]
	except KeyError:
		raise AE35UnitError (f'Variable {sym.ast2nat (arg)!r} is not defined, it can only be attributable to human error.')

	return f'Variable {sym.ast2nat (arg)!r} deleted.'

def _admin_delall (ast):
	last_var = _vars [_VAR_LAST]
	_vars.clear ()
	_vars [_VAR_LAST] = last_var

	return 'All variables deleted.'

def _admin_sympyEI (ast):
	sast.sympyEI (bool (sym.ast2spt (ast.args [0])) if ast.args else True)

	return f'Constant representation set to {AST.E.var!r} and {AST.I.var!r}.'

#...............................................................................................
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
		request = parse_qs (self.rfile.read (int (self.headers ['Content-Length'])).decode ('utf8'), keep_blank_values = True)

		for key, val in list (request.items ()):
			if isinstance (val, list) and len (val) == 1:
				request [key] = val [0]

		print (request, file = sys.stderr)

		if request ['mode'] == 'validate':
			response = self.validate (request)
		else: # request ['mode'] == 'evaluate':
			response = self.evaluate (request)

		response ['mode'] = request ['mode']
		response ['idx']  = request ['idx']
		response ['text'] = request ['text']

		self.send_response (200)
		self.send_header ("Content-type", "application/json")
		self.end_headers ()
		self.wfile.write (json.dumps (response).encode ('utf8'))
		# self.wfile.write (json.dumps ({**request, **response}).encode ('utf8'))

	def validate (self, request):
		ast, erridx, autocomplete = _parser.parse (request ['text'])
		tex = nat = py            = None

		if ast is not None:
			ast = _ast_remap (ast, {_VAR_LAST: _vars [_VAR_LAST]}) # just remap last evaluated _
			tex = sym.ast2tex (ast)
			nat = sym.ast2nat (ast)
			py  = sym.ast2py (ast)

			if os.environ.get ('SYMPAD_DEBUG'):
				print ('ast:', ast, file = sys.stderr)
				print ('tex:', tex, file = sys.stderr)
				print ('nat:', nat, file = sys.stderr)
				print ('py: ', py, file = sys.stderr)
				print (file = sys.stderr)

		return {
			'tex'         : tex,
			'nat'         : nat,
			'py'          : py,
			'erridx'      : erridx,
			'autocomplete': autocomplete,
		}

	def evaluate (self, request):
		sys.stdout = io.StringIO ()

		try:
			ast, _, _ = _parser.parse (request ['text'])

			if ast.is_func and ast.func in {'vars', 'del', 'delall', 'sympyEI'}: # special admin function?
				asts = globals () [f'_admin_{ast.func}'] (ast)

				if isinstance (asts, str):
					return {'msg': [asts]}

			else: # not admin function, normal evaluation
				ast, vars = _ast_prepare_ass (ast)

				sym.set_precision (ast)

				spt = sym.ast2spt (ast)
				ast = sym.spt2ast (spt)

				if os.environ.get ('SYMPAD_DEBUG'):
					print ('spt:        ', repr (spt), file = sys.stderr)
					print ('spt type:   ', type (spt), file = sys.stderr)
					print ('sympy latex:', sp.latex (spt), file = sys.stderr)
					print ('ast:        ', ast, file = sys.stderr)
					print (file = sys.stderr)

				asts = _ast_execute_ass (ast, vars)

			response = {}

			if asts and asts [0] is not AST.None_:
				response.update ({'math': [{
					'tex': sym.ast2tex (ast),
					'nat': sym.ast2nat (ast),
					'py' : sym.ast2py (ast),
				} for ast in asts]})

			if sys.stdout.tell ():
				sys.stdout.seek (0)

				response ['msg'] = sys.stdout.read ().strip ().split ('\n')

			return response

		except Exception:
			return {'err': ''.join (traceback.format_exception (*sys.exc_info ())).strip ().split ('\n')}

		finally:
			sys.stdout = _sys_stdout

#...............................................................................................
_month_name = (None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

if __name__ == '__main__':
	try:
		opts, argv = getopt.getopt (sys.argv [1:], '', ['help', 'nobrowser', 'debug', 'sympyEI'])

		if ('--help', '') in opts:
			print (_HELP.strip ())
			sys.exit (0)

		if ('--debug', '') in opts:
			os.environ ['SYMPAD_DEBUG'] = '1'

		if not _SYMPAD_CHILD:
			args      = [sys.executable] + sys.argv
			first_run = '1'

			while 1:
				ret       = subprocess.run (args, env = {**os.environ, 'SYMPAD_CHILD': '1', 'SYMPAD_FIRST_RUN': first_run})
				first_run = ''

				if ret.returncode != 0 and not os.environ.get ('SYMPAD_DEBUG'):
					sys.exit (0)

		if ('--sympyEI', '') in opts:
			sast.sympyEI ()

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

		if _SYMPAD_FIRST_RUN:
			print ('Sympad server running. If a browser window does not automatically open to the address below then try navigating to that URL manually.\n')

		log_message (f'Serving at http://{httpd.server_address [0]}:{httpd.server_address [1]}/')

		if os.environ.get ('SYMPAD_FIRST_RUN') and ('--nobrowser', '') not in opts:
			webbrowser.open (f'http://{httpd.server_address [0] if httpd.server_address [0] != "0.0.0.0" else "127.0.0.1"}:{httpd.server_address [1]}/index.html')

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
