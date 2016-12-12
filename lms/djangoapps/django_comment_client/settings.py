from django.conf import settings

MAX_COMMENT_DEPTH = None
MAX_UPLOAD_FILE_SIZE = 1024 * 1024 * 5   # result in bytes # modify 5Mb
# add ext
ALLOWED_UPLOAD_FILE_TYPES = ('.jpg', '.jpeg', '.gif', '.bmp', '.png', '.tiff', '.pdf', '.hwp', '.ppt', '.pptx', '.doc', '.docx', '.xls', '.xlsx')

if hasattr(settings, 'DISCUSSION_SETTINGS'):
    MAX_COMMENT_DEPTH = settings.DISCUSSION_SETTINGS.get('MAX_COMMENT_DEPTH')
    MAX_UPLOAD_FILE_SIZE = settings.DISCUSSION_SETTINGS.get('MAX_UPLOAD_FILE_SIZE') or MAX_UPLOAD_FILE_SIZE
    ALLOWED_UPLOAD_FILE_TYPES = settings.DISCUSSION_SETTINGS.get('ALLOWED_UPLOAD_FILE_TYPES') or ALLOWED_UPLOAD_FILE_TYPES
