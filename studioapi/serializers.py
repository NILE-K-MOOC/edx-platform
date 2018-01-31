from rest_framework import serializers

class UpdateCourseSerializer(serializers.Serializer):

    display_name = serializers.CharField()
    id = serializers.CharField()
    start_date = serializers.CharField()
    end_date = serializers.CharField()
    enrollment_start = serializers.CharField()
    enrollment_end = serializers.CharField()
    image_dir = serializers.CharField()
    short_description = serializers.CharField()
    #description =  serializers.CharField()
    overview = serializers.CharField()
    email_admin = serializers.CharField()
    email_staff = serializers.CharField()

class CreateUserSerializer(serializers.Serializer):

    email = serializers.CharField()
    full_name = serializers.CharField()
    public_username = serializers.CharField()
    password = serializers.CharField()
    location = serializers.CharField()
    language = serializers.CharField()

class CreateCourseSerializer(serializers.Serializer):

    display_name = serializers.CharField()
    org = serializers.CharField()
    number = serializers.CharField()
    run = serializers.CharField()
    has_org = serializers.CharField()
    has_number = serializers.CharField()
    has_run  = serializers.CharField()

class EnrollUserSerializer(serializers.Serializer):

    email = serializers.CharField()
    course_key = serializers.CharField()

class RerunCourseSerializer(serializers.Serializer):

    id = serializers.CharField()
    display_name = serializers.CharField()
    org = serializers.CharField()
    number = serializers.CharField()
    run = serializers.CharField()

class ManageUserSerializer(serializers.Serializer):

    id = serializers.CharField()
    email = serializers.CharField()
