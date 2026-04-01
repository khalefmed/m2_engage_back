from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 
            'last_name', 'role', 'phone_number', 
            'is_mfa_enabled', 'is_active', 'password'
        ]
        read_only_fields = ['is_mfa_enabled']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Vérification standard (user/pass)
        data = super().validate(attrs)
        
        user = self.user
        
        # Si le MFA n'est pas encore configuré
        if not user.is_mfa_enabled:
            print("MFA non configuré pour l'utilisateur:", user.username)
            return {
                "mfa_setup_required": True,
                "access": data['access'], # On donne le token mais il est limité
                "user_id": user.id,
                "message": "Token temporaire fourni. Veuillez configurer le MFA via /mfa/setup/."
            }
        
        # Si le MFA est activé, on NE DONNE PAS de token ici.
        # On attend la validation OTP.
        return {
            "mfa_required": True,
            "user_id": user.id,
            "message": "Veuillez fournir votre code OTP."
        }



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("L'ancien mot de passe est incorrect.")
        return value