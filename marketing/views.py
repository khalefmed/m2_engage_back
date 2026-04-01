import pyotp
import qrcode
import io
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from marketing.models import User
import secrets
import string
from rest_framework import generics
from .permissions import IsAdmin 
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from django.core.mail import send_mail
from django.conf import settings

from .permissions import IsMFAIncomplete
from .serializers import ChangePasswordSerializer



class MFASetupView(APIView):
    # L'utilisateur a un token, mais il n'a pas encore activé le MFA
    permission_classes = [IsMFAIncomplete] 

    def get(self, request):
        user = request.user
        # Génération du secret TOTP
        import pyotp
        secret = pyotp.random_base32()
        user.mfa_secret = secret # On stocke temporairement le secret
        user.save()

        otp_auth_url = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email, 
            issuer_name="MarketingPlatform"
        )

        return Response({
            "secret": secret,
            "otp_auth_url": otp_auth_url,
            "message": "Scannez ce QR code ou entrez le secret manuellement."
        })



class MFAVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("otp_code")
        user = request.user

        if not user.mfa_secret:
            return Response({"error": "MFA non configuré"}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.totp.TOTP(user.mfa_secret)

        print(code)
        
        # Vérification du code (OTP)
        if totp.verify(code):
            user.is_mfa_enabled = True
            user.save()
            return Response({"message": "MFA activé avec succès !"}, status=status.HTTP_200_OK)
        
        return Response({"error": "Code invalide"}, status=status.HTTP_400_BAD_REQUEST)
    


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(
                {"detail": "Mot de passe mis à jour avec succès."}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Déconnexion réussie"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Token invalide"}, status=status.HTTP_400_BAD_REQUEST)
    

class FinalLoginVerifyOTPView(APIView):
    permission_classes = [] 

    def post(self, request):
        user_id = request.data.get("user_id")
        otp_code = request.data.get("otp_code")
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur introuvable"}, status=404)

        totp = pyotp.totp.TOTP(user.mfa_secret)
        if totp.verify(otp_code):
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user.role
            })
        
        return Response({"error": "Code OTP invalide"}, status=400)





class AdminCreateUserView(generics.CreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer # Assure-toi d'avoir un serializer pour User

    def perform_create(self, serializer):
        # Génération d'un mot de passe temporaire aléatoire
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))
        
        # L'utilisateur est créé mais inactif et doit configurer son MFA
        user = serializer.save(
            is_active=False, 
            is_mfa_enabled=False
        )
        user.set_password(temp_password)
        user.save()

        # TODO: Envoyer l'email d'invitation avec le temp_password via Celery
        print(f"DEBUG: Utilisateur {user.email} créé avec le pass: {temp_password}")




class AdminCreateUserView(generics.CreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        # Génération d'un mot de passe temporaire
        temp_password = secrets.token_urlsafe(10)
        
        user = serializer.save(
            is_active=False, 
            is_mfa_enabled=False
        )
        user.set_password(temp_password)
        user.save()

        # Envoi de l'email d'invitation
        subject = "Bienvenue sur la plateforme Marketing"
        message = f"""
        Bonjour {user.first_name},

        Un compte a été créé pour vous.
        Voici vos identifiants temporaires :
        Email : {user.email}
        Mot de passe : {temp_password}

        Veuillez vous connecter pour configurer votre authentification à deux facteurs (MFA).
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )





# Vue pour récupérer et modifier son propre profil
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# Vue pour changer le mot de passe
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        
        if not user.check_password(old_password):
            return Response({"error": "Ancien mot de passe incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({"message": "Mot de passe modifié avec succès !"})