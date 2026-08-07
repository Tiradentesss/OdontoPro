import logging

from django.core.files.storage import default_storage
from django.db.models import ImageField
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _get_image_fields(instance):
    """Return only ImageField descriptors for the concrete model."""
    fields = []
    for field in instance._meta.get_fields():
        if isinstance(field, ImageField):
            fields.append(field)
    return fields


@receiver(post_delete)
def cleanup_cloudinary_image_on_delete(sender, instance=None, **kwargs):
    """Remove any ImageField file already published through the Cloudinary storage backend."""
    if instance is None:
        return

    for field in _get_image_fields(instance):
        image_name = getattr(instance, field.name, None)
        if image_name:
            try:
                file_name = getattr(image_name, 'name', None) or str(image_name)
                if file_name:
                    default_storage.delete(file_name)
                    logger.info('Cloudinary cleanup: %s', file_name)
            except Exception as exc:
                logger.warning('Falha ao remover imagem do storage no delete de %s.%s: %s', sender.__name__, field.name, exc)


@receiver(pre_save)
def cache_previous_image_field_values(sender, instance=None, **kwargs):
    """Store original ImageField names before a model is saved, so replacements can be cleaned later."""
    if instance is None or not getattr(instance, 'pk', None):
        return

    try:
        old_instance = sender._default_manager.get(pk=instance.pk)
    except Exception:
        return

    old_values = {}
    for field in _get_image_fields(instance):
        old_value = getattr(old_instance, field.name, None)
        old_name = getattr(old_value, 'name', None) if old_value else None
        if old_name:
            old_values[field.name] = old_name

    instance._old_image_field_values = old_values


@receiver(post_save)
def cleanup_replaced_cloudinary_images(sender, instance=None, **kwargs):
    """Delete files that used to be stored on the Cloudinary backend when a new image replaces them."""
    if instance is None:
        return

    old_values = getattr(instance, '_old_image_field_values', {})
    if not old_values:
        return

    for field in _get_image_fields(instance):
        current_name = getattr(instance, field.name, None)
        current_name = getattr(current_name, 'name', None) if current_name else None
        previous_name = old_values.get(field.name)

        if previous_name and previous_name != current_name:
            try:
                default_storage.delete(previous_name)
                logger.info('Cloudinary cleanup (replace): %s', previous_name)
            except Exception as exc:
                logger.warning('Falha ao remover imagem antiga de %s.%s: %s', sender.__name__, field.name, exc)
