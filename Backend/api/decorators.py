from functools import wraps
from jose import jwt, JWTError
from django.conf import settings
from django.http import JsonResponse
from .models import User

def jwt_required(role=None):
    """
    Decorator for Django views to enforce JWT verification.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JsonResponse({"detail": "Not authenticated"}, status=401)
            
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                if payload.get("type") != "access":
                    return JsonResponse({"detail": "Wrong token type"}, status=401)
                
                user_id = payload.get("sub")
                if not user_id:
                    return JsonResponse({"detail": "User ID not found in token."}, status=401)
                
                try:
                    user = User.objects.get(id=int(user_id))
                except User.DoesNotExist:
                    return JsonResponse({"detail": "User not found."}, status=404)
                
                request.user = user
                
                if role and user.role != role:
                    return JsonResponse({"detail": f"Only {role}s can access this."}, status=403)
                
            except JWTError:
                return JsonResponse({"detail": "Token is invalid or expired. Please login again."}, status=401)
            except Exception as e:
                return JsonResponse({"detail": f"Authentication error: {str(e)}"}, status=401)
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
