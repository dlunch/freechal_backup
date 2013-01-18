from lxml import html, etree
from lxml.cssselect import CSSSelector
import urllib2
import urllib
import cookielib
import codecs
from config import freechal_id, freechal_password, freechal_board_url, article_filename, comment_filename

def download(opener, url, data = None):
    req = urllib2.Request(url)
    if data:
        req.add_data(urllib.urlencode(data))
    urlfile = opener.open(req)

    totalData = ''
    while True:
        data = urlfile.read(1048576)
        if not data:
            break
        totalData += data
    return totalData.replace('\r\n','\n')

def parseList(url):
    page = 1
    while True:
        bbs_data = download(opener, url + '&PageNo=' + str(page))

        result = html.fromstring(bbs_data.decode('cp949'))
        items = result.cssselect('tr')
        if len(items) == 0:
            break
        for item in items:
            link = item.cssselect('td.td_title a')[0].get('href').strip()
            link = 'http://bbs.freechal.com/ComService/Activity/ABBS/' + link
            parseArticle(link)

        page = page + 1 

def parseArticle(url):
    bbs_data = download(opener, url)
    result = html.fromstring(bbs_data.decode('cp949'))

    num = result.cssselect('td.td_num')[0].text_content().strip()

    if len(result.cssselect('td.td_title img')) > 0:
        result.cssselect('td.td_title img')[0].drop_tag()
    title = result.cssselect('td.td_title')[0].text_content().strip()

    writer = result.cssselect('td.td_writer')[0].text_content().strip()

    date = result.cssselect('td.td_date')[0].text_content().strip()

    content = result.cssselect('#DocContent')[0]
    content = etree.tostring(content, encoding=unicode).strip()

    articlefile.write('%s,"%s","%s","%s","%s"\n' % (num, title.replace('"','\"'), writer.replace('"','\"'), date, content.replace('"','\"')))
    print num 

    comments = result.cssselect('.CommentList tr')
    for comment in comments:
        comment_writer = comment.cssselect('td.nicname')[0].text_content().strip()
        comment_date = comment.cssselect('span.day')[0].text_content().strip()
        comment_node = comment.cssselect('td.cmtxt')[0]
        map(lambda x:x.drop_tree(), comment_node.cssselect('span, a'))
        comment_content = comment_node.text_content().strip()

        commentfile.write('%s,"%s","%s","%s"\n' % (num, comment_writer.replace('"','\"'), comment_date, comment_content.replace('"','\"')))


cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

download(opener, 'http://ses.freechal.com/default.asp') #Get login session
download(opener, 'http://ses.freechal.com/signin/verify.asp', {'Password':freechal_password, 'Secret':'false', 'UserID':freechal_id, 'ViewHompy':'false', 'loginLevel':1});   

with codecs.open(article_filename, mode='w', encoding='utf-8') as articlefile, codecs.open(comment_filename, mode='w', encoding='utf-8') as commentfile:
    parseList(freechal_board_url)


