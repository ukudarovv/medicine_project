from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet,
    RepresentativeViewSet,
    PatientFileViewSet,
    PatientPhoneViewSet,
    PatientSocialNetworkViewSet,
    PatientContactPersonViewSet,
    PatientDiseaseViewSet,
    PatientDiagnosisViewSet,
)

# Import Sprint 2-5 ViewSets only after migrations are applied
# Uncomment these imports after running: python manage.py migrate
# from .views import (
#     ConsentHistoryViewSet,
#     MedicalExaminationViewSet,
#     MedExamPastDiseaseViewSet,
#     MedExamVaccinationViewSet,
#     MedExamLabTestViewSet,
#     TreatmentPlanViewSet,
#     TreatmentStageViewSet,
#     TreatmentStageItemViewSet,
#     TreatmentPlanTemplateViewSet
# )

router = DefaultRouter()
router.register('patients', PatientViewSet, basename='patient')
router.register('representatives', RepresentativeViewSet, basename='representative')
router.register('files', PatientFileViewSet, basename='patient-file')
router.register('phones', PatientPhoneViewSet, basename='patient-phone')
router.register('social-networks', PatientSocialNetworkViewSet, basename='patient-social')
router.register('contact-persons', PatientContactPersonViewSet, basename='patient-contact')
router.register('diseases', PatientDiseaseViewSet, basename='patient-disease')
router.register('diagnoses', PatientDiagnosisViewSet, basename='patient-diagnosis')

# ====================================================================
# UNCOMMENT AFTER APPLYING MIGRATIONS (python manage.py migrate)
# ====================================================================
# # Sprint 1: Consent History
# router.register('consent-history', ConsentHistoryViewSet, basename='consent-history')
# 
# # Sprint 3: Medical Examinations
# router.register('examinations', MedicalExaminationViewSet, basename='medical-examination')
# router.register('exam-past-diseases', MedExamPastDiseaseViewSet, basename='exam-past-disease')
# router.register('exam-vaccinations', MedExamVaccinationViewSet, basename='exam-vaccination')
# router.register('exam-lab-tests', MedExamLabTestViewSet, basename='exam-lab-test')
# 
# # Sprint 3: Treatment Plans
# router.register('treatment-plans', TreatmentPlanViewSet, basename='treatment-plan')
# router.register('treatment-stages', TreatmentStageViewSet, basename='treatment-stage')
# router.register('treatment-stage-items', TreatmentStageItemViewSet, basename='treatment-stage-item')
# router.register('treatment-plan-templates', TreatmentPlanTemplateViewSet, basename='treatment-plan-template')
# ====================================================================

urlpatterns = [
    path('', include(router.urls)),
]
