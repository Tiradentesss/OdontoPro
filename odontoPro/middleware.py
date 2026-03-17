from django.core import signing
from django.utils.decorators import sync_and_async_middleware
from .models import Paciente
import logging

logger = logging.getLogger(__name__)


class RestoreSessionMiddleware:
    """
    Middleware que automaticamente restaura a sessão do paciente usando
    o cookie uid_signed se a sessão estiver vazia.
    
    Isso resolve problemas em ambientes com múltiplos workers onde
    a sessão pode não estar sincronizada.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Se não há paciente_id na sessão, tentar restaurar via uid_signed
        paciente_id = request.session.get('paciente_id')
        
        if not paciente_id:
            signed = request.COOKIES.get('uid_signed')
            if signed:
                try:
                    paciente_id = signing.loads(signed)
                    if Paciente.objects.filter(id=paciente_id).exists():
                        request.session['paciente_id'] = paciente_id
                        # Salva explicitamente a sessão
                        request.session.save()
                        logger.info("[MIDDLEWARE] Sessão restaurada via uid_signed para paciente %s", paciente_id)
                except signing.BadSignature:
                    logger.warning("[MIDDLEWARE] uid_signed inválido: %r", signed)
                except Exception as e:
                    logger.error("[MIDDLEWARE] Erro ao restaurar sessão: %s", str(e), exc_info=True)
        
        response = self.get_response(request)
        return response
