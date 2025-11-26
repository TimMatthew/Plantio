import matplotlib.pyplot as plt
import torch
import torchvision.transforms as transforms
import torchvision.transforms.functional as F
from PIL import Image

CLASSIFY_TRANSFORM = transforms.Compose(
    [transforms.ToTensor(), transforms.Resize((224, 224))]
)


def classify_image(img_path, m, class_names, d):
    transform = CLASSIFY_TRANSFORM

    image = Image.open(img_path).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(d)

    transformed_image = F.to_pil_image(tensor.squeeze(0).cpu().clamp(0, 1))
    plt.imshow(transformed_image)
    plt.axis("off")
    plt.title("Transformed image (224x224)")
    plt.show()

    with torch.no_grad():
        output = m(tensor)
        logits = output[0]
        probs = torch.softmax(logits, dim=0)

        for idx, prob in enumerate(probs):
            disease = class_names[idx]
            print(f"prob {idx} ({disease}) = {prob.item():.4f}")

        _, predicted = torch.max(output, 1)

    predicted_class = class_names[predicted.item()]
    plt.imshow(image)
    plt.axis("off")
    plt.title(f"Predicted class: {predicted_class}")
    plt.show()

    return predicted_class


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)

    class_list = """
    0 - apple black rot
    1 - apple cedar rust
    2 - apple healthy
    3 - apple scab
    4 - cherry (sour) healthy
    5 - cherry (sour) powdery mildew
    6 - corn common rust
    7 - corn healthy
    8 - corn leaf blight
    9 - cucumber  Bacterial Wilt
    10 - cucumber  Belly Rot
    11 - cucumber Downy Mildew
    12 - cucumber Fresh Cucumber
    13 - cucumber Fresh Leaf
    14 - cucumber Gummy Stem Blight
    15 - cucumber Pythium Fruit Rot
    16 - grape black rot
    17 - grape esca (black measles)
    18 - grape healthy
    19 - grape leaf blight
    20 - healthy sunflower
    21 - healthy wheat
    22 - pepper bell bacterial spot
    23 - pepper bell healthy
    24 - potato early blight
    25 - potato healthy
    26 - potato late blight
    27 - powdery mildew wheat
    28 - raspberry healthy
    29 - rhizopus sunflower
    30 - rust wheat
    31 - septoria wheat
    32 - smuts wheat
    33 - soybean healthy
    34 - squash powdery mildew
    35 - strawberry healthy
    36 - strawberry leaf scorch
    37 - tomato bacterial spot
    38 - tomato healthy
    39 - tomato late blight
    40 - tomato leaf mold
    41 - tomato mosaic virus
    42 - tomato septoria leaf spot
    43 - tomato spider mites
    44 - tomato target spot
    45 - tomato verticulium wilt
    46 - tomato yellow leaf curl virus
    """

    class_dict = {}
    for line in class_list.strip().split("\n"):
        idx, name = line.split(" - ", 1)
        class_dict[int(idx)] = name

    model = torch.load(
        "app/models/plantio/model.pth", map_location=device, weights_only=False
    )
    print(model)
    model.eval()

    classify_image(
        r"D:\University\4_year\1_trimestr\ППС\plantio\storage\samples\grape_black_rot_1.jpg",
        model,
        class_dict,
        device,
    )
