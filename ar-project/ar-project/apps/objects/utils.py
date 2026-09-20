from django.http import JsonResponse
from django.db.models import F

from .models import ARTextObjectTemplate, ARTextObject, TextObjectInteraction



def fetch_text_object_template(request, template):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    template_obj = ARTextObjectTemplate.objects.filter(id=template, is_active=True).values(
        'shape', 'width', 'height', 'depth', 'radius', 'radius_top', 'radius_bottom',
        'model_url', 'rotation_x', 'rotation_y', 'rotation_z', 'billboard',
        'material_opacity', 'material_transparent', 'material_metalness', 'material_roughness',
        'texture_url', 'texture_repeat_x', 'texture_repeat_y', 'cast_shadow', 'receive_shadow',
    ).first()

    if template_obj:
        return JsonResponse(template_obj)
    return JsonResponse({'error': 'Template not found'}, status=404)


def like_object(request, object_id, object_type):

    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if object_type == 'text':
        try:
            like, created = TextObjectInteraction.objects.get_or_create(
            user=user,
            text_object_id=object_id,
            liked=True
            )
            if not created:
                like.delete()
                return JsonResponse({'status': 'unliked'})
            else:
                return JsonResponse({'status': 'liked'})
        except ARTextObject.DoesNotExist:
            return JsonResponse({'error': 'Object not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid object type'}, status=400)


def unlike_object(request, object_id, object_type):

    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if object_type == 'text':
        try:
            like = TextObjectInteraction.objects.get(
                user=user,
                content_type__model=object_type,
                object_id=object_id,
                liked=True
            )
            like.delete()
            return JsonResponse({'status': 'unliked'})
        except TextObjectInteraction.DoesNotExist:
            return JsonResponse({'error': 'Like not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid object type'}, status=400)


def hide_object(request, object_id, object_type):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if object_type == 'text':
        try:
            object = ARTextObject.objects.get(id=object_id)
            interaction, created = TextObjectInteraction.objects.get_or_create(
                user=user,
                text_object=object

            )
            interaction.hidden = True
            interaction.save()
            return JsonResponse({'status': 'hidden'})
        except ARTextObject.DoesNotExist:
            return JsonResponse({'error': 'Object not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid object type'}, status=400)


def unhide_object(request, object_id, object_type):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if object_type == 'text':
        try:
            interaction = TextObjectInteraction.objects.get(
                user=user,
                content_type__model=object_type,
                object_id=object_id
            )
            interaction.hidden = False
            interaction.save()
            return JsonResponse({'status': 'unhidden'})
        except TextObjectInteraction.DoesNotExist:
            return JsonResponse({'error': 'Interaction not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid object type'}, status=400)

