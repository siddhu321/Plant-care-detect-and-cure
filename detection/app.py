from flask import Flask, request, render_template
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import base64
from io import BytesIO
import timm

app = Flask(__name__)

# Define class names
class_names = {
    0: "Apple___Apple_scab",
    1: "Apple___Black_rot",
    2: "Apple___Cedar_apple_rust",
    3: "Apple___healthy",
    4: "Blueberry___healthy",
    5: "Cherry_(including_sour)___Powdery_mildew",
    6: "Cherry_(including_sour)___healthy",
    7: "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    8: "Corn_(maize)___Common_rust",
    9: "Corn_(maize)___Northern_Leaf_Blight",
    10: "Corn_(maize)___healthy",
    11: "Grape___Black_rot",
    12: "Grape___Esca_(Black_Measles)",
    13: "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    14: "Grape___healthy",
    15: "Orange___Haunglongbing_(Citrus_greening)",
    16: "Peach___Bacterial_spot",
    17: "Peach___healthy",
    18: "Pepper,_bell___Bacterial_spot",
    19: "Pepper,_bell___healthy",
    20: "Potato___Early_blight",
    21: "Potato___Late_blight",
    22: "Potato___healthy",
    23: "Raspberry___healthy",
    24: "Soybean___healthy",
    25: "Squash___Powdery_mildew",
    26: "Strawberry___Leaf_scorch",
    27: "Strawberry___healthy",
    28: "Tomato___Bacterial_spot",
    29: "Tomato___Early_blight",
    30: "Tomato___Late_blight",
    31: "Tomato___Leaf_Mold",
    32: "Tomato___Septoria_leaf_spot",
    33: "Tomato___Spider_mites Two-spotted_spider_mite",
    34: "Tomato___Target_Spot",
    35: "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    36: "Tomato___Tomato_mosaic_virus",
    37: "Tomato___healthy"
}

# Load model
model_name = 'vgg19'
model = timm.create_model(model_name, pretrained=True)

# Freeze layers
freeze_layers = 30
for i, param in enumerate(model.parameters()):
    if i < freeze_layers:
        param.requires_grad = False

model.load_state_dict(torch.load('best_model_epoch_5.pt', map_location=torch.device('cpu'), weights_only=True))
model.eval()

# Define image transformations
test_transform = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Function to process image and make predictions
# Function to process image and make predictions
def process_image(image):
    input_image = test_transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(input_image)

    predicted_class = torch.argmax(output, dim=1).item()
    confidence = F.softmax(output, dim=1)[0][predicted_class].item()
    predicted_class_name = class_names[predicted_class]
    cure_info = get_cure_info(predicted_class_name)

    return predicted_class_name, confidence, cure_info, image


# Function to encode image as base64
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    encoded_img = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return encoded_img

# Function to get cure information for predicted class
def get_cure_info(predicted_class_name):
    # Define cure information
    cure_info = {
        "Apple___Apple_scab": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur. Spread a 3- to 6-inch layer of compost under trees, keeping it away from the trunk, to cover soil and prevent splash dispersal of the fungal spores. For best control, spray liquid copper soap early, two weeks before symptoms normally appear.",
        "Apple___Black_rot": "Keep all the fallen debris and dead fruit cleaned up and away from the tree. During the winter, check for red cankers and remove them by cutting them out or pruning away the affected limbs at least six inches (15 cm.) beyond the wound. General-purpose fungicides, like copper-based sprays and lime sulfur can be used to control black rot.",
        "Apple___Cedar_apple_rust": "Remove galls from infected junipers. (In some cases, juniper plants should be removed entirely). Apply preventative, disease-fighting fungicides labeled for use on apples weekly, starting with bud break, to protect trees from spores being released by the juniper host. On juniper, rust can be controlled by spraying plants with a copper solution (0.5 to 2.0 oz/ gallon of water) at least four times between late August and late October.",
        "Apple___healthy": "Maintain proper pruning and sanitation.",
        "Blueberry___healthy": "Maintain proper irrigation and soil pH.",
        "Cherry_(including_sour)___Powdery_mildew": "Maintain a consistent program from shuck fall through harvest. Consider post-harvest preventative measures (e.g. application of sulfur, prevent trees from pushing for leaf growth) to obstruct the fungus from overwintering. Keep the disease off of the leaves.",
        "Cherry_(including_sour)___healthy": "Maintain proper pruning and sanitation.",
        "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Crop rotation and tillage reduce survival of the fungus. Use Resistant hybrids and inbreds. By removing weeds, above ground airflow to the crop is increased, relative humidity is decreased, and it limits infection at the most susceptible times.",
        "Corn_(maize)___Common_rust": "Maize rusts are generally controlled by the use of resistant maize hybrids, and by foliar applications of fungicides on sweet corn. The use of resistant varieties is the best way of managing rust diseases, two types of resistance exist: partial resistant and qualitative resistance. Protectant fungicide e.g., chlorothalonil and mancozeb are recommended",
        "Corn_(maize)___Northern_Leaf_Blight": "Scouting fields and monitoring local conditions is vital to control this disease. Reduce the amount of infected residue left in a field, manage weeds to improve airflow and reduce humidity. The use of foliar fungicides for corn can be used to control NCLB",
        "Corn_(maize)___healthy": "Implement crop rotation and maintain soil fertility.",
        "Grape___Black_rot": "Apply sanitation methods to optimally grow grape crops. The most common fungicides that prove to be excellent for controlling black rot are Sovran 50WG, Flint 50WG, Abound Flowable (2.08F), and Pristine 38WDG. Spray copper once a week.",
        "Grape___Esca_(Black_Measles)": "Protect pruning wounds from fungal infections to minimize suspect fungi from colonizing fresh wounds. Keep all the fallen debris and dead fruit cleaned up and away from the tree. Spray copper once a week.",
        "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Spray copper once a week. Keep all the fallen debris and dead fruit cleaned up and away from the tree. Rotate crops when possible.",
        "Grape___healthy": "Monitor vineyard health and management practices.",
        "Orange___Haunglongbing_(Citrus_greening)": "Once a tree has citrus greening, there is no cure. It is incredibly important to remove trees that have citrus greening disease. Keep all the fallen debris and dead fruit cleaned up and away from the tree.",
        "Peach___Bacterial_spot": "Use Oxytetracycline as it is generally considered the most effective compound and the least prone to phytotoxicity problems (damage to plant tissue). Syllit+captan can be used to control it. Repeated applications are typically necessary for even minimal disease control.",
        "Peach___healthy": "Maintain proper pruning and irrigation.",
        "Pepper,_bell___Bacterial_spot": "Apply copper-based fungicides, rotate crops.",
        "Pepper,_bell___healthy": "Practice good cultural practices.",
        "Potato___Early_blight": "Apply chlorothalonil or mancozeb fungicides.",
        "Potato___Late_blight": "Apply chlorothalonil or mancozeb fungicides, rotate crops.",
        "Potato___healthy": "Practice good field hygiene, use disease-free seed potatoes.",
        "Raspberry___healthy": "Maintain pruning and irrigation practices.",
        "Soybean___healthy": "Practice crop rotation, choose resistant varieties.",
        "Squash___Powdery_mildew": "Apply sulfur or potassium bicarbonate fungicides, space plants properly.",
        "Strawberry___Leaf_scorch": "Apply copper hydroxide or sulfur fungicides, maintain air circulation.",
        "Strawberry___healthy": "Practice sanitation and weed control.",
        "Tomato___Bacterial_spot": "Apply copper-based fungicides, rotate crops.",
        "Tomato___Early_blight": "Apply chlorothalonil or mancozeb fungicides, ensure good drainage.",
        "Tomato___Late_blight": "Apply chlorothalonil or mancozeb fungicides, practice sanitation.",
        "Tomato___Leaf_Mold": "Apply chlorothalonil or mancozeb fungicides, ensure ventilation.",
        "Tomato___Septoria_leaf_spot": "Apply chlorothalonil or mancozeb fungicides, rotate crops.",
        "Tomato___Spider_mites Two-spotted_spider_mite": "Apply insecticidal soaps or oils, control weeds.",
        "Tomato___Target_Spot": "Apply chlorothalonil or mancozeb fungicides, improve air circulation.",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Control whiteflies with insecticides, use resistant varieties.",
        "Tomato___Tomato_mosaic_virus": "No cure; control aphids, remove infected plants.",
        "Tomato___healthy": "Maintain proper cultural practices."
    }

    return cure_info.get(predicted_class_name, "No cure information available.")



# Define Flask routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', message='No file part')

        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', message='No selected file')

        if file:
            image = Image.open(file).convert('RGB')
            predicted_class, confidence, cure_info, original_image = process_image(image)
            encoded_image = encode_image(original_image)

            return render_template('index.html', predicted_class=predicted_class, confidence=confidence, cure_info=cure_info, encoded_image=encoded_image)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
