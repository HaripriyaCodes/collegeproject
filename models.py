from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Member(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)


class ImageUpload(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='uploads/')

class CropInfo(models.Model):
    crop = models.CharField(max_length=255,unique=True)

class Disease(models.Model):
    name = models.CharField(max_length=100,unique=True)
    type = models.CharField(max_length=100)
    crop_name = models.ForeignKey(CropInfo, related_name='crop_name', on_delete=models.CASCADE)
    description = models.TextField()
    symptoms = models.TextField()  # Symptoms of the disease or pest
    recommendations_organic = models.TextField()  # Recommendations for treatment
    recommendations_chemical = models.TextField()
    cause = models.TextField()  # Cause of the disease or pest
    preventive_measures = models.TextField()  # Preventive measures for the disease or pest
    image = models.ImageField(upload_to='uploads/disease/')

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()

class ProductCategory(models.Model):
    name = models.CharField(max_length=255,unique=True)

class ProductInfo(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField()
    quantity = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='uploads/product/')
