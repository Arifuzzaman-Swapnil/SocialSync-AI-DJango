from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_image.models import ImageGeneration, AssetPlatformVariant
from brands.models import BrandTemplate
from accounts.api_keys import get_openai_key
from ai_image.services.alt_text_service import generate_alt_text
from ai_image.services.resize_service import resize_image_for_platforms
from ai_image.services.template_service import apply_brand_template


class GenerateAltTextView(APIView):
    """Generate accessibility alt text for an image using LLM vision"""
    permission_classes = [IsAuthenticated]

    def post(self, request, asset_id):
        try:
            asset = ImageGeneration.objects.get(id=asset_id, user=request.user)
        except ImageGeneration.DoesNotExist:
            return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)

        api_key = get_openai_key(request.user)
        alt_text = generate_alt_text(asset, api_key)

        return Response({
            'asset_id': asset.id,
            'alt_text': alt_text,
        })


class ResizeAssetView(APIView):
    """Resize an image for platform-specific dimensions"""
    permission_classes = [IsAuthenticated]

    def post(self, request, asset_id):
        try:
            asset = ImageGeneration.objects.get(id=asset_id, user=request.user)
        except ImageGeneration.DoesNotExist:
            return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)

        platforms = request.data.get('platforms')
        variants = resize_image_for_platforms(asset, platforms=platforms)

        return Response({
            'asset_id': asset.id,
            'variants_created': len(variants),
            'variants': [
                {
                    'id': v.id,
                    'platform': v.platform,
                    'format_label': v.format_label,
                    'dimensions': v.dimensions,
                    'file_url': v.file_url.url if v.file_url else None,
                }
                for v in variants
            ],
        }, status=status.HTTP_201_CREATED)


class ApplyTemplateView(APIView):
    """Apply a brand template overlay to an image"""
    permission_classes = [IsAuthenticated]

    def post(self, request, asset_id):
        try:
            asset = ImageGeneration.objects.get(id=asset_id, user=request.user)
        except ImageGeneration.DoesNotExist:
            return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)

        template_id = request.data.get('template_id')
        if not template_id:
            return Response({'error': 'template_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            template = BrandTemplate.objects.get(id=template_id)
        except BrandTemplate.DoesNotExist:
            return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)

        result = apply_brand_template(asset, template)
        if result is None:
            return Response(
                {'error': 'Failed to apply template'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({
            'asset_id': result.id,
            'message': 'Brand template applied successfully',
        })


class AssetVersionsView(APIView):
    """Get version history for an asset"""
    permission_classes = [IsAuthenticated]

    def get(self, request, asset_id):
        try:
            asset = ImageGeneration.objects.get(id=asset_id, user=request.user)
        except ImageGeneration.DoesNotExist:
            return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)

        from ai_image.models import CreativeVersionHistory
        versions = CreativeVersionHistory.objects.filter(asset=asset).order_by('-created_at')

        return Response([
            {
                'id': v.id,
                'version': v.version,
                'file_url': v.file_url,
                'generation_params': v.generation_params,
                'created_at': v.created_at.isoformat(),
            }
            for v in versions
        ])
