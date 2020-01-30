import json
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Scope, String, Float, Boolean, Dict, DateTime, Integer
from django.template import Context, Template
from webob import Response

_ = lambda text: text

class ForumXBlock(XBlock):

    display_name = String(
        display_name=_("Display Name"),
        help=_("Display name for this module"),
        default="Forum XBlock",
        scope=Scope.settings
    )

    count = Integer(
        default=0,
        help=_("A simple counter, to show something happening"),
        scope=Scope.user_state
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

    def student_view(self, context=None):
        html = self.resource_string("static/html/forumxblock.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/forumxblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/forumxblock.js"))
        frag.initialize_js('ForumXBlock')
        return frag

    @XBlock.json_handler
    def increment_count(self, data, suffix=''):
        self.count += 1
        return {"count": self.count}

    def get_context_studio(self):
        return {
            'field_display_name': self.fields['display_name'],
            'field_has_score': self.fields['has_score'],
            'forum_xblock': self
        }

    def render_template(self, template_path, context):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    def studio_view(self, context=None):
        context_html = self.get_context_studio()
        template = self.render_template('static/html/studio.html', context_html)
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/studio.css"))
        frag.add_javascript(self.resource_string("static/js/src/studio.js"))
        frag.initialize_js('ForumXBlock')
        return frag

    @XBlock.handler
    def studio_submit(self, request, suffix=''):
        self.display_name = request.params['display_name']
        self.has_score = request.params['has_score']
        return Response(json.dumps({'result': 'success'}), content_type='application/json')