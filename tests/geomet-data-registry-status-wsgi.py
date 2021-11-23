###############################################################################
#
# Copyright (C) 2021 Philippe Théroux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import sys


def _get_status_page(environ):
    fn = environ['GDR_LOGGING_LOGFILE']

    is_error = False

    try:
        with open(fn, encoding='utf-8') as fh:
            content = fh.readlines()
            content = [x.strip() for x in content]
            text = ''
            launch_time = ''
            status = '200 OK'
            append_next_line = False
            for x in content:
                if append_next_line:
                    text += '{}<br/>'.format(x)
                    append_next_line = False
                if 'Launch time :' in x:
                    launch_time += '{}<br/>'.format(x)
                if 'ERROR' in x:
                    text += '{}<br/>'.format(x)
                    is_error = True
                    if x.endswith(':'):
                        append_next_line = True
    except IOError as err:
        status = '500 Internal Server Error'
        text = err

    if is_error:
        status = '500 Internal Server Error'

    output = '''<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>GeoMet Nightly Data Registry Tests</title>
    </head>
    <body>
        <h1>GeoMet Data Registry Tests</h1>
        <p>{}</p>
    </body>
</html>'''.format(text)

    return status, output.encode('utf-8')


def application(environ, start_response):

    status, output = _get_status_page(environ)

    response_headers = [('Content-type', 'text/html'),
                        ('Content-Length', str(len(output)))]

    start_response(status, response_headers)

    return [output]


if __name__ == '__main__':  # run inline using WSGI reference implementation
    from wsgiref.simple_server import make_server
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    httpd = make_server('', port, application)
    print('Serving on port {}...'.format(port))
    httpd.serve_forever()
