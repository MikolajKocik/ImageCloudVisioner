from src.services.image_process_service import analyze_image, recognize_image

def main():
    image = input()
    result = analyze_image(image)
    print(result)
    recognize_image(image)

    return image

if __name__ == "__main__":
    main()