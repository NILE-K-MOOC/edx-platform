from rest_framework import serializers

class DeleteCourseSerializer(serializers.Serializer):

    id = serializers.CharField()


class ProgressUserSerializer(serializers.Serializer):

    id = serializers.CharField()
    email = serializers.CharField()

class CourseEnrollSerializer(serializers.Serializer):

    id = serializers.CharField()
    email = serializers.CharField()
    action = serializers.CharField()
