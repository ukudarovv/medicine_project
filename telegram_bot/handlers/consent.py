"""
Consent management handlers for Telegram bot
Handles OTP verification and access grant management
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from services.api_client import DjangoAPIClient
from config import config

router = Router()
api_client = DjangoAPIClient(config.DJANGO_API_URL, config.DJANGO_API_SECRET)


@router.callback_query(F.data.startswith('consent_approve:'))
async def consent_approve(callback: CallbackQuery, t: callable, telegram_user: any):
    """
    Handle consent approval from patient
    """
    try:
        # Parse callback data
        parts = callback.data.split(':')
        if len(parts) < 3:
            await callback.answer(t('error_general'), show_alert=True)
            return
        
        access_request_id = parts[1]
        otp_code = parts[2]
        
        # Verify OTP via backend API
        result = await api_client.verify_consent_otp(
            access_request_id=access_request_id,
            otp_code=otp_code
        )
        
        if result.get('success'):
            grant = result.get('grant', {})
            org_name = grant.get('grantee_org_name', 'организация')
            valid_to = grant.get('valid_to', '')
            
            await callback.message.edit_text(
                f"✅ <b>Доступ предоставлен</b>\n\n"
                f"Организация <b>{org_name}</b> получила доступ к вашей медицинской карте.\n\n"
                f"<b>Доступ действителен до:</b> {valid_to[:10]}\n\n"
                f"Вы можете отозвать доступ в любой момент через /my_access",
                parse_mode='HTML'
            )
            await callback.answer('✅ Доступ предоставлен')
        else:
            error_msg = result.get('error', 'Ошибка при предоставлении доступа')
            await callback.answer(error_msg, show_alert=True)
            
    except Exception as e:
        await callback.answer(t('error_general'), show_alert=True)


@router.callback_query(F.data.startswith('consent_deny:'))
async def consent_deny(callback: CallbackQuery, t: callable):
    """
    Handle consent denial from patient
    """
    try:
        # Parse callback data
        parts = callback.data.split(':')
        if len(parts) < 2:
            await callback.answer(t('error_general'), show_alert=True)
            return
        
        access_request_id = parts[1]
        
        # Deny access request via backend API
        result = await api_client.deny_access_request(access_request_id)
        
        if result.get('success'):
            org_name = result.get('org_name', 'организация')
            
            await callback.message.edit_text(
                f"❌ <b>Доступ отклонён</b>\n\n"
                f"Вы отклонили запрос доступа от организации <b>{org_name}</b>.",
                parse_mode='HTML'
            )
            await callback.answer('❌ Доступ отклонён')
        else:
            await callback.answer(t('error_general'), show_alert=True)
            
    except Exception as e:
        await callback.answer(t('error_general'), show_alert=True)


@router.callback_query(F.data.startswith('consent_details:'))
async def consent_details(callback: CallbackQuery, t: callable):
    """
    Show detailed information about consent request
    """
    try:
        # Parse callback data
        parts = callback.data.split(':')
        if len(parts) < 2:
            await callback.answer(t('error_general'), show_alert=True)
            return
        
        access_request_id = parts[1]
        
        # Get request details from backend API
        result = await api_client.get_access_request_details(access_request_id)
        
        if result.get('success'):
            request_data = result.get('request', {})
            
            # Format scopes
            scope_names = {
                'read_summary': 'Чтение краткой информации',
                'read_records': 'Чтение медицинских записей',
                'write_records': 'Создание медицинских записей',
                'read_images': 'Просмотр изображений и файлов'
            }
            scopes = request_data.get('scopes', [])
            scopes_text = '\n'.join([f'• {scope_names.get(s, s)}' for s in scopes])
            
            message = (
                f"ℹ️ <b>Подробная информация о запросе</b>\n\n"
                f"<b>Организация:</b> {request_data.get('requester_org_name', '-')}\n"
                f"<b>Врач:</b> {request_data.get('requester_user_name', '-')}\n"
                f"<b>Причина:</b> {request_data.get('reason', '-')}\n"
                f"<b>Срок доступа:</b> {request_data.get('requested_duration_days', 30)} дней\n\n"
                f"<b>Запрашиваемые права:</b>\n{scopes_text}\n\n"
                f"<b>Что это значит?</b>\n"
                f"Врач сможет просматривать ваши медицинские записи "
                f"для оказания медицинской помощи. Вы можете отозвать доступ в любой момент."
            )
            
            await callback.message.edit_text(message, parse_mode='HTML')
            await callback.answer()
        else:
            await callback.answer(t('error_general'), show_alert=True)
            
    except Exception as e:
        await callback.answer(t('error_general'), show_alert=True)


@router.message(Command('my_access'))
async def cmd_my_access(message: Message, t: callable, telegram_user: any):
    """
    Show patient's active access grants
    """
    try:
        # Get patient's access grants from backend API
        result = await api_client.get_my_access_grants(telegram_user.id)
        
        if not result.get('success'):
            await message.answer(t('error_general'))
            return
        
        grants = result.get('grants', [])
        
        if not grants:
            await message.answer(
                "У вас нет активных предоставленных доступов.\n\n"
                "Когда вы предоставите доступ к своей медицинской карте, "
                "здесь появится список организаций с доступом."
            )
            return
        
        # Format grants list
        grants_text = []
        for grant in grants:
            org_name = grant.get('grantee_org_name', 'Неизвестно')
            valid_to = grant.get('valid_to', '')[:10]
            is_active = grant.get('is_active', False)
            
            status_icon = '🟢' if is_active else '🔴'
            grants_text.append(f"{status_icon} <b>{org_name}</b>\n   До: {valid_to}")
        
        message_text = (
            "🔐 <b>Ваши активные доступы</b>\n\n"
            + '\n\n'.join(grants_text) +
            "\n\n"
            "Используйте кнопки ниже для управления доступами."
        )
        
        # Create inline keyboard for grant management
        from keyboards.inline import get_access_grants_keyboard
        keyboard = get_access_grants_keyboard(grants)
        
        await message.answer(message_text, parse_mode='HTML', reply_markup=keyboard)
        
    except Exception as e:
        await message.answer(t('error_general'))


@router.callback_query(F.data.startswith('grant_revoke:'))
async def grant_revoke(callback: CallbackQuery, t: callable):
    """
    Revoke an access grant
    """
    try:
        # Parse callback data
        parts = callback.data.split(':')
        if len(parts) < 2:
            await callback.answer(t('error_general'), show_alert=True)
            return
        
        grant_id = parts[1]
        
        # Revoke grant via backend API
        result = await api_client.revoke_access_grant(grant_id)
        
        if result.get('success'):
            org_name = result.get('org_name', 'организация')
            
            await callback.message.edit_text(
                f"✅ <b>Доступ отозван</b>\n\n"
                f"Доступ организации <b>{org_name}</b> к вашей медицинской карте отозван.",
                parse_mode='HTML'
            )
            await callback.answer('✅ Доступ отозван')
        else:
            await callback.answer(t('error_general'), show_alert=True)
            
    except Exception as e:
        await callback.answer(t('error_general'), show_alert=True)


@router.callback_query(F.data.startswith('grant_details:'))
async def grant_details(callback: CallbackQuery, t: callable):
    """
    Show detailed information about an access grant
    """
    try:
        # Parse callback data
        parts = callback.data.split(':')
        if len(parts) < 2:
            await callback.answer(t('error_general'), show_alert=True)
            return
        
        grant_id = parts[1]
        
        # Get grant details from backend API
        result = await api_client.get_access_grant_details(grant_id)
        
        if result.get('success'):
            grant = result.get('grant', {})
            
            # Format scopes
            scope_names = {
                'read_summary': 'Чтение краткой информации',
                'read_records': 'Чтение медицинских записей',
                'write_records': 'Создание медицинских записей',
                'read_images': 'Просмотр изображений и файлов'
            }
            scopes = grant.get('scopes', [])
            scopes_text = '\n'.join([f'• {scope_names.get(s, s)}' for s in scopes])
            
            last_accessed = grant.get('last_accessed_at', None)
            last_accessed_text = last_accessed[:10] if last_accessed else 'Не использовался'
            
            message = (
                f"🔐 <b>Информация о доступе</b>\n\n"
                f"<b>Организация:</b> {grant.get('grantee_org_name', '-')}\n"
                f"<b>Предоставлен:</b> {grant.get('created_at', '')[:10]}\n"
                f"<b>Действителен до:</b> {grant.get('valid_to', '')[:10]}\n"
                f"<b>Последнее использование:</b> {last_accessed_text}\n"
                f"<b>Количество обращений:</b> {grant.get('access_count', 0)}\n\n"
                f"<b>Предоставленные права:</b>\n{scopes_text}"
            )
            
            # Add revoke button
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='❌ Отозвать доступ', callback_data=f'grant_revoke:{grant_id}')],
                [InlineKeyboardButton(text='« Назад', callback_data='my_access_list')]
            ])
            
            await callback.message.edit_text(message, parse_mode='HTML', reply_markup=keyboard)
            await callback.answer()
        else:
            await callback.answer(t('error_general'), show_alert=True)
            
    except Exception as e:
        await callback.answer(t('error_general'), show_alert=True)


@router.callback_query(F.data == 'my_access_list')
async def my_access_list(callback: CallbackQuery, t: callable, telegram_user: any):
    """
    Show list of access grants (back from details)
    """
    # Reuse cmd_my_access logic
    await cmd_my_access(callback.message, t, telegram_user)
    await callback.answer()

