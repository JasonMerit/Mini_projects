import pyautogui as pag
import pytesseract

def image_to_latex(image):
    # recognize math expressions
    text = image_to_string(image)
    # convert text to latex
    latex = text_to_latex(text)
    return latex

def image_to_string(image):
    # recognize math expressions
    text = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
    return text

def text_to_latex(text):
    # convert text to latex
    latex = text
    return latex

def main():
    image = pag.screenshot()
    # recognize math expressions
    text = image_to_string(image)
    print(text)
    
        
    

if __name__ == '__main__':
    main()

