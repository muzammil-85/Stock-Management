from rest_framework import serializers
import base64
from django.core.files.base import ContentFile
from api.models import Product, SubVariant, Variant

class SubVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubVariant
        fields = ['name']

class VariantSerializer(serializers.ModelSerializer):
    subvariants = SubVariantSerializer(many=True)

    class Meta:
        model = Variant
        fields = ['name', 'subvariants']

class ProductSerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'ProductID', 'ProductCode', 'ProductName', 'ProductImage', 'IsFavourite', 'Active', 'HSNCode', 'TotalStock', 'variants']

    def create(self, validated_data):
        variants_data = validated_data.pop('variants')
        request = self.context.get('request')
        validated_data['CreatedUser'] = request.user
        product = Product.objects.create(**validated_data)
        for variant_data in variants_data:
            print(validated_data)
            subvariants_data = variant_data.pop('subvariants')
            variant = Variant.objects.create(product=product, **variant_data)
            for subvariant_data in subvariants_data:
                SubVariant.objects.create(variant=variant, **subvariant_data)
        return product
