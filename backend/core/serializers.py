from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        # Password write_only (tidak dikirim balik saat GET demi keamanan)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # create_user otomatis meng-hash password
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        # Update biasa untuk username/email
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        
        # Logic update password (jika dikirim)
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance