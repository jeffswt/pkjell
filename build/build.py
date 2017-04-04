
import binascii
import hashlib
import json
import mako
import mako.template
import os
import pandoc
import PIL.Image
import re
import sys
import time

ignore_old_articles = False
old_articles_timestamp = '2017-01-01'

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

""" Console logger """
last_log_string = ''
def log(s, *args):
    global last_log_string
    t = last_log_string
    print('\r' * len(t) + ' ' * len(t) + '\r' * (len(t) + 1), end='')
    s = s % tuple(args)
    if s[:4] in {'... ', '!!! '}:
        print(s, end='\n')
        last_log_string = ''
    else:
        print(s, end='')
        last_log_string = s
    sys.stdout.flush()
    return

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
        return '%s-%s-%s' % (str(o['year']).rjust(2, '0'), str(o['month']).rjust(2, '0'), str(o['day']).rjust(2, '0'))
    elif t == 'Array':
        return [str(o['year']).rjust(4, '0'), str(o['month']).rjust(2, '0'), str(o['day']).rjust(2, '0'), str(o['hour']).rjust(2, '0'), str(o['minute']).rjust(2, '0'), str(o['second']).rjust(2, '0')]
    elif t == 'EasySplit':
        return '%s-%s-%s-%s-%s-%s' % tuple(fmt_time(o, 'Array'))
    elif t == 'Standard':
        return '%s-%s-%s %s:%s:%s' % tuple(fmt_time(o, 'Array'))
    return fmt_time(o, 'Standard')

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
    return open(clean_path(get_native_path(file_name)), *args, **kwargs)

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

def make_dirs(path):
    path = clean_path(get_native_path(path))
    if os.path.exists(path):
        return True
    return os.makedirs(path)

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
                    'hash': get_hash(''),
                },
                'archive': {
                    'hash': get_hash(''),
                },
                'categories': {
                    'hash': get_hash(''),
                },
                'tags': {
                    'hash': get_hash(''),
                },
                'article': {
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
            'id': 'null',
            'title': 'NULL',
            'date': '1970-01-01-00-00-00',
            'date-id': '1970-01-01',
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
    log('==> Loading site JSON database...')
    j_data = jindex.load()
    log(' .. Procedure complete.')
    # Reading templates (on-disk)
    temp_src = diff(
        sub_every(lsdir('/assets/templates'), r'^/assets/templates/(.*)\..*?$', r'\1'),
    ['frame', 'post', 'brief'])
    # Compiling index templates
    log('==> Building site templates...')
    j_data['indexes'] = dict()
    for name in temp_src:
        temp_data = render_page(
            read_file('/assets/templates/frame.html'),
            data = {
                'content': read_file('/assets/templates/%s.html' % name),
                'script': read_file('/assets/templates/%s.js' % name),
            })
        j_data['indexes'][name] = {
            'hash': get_hash(temp_data),
        }
        if name != 'index':
            make_dirs('/%s/' % name)
            path = '/%s/index.html' % name
        else:
            path = '/index.html'
        write_file(path, temp_data)
        j_data['indexes'][name]['hash'] = get_hash(read_file(path))
        log(' .. Built template "%s".', name)
    log(' .. Procedure complete.')
    # Resolving new articles
    temp_src = select_match(
        sub_every(lsdir('/posts/', nowalk=True), r'^/posts/(.*)$', r'\1'),
    r'\.md$')
    # Retrieving index of ids
    article_idx = dict()
    for i in range(0, len(j_data['entries'])):
        obj = j_data['entries'][i]
        article_idx['%s-%s' % (obj['date-id'], obj['id'])] = i
    # Compiling articles
    for fname in temp_src:
        log('==> Compiling source of post "%s".', fname)
        # Enforcing newest posts
        if fname < old_articles_timestamp and ignore_old_articles:
            log(' .. The article is too old, skipping.')
            continue
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
                continue
            a = re.sub(r'\[(.*?)\]', r'\1', headers[i])
            b = a.split(',') if ',' in a else [a,]
            while '' in b:
                b.remove('')
            c = list(re.sub(r'^[ ]*(.*?)[ ]*$', r'\1', j) for j in b)
            headers[i] = c
        # Overriding invalid header entries
        if 'date' not in headers or not re.findall(r'^\d+-\d+-\d+ \d+:\d+:\d+$', headers['date']):
            headers['date'] = '1970-01-01 00:00:00'
        headers['date'] = parse_time(headers['date'])
        if 'title' not in headers:
            headers['title'] = 'Untitled'
        # Checking if this post exists in database
        title_id = re.sub(r'^[0-9\-]*(.*?)\.md$', r'\1', fname)
        doc_id = '%s-%s' % (fmt_time(headers['date'], 'Identifier'), title_id)
        src_hash = get_hash(fdata)
        if doc_id in article_idx:
            obj_id = article_idx[doc_id]
            obj = j_data['entries'][obj_id]
            if src_hash == obj['hash-src']:
                if get_hash(read_file('/data/%s-post.html' % doc_id)) == obj['hash']:
                    log(' .. Skipping document.')
                    continue
                else:
                    log('... Detected HTML output change on document.')
            else:
                log('... Detected source change on document.')
            pass
        # Defining link convertion utilities
        def link_convert(inp):
            out = []
            for line in inp.split('\n'):
                discv = re.findall(r'!\[.*?\]\(\./\d{4}-\d{2}/.*?\)', line)
                if not discv:
                    out.append(line)
                    continue
                # Found links in this line. Determining whether to...
                for pict_path in discv:
                    new_ret = pict_path # To be replaced in original document
                    p_path = re.sub(r'^!\[.*?\]\(\./(\d{4}-\d{2}/.*?)\)$', r'\1', pict_path).split('/')
                    ext = (os.path.splitext(p_path[1])[1].lower())[1:]
                    # If it is an image, then convert image
                    if ext in {'png', 'bmp', 'tiff', 'tif', 'jpeg', 'jpg', 'gif'}:
                        try:
                            f_handle = PIL.Image.open(get_native_path('/posts/%s/%s' % (p_path[0], p_path[1])), 'r')
                            img_out = '/data/%s-%s.jpeg' % (doc_id, os.path.splitext(p_path[1])[0])
                            log('... * Exporting image "%s"...', p_path[1])
                            f_handle.save(get_native_path(img_out), format='jpeg', quality=45, progressive=True)
                        except Exception:
                            log('!!! Error exporting image "%s".', p_path[1])
                        new_ret = re.sub(r'^!\[(.*?)\]\(.*\)$', r'![\1](%s)' % img_out, new_ret)
                    # If it is text, then embed it.
                    elif ext in {'txt', 'log', 'c', 'cpp', 'h', 'hpp', 'py', 'pyw'}:
                        f_data = read_file('/posts/%s/%s' % (p_path[0], p_path[1]))
                        if ext in {'c', 'cpp', 'h', 'hpp'}: f_type = 'C++'
                        elif ext in {'py', 'pyw'}: f_type = 'Python'
                        else: f_type = ''
                        log('... * Embedding plain text "%s"...', p_path[1])
                        new_ret = '\n```%s\n%s\n\n```\n' % (f_type, f_data)
                    # If it is otherwise, copy it.
                    else:
                        f_handle = open_file('/posts/%s/%s' % (p_path[0], p_path[1]), 'rb')
                        f_data = f_handle.read()
                        f_handle.close()
                        new_out = '/data/%s-%s' % (doc_id, p_path[1])
                        log('... * Copying file "%s"...', p_path[1])
                        f_handle = open_file(new_out, 'wb')
                        f_handle.write(f_data)
                        f_handle.close()
                        # new_ret = re.sub(r'^!\[(.*?)\]\(.*\)$', r'[\1](%s)' % new_out, new_ret)
                        new_ret = re.sub(r'^!\[(.*?)\]\(.*\)$', r'<a href="%s" download="%s">\1</a>' % (new_out, p_path[1]), new_ret)
                    # Restoring string in line
                    line = new_ret.join(line.split(pict_path))
                out.append(line)
            return '\n'.join(out)
        brief = body.split('<!-- More -->')[0]
        body = link_convert(body)
        brief = link_convert(brief)
        body_content = pandoc.convert(body)
        brief_content = pandoc.convert(brief)
        # Resolved headers, Building template.
        rend_data = {
            'title': headers['title'],
            'title-id': title_id,
            'date': headers['date'],
            'date-id': fmt_time(headers['date'], 'Identifier'),
            'date-str': fmt_time(headers['date'], 'British'),
            'categories': headers['categories'],
            'tags': headers['tags'],
            'content-body': body_content,
            'content-brief': brief_content,
        }
        # Error handling, rendering page
        if len(rend_data['content-body']) <= 0:
            log('!!! Markdown compiler might have encountered problems.')
        try:
            body_html = render_page(read_file('/assets/templates/post.html'), data=rend_data)
            brief_html = render_page(read_file('/assets/templates/brief.html'), data=rend_data)
            def drop_chars(a, b):
                c = ''
                for i in a:
                    if i not in b:
                        c += i
                return c
            body_html = drop_chars(body_html, '\r')
            brief_html = drop_chars(brief_html, '\r')
        except Exception as e:
            raise e
            log('!!! Template convertion in "mako" had encountered problems.')
            continue
        # Writing files
        write_file('/data/%s-post.html' % doc_id, body_html)
        write_file('/data/%s-brief.html' % doc_id, brief_html)
        # Making JSON entry
        jentry = jindex.create_entry()
        jentry['id'] = title_id
        jentry['title'] = headers['title']
        jentry['date'] = fmt_time(headers['date'], 'EasySplit')
        jentry['date-id'] = fmt_time(headers['date'], 'Identifier')
        jentry['categories'] = headers['categories']
        jentry['tags'] = headers['tags']
        jentry['hash'] = get_hash(read_file('/data/%s-post.html' % doc_id))
        jentry['hash-src'] = get_hash(fdata)
        # Injecting JSON entry
        if doc_id in article_idx:
            obj_id = article_idx[doc_id]
            j_data['entries'][obj_id] = jentry
        else:
            j_data['entries'].append(jentry)
            article_idx[doc_id] = len(j_data['entries']) - 1
        log('... Compiled document "%s".', doc_id)
        pass
    # Sorting pages according to time...
    log('==> Updating database...')
    n_sort = []
    for i in range(0, len(j_data['entries'])):
        n_sort.append((j_data['entries'][i]['date'], i))
    n_sort.sort()
    n_entries = []
    for i in n_sort:
        n_entries.append(j_data['entries'][i[1]])
    j_data['entries'] = n_entries
    # Saving JSON data.
    jindex.save(j_data)
    log('... Procedure complete.')
    return 0

if __name__ == '__main__':
    t_begin = time.time()
    ret_code = main()
    t_end = time.time()
    log('==> Build finished in %.3f seconds.\n', t_end - t_begin)
    exit(ret_code)
