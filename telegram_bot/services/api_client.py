"""
Django API Client
"""
import aiohttp
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DjangoAPIClient:
    """
    Async client for Django API
    """
    
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request to API"""
        url = f"{self.base_url}/api/bot/{endpoint.lstrip('/')}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=self.headers, **kwargs
            ) as response:
                if response.status >= 400:
                    text = await response.text()
                    logger.error(f"API Error {response.status}: {text}")
                    raise Exception(f"API Error: {response.status}")
                
                return await response.json()
    
    # ==================== Patient Management ====================
    
    async def upsert_patient(self, data: Dict) -> Dict:
        """Create or update patient"""
        return await self._request('POST', 'patient/upsert/', json=data)
    
    async def verify_iin(self, iin: str) -> Dict:
        """Verify IIN"""
        return await self._request('POST', 'patient/verify-iin/', json={'iin': iin})
    
    async def get_patient_by_telegram(self, telegram_user_id: int) -> Dict:
        """Get patient by telegram user ID"""
        return await self._request('GET', f'patient/by-telegram/{telegram_user_id}/')
    
    # ==================== Booking ====================
    
    async def get_branches(self, organization_id: Optional[int] = None) -> List[Dict]:
        """Get list of branches"""
        params = {}
        if organization_id:
            params['organization_id'] = organization_id
        
        result = await self._request('GET', 'branches/', params=params)
        return result if isinstance(result, list) else result.get('results', [])
    
    async def get_services(self, branch_id: Optional[int] = None) -> List[Dict]:
        """Get list of services"""
        params = {}
        if branch_id:
            params['branch_id'] = branch_id
        
        result = await self._request('GET', 'services/', params=params)
        return result if isinstance(result, list) else result.get('results', [])
    
    async def get_doctors(self, service_id: Optional[int] = None, date: Optional[str] = None) -> List[Dict]:
        """Get list of doctors"""
        params = {}
        if service_id:
            params['service_id'] = service_id
        if date:
            params['date'] = date
        
        result = await self._request('GET', 'doctors/', params=params)
        return result if isinstance(result, list) else result.get('results', [])
    
    async def get_slots(self, doctor_id: int, date: str) -> List[Dict]:
        """Get available time slots"""
        params = {'doctor_id': doctor_id, 'date': date}
        result = await self._request('GET', 'slots/', params=params)
        return result.get('slots', [])
    
    async def create_appointment(self, data: Dict) -> Dict:
        """Create appointment"""
        return await self._request('POST', 'appointments/', json=data)
    
    async def get_my_appointments(self, telegram_user_id: int) -> List[Dict]:
        """Get my appointments"""
        params = {'telegram_user_id': telegram_user_id}
        result = await self._request('GET', 'appointments/my/', params=params)
        return result if isinstance(result, list) else result.get('results', [])
    
    async def update_appointment(self, appointment_id: int, data: Dict) -> Dict:
        """Update appointment"""
        return await self._request('PATCH', f'appointments/{appointment_id}/', json=data)
    
    async def cancel_appointment(self, appointment_id: int) -> Dict:
        """Cancel appointment"""
        return await self._request('POST', f'appointments/{appointment_id}/cancel/')
    
    # ==================== Documents ====================
    
    async def get_documents(self, telegram_user_id: int, doc_type: Optional[str] = None) -> List[Dict]:
        """Get patient documents"""
        params = {'telegram_user_id': telegram_user_id}
        if doc_type:
            params['type'] = doc_type
        
        result = await self._request('GET', 'documents/', params=params)
        return result if isinstance(result, list) else result.get('results', [])
    
    async def generate_document(self, telegram_user_id: int, document_type: str, language: str = 'ru', **kwargs) -> Dict:
        """Generate document"""
        data = {
            'telegram_user_id': telegram_user_id,
            'document_type': document_type,
            'language': language,
            **kwargs
        }
        return await self._request('POST', 'documents/generate/', json=data)
    
    async def get_document_download(self, document_id: str) -> Dict:
        """Get document download URL"""
        return await self._request('GET', f'documents/{document_id}/download/')
    
    # ==================== Payments ====================
    
    async def create_invoice(self, telegram_user_id: int, amount: float, description: str = '') -> Dict:
        """Create payment invoice"""
        data = {
            'telegram_user_id': telegram_user_id,
            'amount': amount,
            'description': description
        }
        return await self._request('POST', 'payments/invoice/', json=data)
    
    async def get_payment_status(self, invoice_id: str) -> Dict:
        """Get payment status"""
        return await self._request('GET', f'payments/{invoice_id}/status/')
    
    async def get_patient_balance(self, telegram_user_id: int) -> Dict:
        """Get patient balance"""
        params = {'telegram_user_id': telegram_user_id}
        return await self._request('GET', 'payments/balance/', params=params)
    
    # ==================== Feedback ====================
    
    async def create_feedback(self, telegram_user_id: int, appointment_id: int, score: int, comment: str = '') -> Dict:
        """Create NPS feedback"""
        data = {
            'telegram_user_id': telegram_user_id,
            'appointment_id': appointment_id,
            'score': score,
            'comment': comment
        }
        return await self._request('POST', 'feedback/', json=data)
    
    # ==================== Support ====================
    
    async def create_support_ticket(self, telegram_user_id: int, subject: str, message: str) -> Dict:
        """Create support ticket"""
        data = {
            'telegram_user_id': telegram_user_id,
            'subject': subject,
            'message': message
        }
        return await self._request('POST', 'support/ticket/', json=data)
    
    async def get_faq(self) -> List[Dict]:
        """Get FAQ list"""
        result = await self._request('GET', 'support/faq/')
        return result.get('faqs', [])
    
    # ==================== Consent Management ====================
    
    async def verify_consent_otp(self, access_request_id: str, otp_code: str) -> Dict:
        """
        Verify OTP code for consent request
        
        Args:
            access_request_id: UUID of access request
            otp_code: 6-digit OTP code
            
        Returns:
            Dict with success status and grant info
        """
        try:
            url = f"{self.base_url}/api/v1/consent/otp/verify/"
            
            # Use bot secret for authentication
            headers = {
                'X-Bot-Secret': self.headers['Authorization'].replace('Bearer ', ''),
                'Content-Type': 'application/json'
            }
            
            data = {
                'access_request_id': access_request_id,
                'otp_code': otp_code
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 201:
                        grant = await response.json()
                        return {
                            'success': True,
                            'grant': grant
                        }
                    else:
                        error_data = await response.json()
                        return {
                            'success': False,
                            'error': error_data.get('error', 'Ошибка верификации OTP')
                        }
        except Exception as e:
            logger.error(f"Failed to verify consent OTP: {e}")
            return {
                'success': False,
                'error': 'Ошибка связи с сервером'
            }
    
    async def deny_access_request(self, access_request_id: str) -> Dict:
        """
        Deny access request
        
        Args:
            access_request_id: UUID of access request
            
        Returns:
            Dict with success status
        """
        try:
            result = await self._request(
                'POST',
                f'consent/access-requests/{access_request_id}/deny/'
            )
            return {
                'success': True,
                'org_name': result.get('org_name', '')
            }
        except Exception as e:
            logger.error(f"Failed to deny access request: {e}")
            return {'success': False}
    
    async def get_access_request_details(self, access_request_id: str) -> Dict:
        """
        Get details of access request
        
        Args:
            access_request_id: UUID of access request
            
        Returns:
            Dict with success status and request details
        """
        try:
            result = await self._request(
                'GET',
                f'consent/access-requests/{access_request_id}/'
            )
            return {
                'success': True,
                'request': result
            }
        except Exception as e:
            logger.error(f"Failed to get access request details: {e}")
            return {'success': False}
    
    async def get_my_access_grants(self, telegram_user_id: int) -> Dict:
        """
        Get patient's active access grants
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            Dict with success status and grants list
        """
        try:
            result = await self._request(
                'GET',
                f'consent/patient-grants/{telegram_user_id}/'
            )
            return {
                'success': True,
                'grants': result if isinstance(result, list) else result.get('results', [])
            }
        except Exception as e:
            logger.error(f"Failed to get access grants: {e}")
            return {
                'success': False,
                'grants': []
            }
    
    async def revoke_access_grant(self, grant_id: str) -> Dict:
        """
        Revoke access grant
        
        Args:
            grant_id: UUID of access grant
            
        Returns:
            Dict with success status
        """
        try:
            result = await self._request(
                'POST',
                f'consent/grants/{grant_id}/revoke/'
            )
            return {
                'success': True,
                'org_name': result.get('org_name', '')
            }
        except Exception as e:
            logger.error(f"Failed to revoke access grant: {e}")
            return {'success': False}
    
    async def get_access_grant_details(self, grant_id: str) -> Dict:
        """
        Get details of access grant
        
        Args:
            grant_id: UUID of access grant
            
        Returns:
            Dict with success status and grant details
        """
        try:
            result = await self._request(
                'GET',
                f'consent/grants/{grant_id}/'
            )
            return {
                'success': True,
                'grant': result
            }
        except Exception as e:
            logger.error(f"Failed to get access grant details: {e}")
            return {'success': False}

