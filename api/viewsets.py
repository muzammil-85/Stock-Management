from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Product, Variant, SubVariant
from .serializers import ProductSerializer
from django.db.models import F
import logging
from rest_framework.decorators import api_view
from django.contrib.auth import logout
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('CreatedUser').prefetch_related('variants__subvariants')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # to ensure the user is authenticated

    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        try:
            product = self.get_object()
            variant_name = request.data.get('variant')
            subvariant_name = request.data.get('subvariant')
            quantity = request.data.get('quantity', 0)

            variant = Variant.objects.get(product=product, name=variant_name)
            subvariant = SubVariant.objects.get(variant=variant, name=subvariant_name)
            subvariant.save()
            product.TotalStock = F('TotalStock') + quantity
            product.save()
            return Response({'status': 'stock added'}, status=status.HTTP_200_OK)
        except Variant.DoesNotExist:
            return Response({'error': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)
        except SubVariant.DoesNotExist:
            return Response({'error': 'SubVariant not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error adding stock: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def remove_stock(self, request, pk=None):
        try:
            product = self.get_object()
            variant_name = request.data.get('variant')
            subvariant_name = request.data.get('subvariant')
            quantity = int(request.data.get('quantity', 0))
            variant = Variant.objects.get(product=product, name=variant_name)
            subvariant = SubVariant.objects.get(variant=variant, name=subvariant_name)
            if product.TotalStock >= quantity:
                subvariant.save()
                product.TotalStock = F('TotalStock') - quantity
                product.save()
                return Response({'status': 'stock removed'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        except Variant.DoesNotExist:
            return Response({'error': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)
        except SubVariant.DoesNotExist:
            return Response({'error': 'SubVariant not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error removing stock: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(('POST',))
def ProductImageUpload(request, product_id, *args, **kwargs):
    if request.method == "POST":
        try:
            print(product_id)
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the request contains an image
        if 'ProductImage' not in request.FILES:
            return Response({"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)

        product_image = request.FILES['ProductImage']
        print(product_image)

        # Update the product's image
        product.ProductImage = product_image
        product.save()

        return Response({"message": "Image uploaded successfully."}, status=status.HTTP_200_OK)


def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Successfully logged out.'})