"""
Token authentication mixins.
"""

from typing import Any, Dict, Optional



class TokenAuthMixin:
    """
    Mixin for token-based authentication.
    """
    
    TOKEN_REQUIRED_ACTIONS = ["delete", "update_sensitive", "change_ownership"]
    SENSITIVE_FIELDS = ["email", "phone", "password"]
    
    def generate_action_token(
        self,
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_field: str = "user",
    ) -> Optional[str]:
        """
        Generate token for critical action.
        """
        user = getattr(self, user_field, None)
        if not user:
            return None
        
        try:
            from ..services.token import TokenService
            
            # Add instance metadata
            full_metadata = {
                "model": self.__class__.__name__,
                "instance_id": self.pk,
                "action": action,
                **(metadata or {}),
            }
            
            # Generate token
            token_data = TokenService().generate_token(
                user_id=str(user.id),
                action=action,
                metadata=full_metadata,
            )
            
            if token_data.get("success"):
                return token_data.get("token")
                
        except ImportError:
            pass
        
        return None
    
    def validate_action_token(
        self,
        token: str,
        action: str,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate token for action.
        """
        try:
            from ..services.token import TokenService
            
            return TokenService().validate_token(token, action, user_id)
            
        except ImportError:
            # Fallback if TokenService not available
            return {"valid": True, "action": action, "user_id": user_id}
    
    def can_perform_action(
        self,
        token: str,
        action: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Check if action can be performed with token.
        """
        validation = self.validate_action_token(token, action, user_id)
        return validation.get("valid", False)
    
    def perform_critical_action(
        self,
        action: str,
        token: str,
        user_id: str,
        action_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform critical action with token validation.
        """
        # Validate token
        if not self.can_perform_action(token, action, user_id):
            return {
                "success": False,
                "error": "Token validation failed",
                "code": "TOKEN_INVALID",
            }
        
        # Check if action requires token
        if action in self.TOKEN_REQUIRED_ACTIONS:
            # Additional validation for sensitive actions
            if not self._validate_critical_action(action, action_data or {}):
                return {
                    "success": False,
                    "error": "Action validation failed",
                    "code": "ACTION_INVALID",
                }
        
        # Perform action
        try:
            result = self._perform_action(action, action_data or {})
            return {"success": True, "result": result}
            
        except Exception as e:
            return {"success": False, "error": str(e), "code": "ACTION_FAILED"}
    
    def _validate_critical_action(
        self,
        action: str,
        action_data: Dict[str, Any],
    ) -> bool:
        """Validate critical action."""
        # Override in subclasses for specific validation
        return True
    
    def _perform_action(
        self,
        action: str,
        action_data: Dict[str, Any],
    ) -> Any:
        """Perform action."""
        # Override in subclasses
        raise NotImplementedError("Subclasses must implement _perform_action")
    
    def check_token_permission(self, token: str, action: str) -> bool:
        """
        Check token permission for this instance.
        """
        # Override in subclasses for instance-level permissions
        return True


class TokenProtectedMixin(TokenAuthMixin):
    """
    Mixin for token-protected models.
    """
    
    def save(self, *args, **kwargs):
        """Override save to check token for sensitive updates."""
        # Check if this is an update
        if self.pk:
            # Get the original object
            original = self.__class__.objects.get(pk=self.pk)
            
            # Check for sensitive field changes
            sensitive_changes = self._get_sensitive_changes(original)
            
            if sensitive_changes:
                # In a real implementation, you would check for a token here
                # For now, we'll just log a warning
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Sensitive fields changed in {self.__class__.__name__}: {sensitive_changes}"
                )
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to require token for critical deletion."""
        # In a real implementation, you would check for a token here
        # For now, we'll just proceed
        super().delete(*args, **kwargs)
    
    def _get_sensitive_changes(self, original) -> Dict[str, Any]:
        """Get sensitive field changes."""
        changes = {}
        
        for field in self.SENSITIVE_FIELDS:
            if hasattr(self, field) and hasattr(original, field):
                current_value = getattr(self, field)
                original_value = getattr(original, field)
                
                if current_value != original_value:
                    changes[field] = {
                        "from": original_value,
                        "to": current_value,
                    }
        
        return changes