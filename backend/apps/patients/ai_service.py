"""
AI Service for Patient Analysis using Google Gemini
"""
import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai package not installed. AI features will be disabled.")


class PatientAIService:
    """Service for AI-powered patient analysis using Google Gemini"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = None
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured. AI features will be disabled.")
            return
            
        if not GEMINI_AVAILABLE:
            logger.warning("google-generativeai package not available. AI features will be disabled.")
            return
            
        try:
            genai.configure(api_key=self.api_key)
            # Using stable model version available in API
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.model is not None and self.api_key and GEMINI_AVAILABLE
    
    def generate_patient_analysis(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered analysis for a patient based on their medical data
        
        Args:
            patient_data: Dictionary containing patient information
            
        Returns:
            Dictionary with analysis results or error information
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'AI сервис недоступен. Проверьте настройку GEMINI_API_KEY.',
                'analysis': None
            }
        
        try:
            # Build comprehensive prompt from patient data
            prompt = self._build_analysis_prompt(patient_data)
            
            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'error': None,
                'analysis': response.text,
                'model': 'gemini-2.5-flash'
            }
            
        except Exception as e:
            logger.error(f"Error generating patient analysis: {e}")
            return {
                'success': False,
                'error': f'Ошибка при генерации анализа: {str(e)}',
                'analysis': None
            }
    
    def _build_analysis_prompt(self, patient_data: Dict[str, Any]) -> str:
        """Build a comprehensive prompt for patient analysis"""
        
        # Basic patient info
        full_name = patient_data.get('full_name', 'Пациент')
        age = patient_data.get('age', 'неизвестно')
        sex = patient_data.get('sex_display', 'неизвестно')
        
        prompt_parts = [
            f"Вы медицинский AI-ассистент. Проанализируйте медицинские данные пациента и предоставьте профессиональное заключение.",
            f"\n**ДАННЫЕ ПАЦИЕНТА:**",
            f"\nИмя: {full_name}",
            f"Возраст: {age} лет",
            f"Пол: {sex}",
        ]
        
        # Medical history
        medical_history = patient_data.get('medical_history', '')
        if medical_history:
            prompt_parts.append(f"\n**Анамнез:** {medical_history}")
        
        # Allergies
        allergies = patient_data.get('allergies', '')
        if allergies:
            prompt_parts.append(f"\n**Аллергии:** {allergies}")
        
        # Chronic diseases
        diseases = patient_data.get('diseases', [])
        if diseases:
            diseases_list = [f"- {d.get('name', 'Неизвестно')}: {d.get('notes', '')}" for d in diseases]
            prompt_parts.append(f"\n**Хронические заболевания:**\n" + "\n".join(diseases_list))
        
        # Diagnoses
        diagnoses = patient_data.get('diagnoses', [])
        if diagnoses:
            diagnoses_list = [
                f"- {d.get('diagnosis_text', 'Неизвестно')} (код: {d.get('icd_code', 'N/A')})"
                for d in diagnoses
            ]
            prompt_parts.append(f"\n**Диагнозы:**\n" + "\n".join(diagnoses_list))
        
        # Blood type and additional info
        blood_type = patient_data.get('blood_type', '')
        rh_factor = patient_data.get('rh_factor', '')
        if blood_type:
            prompt_parts.append(f"\n**Группа крови:** {blood_type} {rh_factor}")
        
        # Disability info
        disability_group = patient_data.get('disability_group', '')
        if disability_group:
            prompt_parts.append(f"\n**Группа инвалидности:** {disability_group}")
            disability_notes = patient_data.get('disability_notes', '')
            if disability_notes:
                prompt_parts.append(f"Примечания: {disability_notes}")
        
        # Notes
        notes = patient_data.get('notes', '')
        if notes:
            prompt_parts.append(f"\n**Дополнительные заметки:** {notes}")
        
        # Add instructions for the AI
        prompt_parts.extend([
            f"\n\n**ЗАДАЧА:**",
            f"На основе предоставленных данных, пожалуйста, составьте:",
            f"1. **Общее состояние пациента** - краткая оценка текущего состояния здоровья",
            f"2. **Факторы риска** - выявленные или потенциальные риски для здоровья",
            f"3. **Рекомендации** - медицинские рекомендации и предложения по дальнейшему обследованию",
            f"4. **Взаимодействие заболеваний** - если есть несколько заболеваний, укажите возможные взаимодействия",
            f"\nПожалуйста, предоставьте профессиональное, структурированное заключение на русском языке.",
            f"ВАЖНО: Это вспомогательный инструмент для врача. Все рекомендации должны быть согласованы с лечащим врачом."
        ])
        
        return "\n".join(prompt_parts)
    
    def generate_diagnosis_suggestion(self, symptoms: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate diagnosis suggestions based on symptoms and patient context
        
        Args:
            symptoms: Description of symptoms
            patient_context: Additional patient information
            
        Returns:
            Dictionary with suggestions or error information
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'AI сервис недоступен. Проверьте настройку GEMINI_API_KEY.',
                'suggestions': None
            }
        
        try:
            age = patient_context.get('age', 'неизвестно')
            sex = patient_context.get('sex_display', 'неизвестно')
            
            prompt = f"""Вы медицинский AI-ассистент. На основе следующей информации предложите возможные диагнозы:

Возраст пациента: {age} лет
Пол: {sex}
Симптомы: {symptoms}

Предоставьте:
1. Список возможных диагнозов (3-5 наиболее вероятных)
2. Краткое обоснование для каждого
3. Рекомендации по дополнительным обследованиям

ВАЖНО: Это вспомогательный инструмент. Окончательный диагноз ставит врач."""
            
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'error': None,
                'suggestions': response.text,
                'model': 'gemini-2.5-flash'
            }
            
        except Exception as e:
            logger.error(f"Error generating diagnosis suggestions: {e}")
            return {
                'success': False,
                'error': f'Ошибка при генерации предложений: {str(e)}',
                'suggestions': None
            }


# Singleton instance
_ai_service_instance = None


def get_ai_service() -> PatientAIService:
    """Get singleton instance of AI service"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = PatientAIService()
    return _ai_service_instance

