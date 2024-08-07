from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Product, Variant, SubVariant
from .serializers import ProductSerializer
from django.db.models import F
import logging

logger = logging.getLogger(__name__)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('CreatedUser').prefetch_related('variants__subvariants')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        try:
            product = self.get_object()
            variant_name = request.data.get('variant')
            subvariant_name = request.data.get('subvariant')
            quantity = request.data.get('quantity', 0)

            variant = Variant.objects.get(product=product, name=variant_name)
            subvariant = SubVariant.objects.get(variant=variant, name=subvariant_name)
            subvariant.stock = F('stock') + quantity
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
            quantity = request.data.get('quantity', 0)

            variant = Variant.objects.get(product=product, name=variant_name)
            subvariant = SubVariant.objects.get(variant=variant, name=subvariant_name)
            if subvariant.stock >= quantity:
                subvariant.stock = F('stock') - quantity
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
