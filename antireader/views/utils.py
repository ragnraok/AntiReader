from flask import jsonify, make_response

def generate_article_link(site_id, article_id):
    return "/siteview/%d/%d/" % (site_id, article_id)

def unauthorize_response():
    return make_response(response="", status=401)

def response_html(html):
    return make_response(response=html)

def ajax_response(success, data={}, errorcode=0):
    if success:
        return jsonify(success=True, data=data)
    else:
        return jsonify(success=False, errorcode=errorcode)
