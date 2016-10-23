
import binascii
import hashlib
import json
import mako
import mako.template
import os
import pandoc
import re

""" consq_sub -- Consecutively substitute patterns in RegEx. """
def consq_sub(s, *args):
    if len(args) % 2 != 0:
        raise AttributeError('Odd arguments given')
    for i in range(0, len(args), 2):
        s = re.sub(args[i], args[i + 1], s)
    return s

""" sub_every -- Substitute every string """
def sub_every(l, pattern, sub):
    nl = []
    for s in l:
        nl.append(re.sub(pattern, sub, s))
    return nl

""" select_match -- Select all which matches the string """
def select_match(l, pattern):
    nl = []
    for s in l:
        if re.findall(pattern, s):
            nl.append(s)
    nl.sort()
    return nl

""" Diffs two lists / sets. Returns a - b. """
def diff(a, b, ordered=False):
    if not hasattr(a, '__iter__') or type(a) == str: a = [a,]
    if not hasattr(b, '__iter__') or type(b) == str: b = [b,]
    if not ordered:
        a_ = set(a); b_ = set(b);
        c_ = set();
        for i in a_:
            if i not in b_: c_.add(i)
        c = sorted(list(c_))
    else:
        a_ = list(a); b_ = list(b);
        c_ = list();
        for i in a_:
            if i not in b_: c_.append(i)
        c = c_
    return c

""" Mako renderer """
def render_page(html_data, **additional_arguments):
    if type(html_data) == bytes:
        html_data = html_data.decode('utf-8', 'ignore')
    html_data = mako.template.Template(
        text=html_data,
        input_encoding='utf-8',
        output_encoding='utf-8').render(
            **additional_arguments if additional_arguments else dict()
        ).decode('utf-8', 'ignore')
    return html_data

""" SHA256 invoker """
def get_hash(data):
    return binascii.hexlify(hashlib.sha256(data.encode('utf-8', 'ignore')).digest()).decode('utf-8', 'ignore')

""" Parse time """
def parse_time(s):
    a = s.split(' ')
    b = a[0].split('-')
    c = a[1].split(':')
    r = {'year':int(b[0]), 'month':int(b[1]), 'day':int(b[2]), 'hour':int(c[0]), 'minute':int(c[1]), 'second':int(c[2])}
    return r

""" Format time to given style. """
def fmt_time(o, t):
    if type(o) == str:
        o = parse_time(o)
    if t == 'British':
        return '%d %s %d' % (o['day'], ['', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'][o['month']], o['year'])
    elif t == 'Identifier':
        return '%s-%s-%s' % (str(o['year']).ljust(2, '0'), str(o['month']).ljust(2, '0'), str(o['day']).ljust(2, '0'))
    return '%s-%s-%s %s:%s:%s' % (str(o['year']).ljust(2, '0'), str(o['month']).ljust(2, '0'), str(o['day']).ljust(2, '0'), str(o['hour']).ljust(2, '0'), str(o['minute']).ljust(2, '0'), str(o['second']).ljust(2, '0'))

""" clean_path -- Make path comfortable under POSIX. """
def clean_path(path):
    path = consq_sub(path,
        '\\\\', '/',
        '\\./', '/',
        '[/]+', '/',
        '\\./', '../',)
    return path

""" get_native_path -- Retrieve actual path of this file. """
def get_native_path(path):
    return '../' + path

""" Opens file, relative to source folder. """
def open_file(file_name, *args, **kwargs):
    return open(get_native_path(file_name), *args, **kwargs)

""" Reads file content, relative to source folder. """
def read_file(file_name):
    try:
        f = open_file(file_name, 'r', encoding='utf-8')
        s = f.read()
        f.close()
    except:
        s = ''
    return s

""" Writes file content, relative to source folder. """
def write_file(file_name, data):
    f = open_file(file_name, 'w', encoding='utf-8')
    f.write(data)
    f.close()
    return

""" lsdir(path) -- Lists all files under current directory. """
def lsdir(path, nowalk=False, strip_source=True):
    n_path = clean_path(get_native_path(path))
    strip_path = n_path[len(clean_path(path)):]
    a = []
    for i, j, k in os.walk(n_path):
        if nowalk and i != n_path:
            continue
        for p in k:
            p = os.path.join(i, p)
            p = clean_path(p)
            if strip_source:
                p = p[len(strip_path):]
            a.append(p)
    a.sort()
    return a

class jindex:
    """ Loads JSON index data from file. """
    @classmethod
    def load(self):
        try:
            f = open_file('/data/index.json', 'r', encoding='utf-8')
            s = f.read()
            d = json.loads(s)
            f.close()
        except:
            d = self.create()
        return d
    """ Dumps JSON index data to file. """
    @classmethod
    def save(self, data):
        s = json.dumps(data, indent=4, sort_keys=True)
        f = open_file('/data/index.json', 'w', encoding='utf-8')
        f.write(s)
        f.close()
        return
    """ Create JSON data, initially. """
    @classmethod
    def create(self):
        d = {
            'indexes': {
                'index': {
                    'location': '/index.html',
                    'hash': get_hash(''),
                },
                'archive': {
                    'location': '/archive.html',
                    'hash': get_hash(''),
                },
                'categories': {
                    'location': '/categories.html',
                    'hash': get_hash(''),
                },
                'tags': {
                    'location': '/tags.html',
                    'hash': get_hash(''),
                },
                'article': {
                    'location': '/article.html',
                    'hash': get_hash(''),
                },
            },
            'entries': [],
        }
        return d
    """ Create JSON data of an entry, initially of an empty file. """
    @classmethod
    def create_entry(self):
        d = {
            'id': '1970-01-01-null',
            'date': '1970-01-01 00:00:00',
            'categories': [],
            'tags': [],
            'hash': get_hash(''),
            'hash-src': get_hash(''),
        }
        return d
    pass

""" Main function. """
def main():
    # Getting JSON data
    j_data = jindex.load()
    # Reading templates (on-disk)
    temp_src = diff(
        sub_every(lsdir('/assets/templates'), r'^/assets/templates/(.*)\..*?$', r'\1'),
    ['frame', 'post', 'brief'])
    # Compiling index templates
    j_data = dict()
    for name in temp_src:
        temp_data = render_page(
            read_file('/assets/templates/frame.html'),
            data = {
                'content': read_file('/assets/templates/%s.html' % name),
                'script': read_file('/assets/templates/%s.js' % name),
            })
        j_data[name] = {
            'location': './%s.html' % name,
            'hash': get_hash(temp_data),
        }
        write_file('/%s.html' % name, temp_data)
        pass
    # Resolving new articles
    temp_src = select_match(
        sub_every(lsdir('/posts/', nowalk=True), r'^/posts/(.*)$', r'\1'),
    r'\.md$')
    # Compiling articles
    for fname in temp_src:
        # Parsing lines
        fdata = read_file('/posts/%s' % fname)
        flines = fdata.split('\n')
        # Retrieving headers
        header = []
        for i in flines:
            if i == '---' and '---' in header:
                header.append(i)
                break
            header.append(i)
        # Splitting body
        body = fdata[len('\n'.join(header)):]
        # Parsing headers
        header = diff(header, '---', ordered=True)
        headers = dict()
        for i in header:
            a = re.sub(r'^(.*?):.*$', r'\1', i)
            b = re.sub(r'^.*?:[ ]*(.*)$', r'\1', i)
            headers[a] = b
        for i in ['categories', 'tags']: # Some array-typed
            if i not in headers:
                headers[i] = []
            a = headers[i]
            b = a.split(',') if ',' in a else [a,]
            c = list(re.sub(r'^[ ]*(.*?)[ ]*$', r'\1', j) for j in b)
            headers[i] = c
        if 'date' not in headers or not re.findall(r'^\d+-\d+-\d+ \d+:\d+:\d+$', headers['date']):
            headers['date'] = '1970-01-01 00:00:00'
        if 'title' not in headers:
            headers['title'] = 'Untitled'
        # Resolved headers, Building template.
        brief = body.split('<!-- More -->')[0]
        rend_data = {
            'title': headers['title'],
            'title-id': re.sub(r'^[0-9\-]*(.*?)\.md$', r'\1', fname),
            'date': headers['date'],
            'date-id': fmt_time(headers['date'], 'Identifier'),
            'date-str': fmt_time(headers['date'], 'British'),
            'categories': headers['categories'],
            'tags': headers['tags'],
            'content-body': pandoc.convert('markdown', 'html', body),
            'content-brief': pandoc.convert('markdown', 'html', body.split('<!-- More -->')[0]),
        }
        body_html = render_page(read_file('/assets/templates/post.html'), data=rend_data)
        brief_html = render_page(read_file('/assets/templates/brief.html'), data=rend_data)
        print(body_html, '\n\n\n\n\n', brief_html)
        pass
    # Saving JSON data.
    jindex.save(j_data)
    return 0

if __name__ == '__main__':
    ret_code = main()
    exit(ret_code)
