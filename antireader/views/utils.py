from flask import jsonify, make_response

def generate_article_link(article_id):
    return "/timeline/%d" % article_id

def unauthorize_response():
    return make_response(response="", status=401)

def response_html(html):
    return make_response(response=html)
