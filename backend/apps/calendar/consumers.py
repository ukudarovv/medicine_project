import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class CalendarConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time calendar updates
    """
    
    async def connect(self):
        """
        Handle WebSocket connection
        """
        # Get branch_id from query string
        self.branch_id = self.scope['url_route']['kwargs'].get('branch_id')
        self.user = self.scope['user']
        
        # Check authentication
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Check branch access
        has_access = await self.check_branch_access()
        if not has_access:
            await self.close()
            return
        
        # Join branch-specific group
        self.group_name = f'calendar_branch_{self.branch_id}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnect
        """
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages (optional, for client-initiated actions)
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            # Handle different message types
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
        except json.JSONDecodeError:
            pass
    
    async def appointment_event(self, event):
        """
        Send appointment event to WebSocket
        """
        await self.send(text_data=json.dumps(event['data']))
    
    @database_sync_to_async
    def check_branch_access(self):
        """
        Check if user has access to the branch
        """
        from apps.core.models import UserBranchAccess
        
        # Owner has access to all branches
        if self.user.role == 'owner':
            return True
        
        # Check branch access
        return UserBranchAccess.objects.filter(
            user=self.user,
            branch_id=self.branch_id
        ).exists()

