from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserBranchAccess
import qrcode
import io
import base64


class OrganizationMinimalSerializer(serializers.Serializer):
    """
    Minimal organization serializer for user response
    """
    id = serializers.IntegerField()
    name = serializers.CharField()
    sms_sender = serializers.CharField(allow_blank=True, allow_null=True)
    logo = serializers.SerializerMethodField()
    
    def get_logo(self, obj):
        """Return logo URL if exists"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer
    """
    organization = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    is_superuser = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'phone',
            'is_2fa_enabled',
            'is_superuser',
            'organization'
        ]
        read_only_fields = ['id', 'is_superuser']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    
    def get_organization(self, obj):
        """Serialize organization using OrganizationMinimalSerializer"""
        if obj.organization:
            return OrganizationMinimalSerializer(obj.organization, context=self.context).data
        return None


class LoginSerializer(serializers.Serializer):
    """
    Login serializer
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    totp_token = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        totp_token = attrs.get('totp_token')
        
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')
        
        # Check 2FA if enabled
        if user.is_2fa_enabled:
            if not totp_token:
                raise serializers.ValidationError('2FA token required')
            
            if not user.verify_totp(totp_token):
                raise serializers.ValidationError('Invalid 2FA token')
        
        attrs['user'] = user
        return attrs
    
    def create(self, validated_data):
        user = validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        # Get user's branches
        branches = UserBranchAccess.objects.filter(user=user).select_related('branch')
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user, context=self.context).data,
            'branches': [
                {
                    'id': access.branch.id,
                    'name': access.branch.name,
                    'is_default': access.is_default
                }
                for access in branches
            ]
        }


class RefreshTokenSerializer(serializers.Serializer):
    """
    Refresh token serializer
    """
    refresh = serializers.CharField()
    
    def validate(self, attrs):
        refresh_token = attrs.get('refresh')
        
        try:
            refresh = RefreshToken(refresh_token)
            attrs['access'] = str(refresh.access_token)
        except Exception as e:
            raise serializers.ValidationError('Invalid refresh token')
        
        return attrs


class Enable2FASerializer(serializers.Serializer):
    """
    Enable 2FA serializer
    """
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Generate TOTP secret
        secret = user.generate_totp_secret()
        uri = user.get_totp_uri()
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            'secret': secret,
            'qr_code': f'data:image/png;base64,{qr_code_base64}',
            'uri': uri
        }


class Verify2FASerializer(serializers.Serializer):
    """
    Verify 2FA token and enable it
    """
    token = serializers.CharField(max_length=6, min_length=6)
    
    def validate(self, attrs):
        user = self.context['request'].user
        token = attrs.get('token')
        
        if not user.totp_secret:
            raise serializers.ValidationError('2FA not initiated')
        
        if not user.verify_totp(token):
            raise serializers.ValidationError('Invalid token')
        
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        user.is_2fa_enabled = True
        user.save(update_fields=['is_2fa_enabled'])
        
        return {'message': '2FA enabled successfully'}


class Disable2FASerializer(serializers.Serializer):
    """
    Disable 2FA
    """
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        user = self.context['request'].user
        password = attrs.get('password')
        
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid password')
        
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        user.is_2fa_enabled = False
        user.totp_secret = ''
        user.save(update_fields=['is_2fa_enabled', 'totp_secret'])
        
        return {'message': '2FA disabled successfully'}

