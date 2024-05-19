# WEBP2PNG Converter

This project provides a simple GUI application to convert images from WEBP format to PNG format. The application allows users to paste an image from the clipboard, convert it to PNG, and copy the converted image back to the clipboard.

## Features

- Paste an image from the clipboard
- Convert the image to PNG format
- Copy the converted PNG image to the clipboard
- Always on top window option

## Usage

1. **Install the required libraries**:
    ```bash
    pip install pillow pywin32
    ```

2. **Run the script**:
    ```bash
    python WEBP2PNG-0011.py
    ```

3. **Copy an image** from your browser or any other source to your clipboard.

4. **Paste the image** into the application by pressing `Ctrl + V`.

5. **Click the "Convert to PNG" button**. The image will be saved to the `./CONVERTED` directory with a timestamped name and displayed in the window.

6. **Click the "Copy to Clipboard" button** to copy the converted PNG image to the clipboard.

7. **Toggle the "Always on Top"** feature from the "Options" menu to keep the window on top of other windows. The checkbutton will indicate whether this feature is enabled. It is enabled by default on startup.

## License

This project is licensed under the MIT License.
