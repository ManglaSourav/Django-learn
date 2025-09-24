from rest_framework import serializers


class TimeStampedSerializer(serializers.ModelSerializer):
    """
    Serializer mixin that includes created_at and updated_at fields.
    """

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        fields = ["created_at", "updated_at"]
