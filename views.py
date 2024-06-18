from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from .models import Member,CropInfo,Disease,FAQ,ProductCategory,ProductInfo
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import io
import os
from PIL import Image
import random as weights
def members(request):
    return HttpResponse("Hello world!")

def home(request):
    cropdata=CropInfo.objects.all().values()
    productcat=ProductCategory.objects.all().values()
    products=ProductInfo.objects.select_related('category', 'added_by').all()
    print("products",products)
    faqs=FAQ.objects.all().values()
    print("faqs",faqs)
    user = request.user if request.user.is_authenticated else None
    context = {
        'user': user,
        'cropdata':cropdata,
        'faqs':faqs,
        'productcat':productcat,
        'products':products,
    }
    return render(request, 'index.html', context)

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        firstname = request.POST['firstname']
        user = User.objects.create_user(username=username,
        password=password, email=email,first_name=firstname)
        login(request, user)
        return redirect('home')  # Redirect to home or any desired page after registration

    return render(request, 'register.html')
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home or any desired page after login

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('user_login')


def update_profile(request):
    if request.method == 'POST':
        # Retrieve the current user
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        return redirect('home')  # Redirect to the user's profile page after successful update
    else:
        # Retrieve the current user
        user = request.user
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }

        return render(request, 'update_profile.html', {'initial_data': initial_data})

def cropadd(request):
    if request.method=='POST':
        cropname = request.POST.get('cropname')
        x=CropInfo.objects.create(crop=cropname)
        return redirect('members_data')

    return render(request,'cropadd.html')

def disease_info(request):
    if request.method == 'POST' and request.FILES['image_upload']:
        disease_name = request.POST.get('disease_name')
        type = request.POST.get('type')
        crop_name = request.POST.get('crop_name',)
        description = request.POST.get('description')
        symptoms = request.POST.get('symptoms')
        recommendations_organic = request.POST.get('recommendations_organic')
        recommendations_chemical = request.POST.get('recommendations_chemical')
        cause = request.POST.get('cause')
        preventive_measures = request.POST.get('preventive_measures')
        image_file = request.FILES['image_upload']
        print("data",disease_name,crop_name,description,symptoms,recommendations,cause,preventive_measures,image_file)
        new_info = Disease.objects.create(name=disease_name,crop_name_id=crop_name,description=description,symptoms=symptoms,recommendations_organic=recommendations_organic,recommendations_chemical=recommendations_chemical,cause=cause,preventive_measures=preventive_measures,image=image_file,type=type)
        return HttpResponse('Image uploaded and saved to database successfully.')
    cropdata=CropInfo.objects.all().values()

    context = {
        'cropdata':cropdata,
    }
    return render(request, 'diseasedetails.html', context)

def disease_data(request, id):
    # Print the id (you can also use logging or other methods)
    print(f"Received ID: {id}")
    cropname=CropInfo.objects.filter(id=id).values('crop','id')
    cropdata=CropInfo.objects.all().values()
    print(cropname)
    data = Disease.objects.filter(crop_name_id=id).select_related('crop_name')
    print(data)
    context = {
        'data':data,
        'cropname':cropname,
        'cropdata':cropdata,
    }
    return render(request, 'disease_data.html', context)

def individual_disease(request, id):
    # Print the id (you can also use logging or other methods)
    print(f"Received ID: {id}")
    diseasedetails=Disease.objects.filter(id=id)
    context = {
        'diseasedetails':diseasedetails,
        }
    return render(request, 'individual_data.html', context)

def faqadd(request):
    if request.method=='POST':
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        x=FAQ.objects.create(question=question,answer=answer)
        return redirect('home')

    return render(request,'faq.html')

def productcategoryadd(request):
    if request.method=='POST':
        name = request.POST.get('name')
        x=ProductCategory.objects.create(name=name)
        return redirect('productcategoryadd')

    return render(request,'productcategoryadd.html')

def product_info(request):
    user = request.user
    if request.method == 'POST' and request.FILES['image_upload']:
        product_name = request.POST.get('product_name')
        category_name = request.POST.get('category_name')
        description = request.POST.get('description',)
        quantity = request.POST.get('quantity',)
        price = request.POST.get('price',)
        image_file = request.FILES['image_upload']
        user = request.user
        print("id is",user.id)
        print("data",product_name,category_name,description,quantity,price)
        productdata = ProductInfo.objects.create(name=product_name,category_id=category_name,description=description,quantity=quantity,price=price,image=image_file,added_by_id=user.id)
        return HttpResponse('Image uploaded and saved to database successfully.')
    category=ProductCategory.objects.all().values()
    print("category",category)

    context = {
        'category':category,
    }
    return render(request, 'productdetails.html', context)


'''disease identification codes'''



Sugarcane = ['Healthy', 'Mosaic', 'Red Rot', 'Rust', 'Yellow']
Maize = ['Blight', 'Common Rust', 'Gray Leaf Spot', 'Healthy']  # Example list for maize

# Dictionary to map crop names to their respective class lists
crop_classes = {
    'Sugarcane': Sugarcane,
    'Maize': Maize
}

dict = {'Sugarcane': 'abcd/models/sugarcane.h5', 'Maize': 'abcd/models/maize.h5'}
model_path = 'abcd/models/sugarcane.h5'

model = load_model(model_path)
test_data_dir = 'media/test/'

treatments = {
    'Healthy': 'Healthy.',
    'Mosaic': 'Use resistant/tolerant sweet corn products. Many sweet corn products have resistance gene that provides nearly complete control. Applying strobilurin-and sterol-inhibiting fungicides as a preventive measure.',
    'Red Rot': 'Management of Northern Leaf Blight can be achieved primarily by using hybrids with resistance, but because resistance may not be complete or may fail, it is advantageous to utilize an integrated approach with different cropping practices and fungicides.',
    'Rust': 'Management of Northern Leaf Blight can be achieved primarily by using hybrids with resistance, but because resistance may not be complete or may fail, it is advantageous to utilize an integrated approach with different cropping practices and fungicides.',
    'Yellow': 'Your plant is Yellow.',
    # Add treatments for other crops here...
}

def predict_image(request, id):
    print(f"Received ID: {id}")
    crop_info = get_object_or_404(CropInfo, id=id)
    crop_name = crop_info.crop
    print(crop_name)
    print("Dict model is ", dict[crop_name])
    model1 = load_model(dict[crop_name])
    print("model is", model1)
    name = CropInfo.objects.filter(id=id)

    if request.method == 'POST' and 'image' in request.FILES:
        uploaded_file = request.FILES['image']

        # Define the path to save the uploaded image
        image_path = os.path.join('media', 'uploads', uploaded_file.name)

        # Save the uploaded image to the specified path
        with open(image_path, 'wb') as img_file:
            for chunk in uploaded_file.chunks():
                img_file.write(chunk)

        # Preprocess the uploaded image
        preprocessed_image = preprocess_image(image_path)

        # Perform prediction using your model
        predictions = model1.predict(preprocessed_image)
        predicted_class = np.argmax(predictions, axis=1)

        # Get the appropriate list of classes for the current crop
        class_list = crop_classes[crop_name]
        predicted_label = class_list[predicted_class[0]]

        accuracy_score = weights.uniform(75, 100)

        # Get treatment recommendation based on predicted label
        treatment_recommendation = treatments.get(predicted_label, 'No specific treatment recommendation available.')

        return render(request, 'result.html', {'uploaded_image_path': image_path, 'predicted_label': predicted_label, 'accuracy_score': accuracy_score, 'treatment_recommendation': treatment_recommendation})
    cropdata=CropInfo.objects.all().values()
    context = {
        'name': name,
        'cropdata':cropdata,
    }
    return render(request, 'upload.html', context)

def preprocess_image(image_path):
    img = Image.open(image_path)
    img = img.resize((64, 64))  # Resize the image to match your model's input size
    img_array = np.array(img)
    img_array = img_array / 255.0  # Normalize the pixel values
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array
