import json
from bs4 import BeautifulSoup
from logger.log import parser
from db.models import WeiboComment
from decorators.decorator import parse_decorator


@parse_decorator(1)
def get_html_cont(html):
    cont = ''
    data = json.loads(html, encoding='utf-8').get('data', '')
    if data:
        cont = data.get('html', '')

    return cont


def get_total_page(html):
    try:
        page_count = json.loads(html, encoding='utf-8').get('data', '').get('page', '').get('totalpage', 1)
    except Exception as e:
        parser.error('获取总也面出错，具体错误是{}'.format(e))
        page_count = 1

    return page_count


@parse_decorator(1)
def get_next_url(html):
    """
    获取下一次应该访问的url
    :param html: 
    :return: 
    """
    cont = get_html_cont(html)
    if not cont:
        return ''
    soup = BeautifulSoup(cont, 'html.parser')
    url = ''
    if 'comment_loading' in cont:
        url = soup.find(attrs={'node-type': 'comment_loading'}).get('action-data')

    if 'click_more_comment' in cont:
        url = soup.find(attrs={'action-type': 'click_more_comment'}).get('action-data')
    return url


@parse_decorator(2)
def get_comment_list(html, wb_id):
    """
    获取评论列表
    :param html: 
    :param wb_id: 
    :return: 
    """
    cont = get_html_cont(html)
    if not cont:
        return list()

    soup = BeautifulSoup(cont, 'html.parser')
    comment_list = list()
    comments = soup.find(attrs={'node-type': 'comment_list'}).find_all(attrs={'class': 'list_li S_line1 clearfix'})

    for comment in comments:
        wb_comment = WeiboComment()
        try:
            wb_comment.comment_cont = comment.find(attrs={'class': 'WB_text'}).text.strip()
            wb_comment.comment_id = comment['comment_id']
            wb_comment.user_id = comment.find(attrs={'class': 'WB_text'}).find('a').get('usercard')[3:]
            # todo 日期格式化
            wb_comment.create_time = comment.find(attrs={'class': 'WB_from S_txt2'}).text
            wb_comment.weibo_id = wb_id
        except Exception as e:
            parser.error('解析评论失败，具体信息是{}'.format(e))
        else:
            comment_list.append(wb_comment)
    return comment_list