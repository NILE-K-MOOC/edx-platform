import json
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Scope, String, Float, Boolean, Dict, DateTime, Integer
from django.template import Context, Template
from webob import Response
from django.conf import settings
from pymongo import MongoClient
from bson import ObjectId

_ = lambda text: text

class ForumXBlock(XBlock):

    display_name = String(
        display_name=_("Display Name"),
        help=_("Display name for this module"),
        default="Forum XBlock",
        scope=Scope.settings
    )

    write_count = Integer(
        display_name=_("Write Count"),
        default=1,
        help=_("Number of comments written"),
        scope=Scope.settings
    )

    give_point = Integer(
        display_name=_("Give Point"),
        default=100,
        help=_("Score on writing one time"),
        scope=Scope.settings
    )

    has_score = Boolean(
        default=True,
        help=_("Decide whether to give points to the learning module"),
        display_name=_("Score Activate"),
        scope=Scope.settings
    )

    def _publish_grade(self, score):
        self.runtime.publish(self, 'grade', { 'value': score, 'max_value': 1 })

    def resource_string(self, path):
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render_template(self, template_path, context):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    def student_view(self, context=None):
        context_html = {
            'write_count': self.write_count,
            'give_point': self.give_point,
        }
        template = self.render_template('static/html/forumxblock.html', context_html)
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/forumxblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/forumxblock.js"))
        frag.initialize_js('ForumXBlock')
        return frag

    @XBlock.json_handler
    def increment_count(self, request, data, suffix=''):
        user_id = self.runtime.user_id
        course_id = self.course_id

        m_password = settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('password')
        m_host = settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host')
        m_port = settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port')

        client = MongoClient(m_host, m_port)
        client.admin.authenticate('edxapp', m_password, mechanism='SCRAM-SHA-1', source='edxapp')
        db = client.cs_comments_service_development

        current_count = db.contents.find({"course_id": str(course_id), "author_id": str(user_id)}).count()
        write_count = self.write_count
        give_point = self.give_point

        print "current_count = ", current_count
        print "write_count = ", write_count
        print "give_point = ", give_point

        score = (current_count / write_count) * give_point

        print "score = ", score

        if score > 100:
            score = 100

        print "score = ", score

        raw_score = (float(score) / 100)

        print "raw_score = ", raw_score

        self._publish_grade(raw_score)

        return {"current_count": current_count}

    def studio_view(self, context=None):
        context_html = {
            'field_display_name': self.fields['display_name'],
            'field_has_score': self.fields['has_score'],
            'field_write_count': self.fields['write_count'],
            'field_give_point': self.fields['give_point'],
            'forum_xblock': self
        }
        template = self.render_template('static/html/studio.html', context_html)
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/studio.css"))
        frag.add_javascript(self.resource_string("static/js/src/studio.js"))
        frag.initialize_js('ForumXBlock')
        return frag

    @XBlock.handler
    def studio_submit(self, request, suffix=''):
        # self.has_score = request.params['has_score']
        self.display_name = request.params['display_name']

        try:
            write_count = int(request.params['write_count'])
        except BaseException:
            write_count = 1

        try:
            give_point = int(request.params['give_point'])
        except BaseException:
            give_point = 100

        if give_point > 0 and give_point <= 100:
            self.give_point = give_point
        else:
            self.give_point = 100

        self.write_count = write_count

        return Response(json.dumps({'result': 'success'}), content_type='application/json')