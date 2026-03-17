from django.core import signing
from django.conf import settings
from django.http import HttpResponse, Http404
from .models import Paciente
import os
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
                        logger.info(
                            "[MIDDLEWARE] ✓ Sessão restaurada via uid_signed para paciente %s",
                            paciente_id
                        )
                    else:
                        logger.warning(
                            "[MIDDLEWARE] Paciente %s não existe no banco de dados",
                            paciente_id
                        )
                except signing.BadSignature as e:
                    logger.warning(
                        "[MIDDLEWARE] ✗ BadSignature error ao decodificar uid_signed. "
                        "Provável causa: SECRET_KEY foi alterada entre requisições. "
                        "Certifique-se de que SECRET_KEY está configurada como variável de ambiente em produção. "
                        "Cookie: %s | Erro: %s",
                        signed[:20] + "..." if len(signed) > 20 else signed,
                        str(e)
                    )
                except Exception as e:
                    logger.error(
                        "[MIDDLEWARE] Erro ao restaurar sessão via uid_signed: %s",
                        str(e),
                        exc_info=True
                    )
        
        response = self.get_response(request)
        return response


class MediaServeMiddleware:
    """
    Middleware para servir arquivos de mídia em produção (Railway).
    O WhiteNoise não serve mídia por padrão, então fazemos isso manualmente.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar se é uma requisição para /media/
        if request.path.startswith('/media/'):
            # Remover /media/ do path para obter o caminho relativo
            file_path = request.path[7:]  # Remove '/media/' (7 caracteres)

            # Caminho completo no sistema de arquivos
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # Verificar se o arquivo existe
            if os.path.exists(full_path) and os.path.isfile(full_path):
                try:
                    # Abrir e servir o arquivo
                    with open(full_path, 'rb') as f:
                        content = f.read()

                    # Determinar content-type baseado na extensão
                    content_type = self._get_content_type(file_path)

                    response = HttpResponse(content, content_type=content_type)
                    response['Content-Length'] = len(content)
                    return response

                except Exception as e:
                    logger.error(f"Erro ao servir arquivo de mídia {file_path}: {e}")
                    raise Http404("Arquivo não encontrado")

            else:
                logger.warning(f"Arquivo de mídia não encontrado: {full_path}")
                raise Http404("Arquivo não encontrado")

        return self.get_response(request)

    def _get_content_type(self, file_path):
        """Determinar content-type baseado na extensão do arquivo"""
        ext = file_path.lower().split('.')[-1]

        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'svg': 'image/svg+xml',
            'avif': 'image/avif',
            'pdf': 'application/pdf',
        }

        return content_types.get(ext, 'application/octet-stream')

