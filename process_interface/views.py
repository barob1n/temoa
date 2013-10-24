from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import HttpResponse, Http404
from django.shortcuts import render, render_to_response
from django.utils import simplejson as json

from settings import CD # content delivery

from forms import LoginForm

from views_analysis import *
from views_auth import *
from views_process import *

from view_helpers import set_cookie, get_messages


def home ( req ):
	return render_to_response('process_interface/home.html')


def view ( req ):
	template = 'process_interface/view.html'

	c = {'CD': CD, 'username': None}
	c.update(csrf(req))

	if req.user.is_authenticated():
		c.update( username=req.user.username )
	else:
		c.update( password_form=LoginForm() )

	res = render( req, template, c )
	set_cookie( req, res )

	return res


def test_view ( req ):
	from django.shortcuts import redirect
	print req.POST
	return redirect('http://localhost:8000/analysis/1/process_info/3,4?json')


def tutorial ( req ):
	raise Http404


def user ( req ):
	users = [ (u.username, u.get_full_name() ) for u in User.objects.all() ]

	for i, (uname, fname) in enumerate( users ):
		if not fname:
			users[ i ] = (uname, 'unknown name')
	users.sort()

	data = json.dumps( users )
	response = HttpResponse(
	  data,
	  content_type='application/json'
	)
	response['Content-Length'] = len( data )
	return response

