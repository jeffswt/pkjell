
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

""" Diffs two lists / sets. Returns a - b. """
def diff(a, b):
    if not hasattr(a, '__iter__') or type(a) == str: a = [a,]
    if not hasattr(b, '__iter__') or type(b) == str: b = [b,]
    a_ = set(a); b_ = set(b);
    c_ = set();
    for i in a_:
        if i not in b_: c_.add(i)
    c = sorted(list(c_))
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
def lsdir(path, strip_source=True):
    n_path = clean_path(get_native_path(path))
    strip_path = n_path[len(clean_path(path)):]
    a = []
    for i, j, k in os.walk(n_path):
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
    def load(self):
        try:
            f = open_file('/data/index.json', 'r', encoding='utf-8')
            s = f.read()
            f.close()
        except:
            s = self.create()
        d = json.loads(s)
        return d
    """ Dumps JSON index data to file. """
    def save(self, data):
        s = json.dumps(indent=4)
        f = open_file('/data/index.json', 'w', encoding='utf-8')
        f.write(s)
        f.close()
        return
    """ Create JSON data, initially. """
    def create(self):
        d = {
            'indexes': {
                'index': {
                    'location': '/index.html',
                    'hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                },
                'archive': {
                    'location': '/archive.html',
                    'hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                },
                'categories': {
                    'location': '/categories.html',
                    'hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                },
                'tags': {
                    'location': '/tags.html',
                    'hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                },
                'article': {
                    'location': '/article.html',
                    'hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                },
            },
            'entries': [],
        }
        return d
    """ Create JSON data of an entry, initially of an empty file. """
    def create_entry(self):
        d = {
            'id': '1970-01-01_null',
            'date': '1970-01-01 00:00',
            'categories': [],
            'tags': [],
            'hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        }
        return d
    pass

""" Main function. """
def main():
    # j_data = jindex.load()
    # Reading templates (on-disk)
    temp_src = diff(
        sub_every(lsdir('/assets/templates'), r'^/assets/templates/(.*)\..*?$', r'\1'),
    'frame')
    # Creating file
    for name in temp_src:
        write_file('/%s.html' % name, render_page(
            read_file('/assets/templates/frame.html'),
            data = {
                'content': read_file('/assets/templates/%s.html' % name),
                'script': read_file('/assets/templates/%s.js' % name),
            }))
        pass
    # jindex.save(j_data)
    return 0

if __name__ == '__main__':
    ret_code = main()
    exit(ret_code)
