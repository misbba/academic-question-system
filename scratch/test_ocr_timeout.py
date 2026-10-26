import concurrent.futures

def try_ocr():
    try:
        import winocr
        from PIL import Image
        img = Image.new('RGB', (200, 50), color=(255, 255, 255))
        # Call with timeout
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(winocr.recognize_pil_sync, img)
            res = future.result(timeout=3)
            return True, res
    except Exception as e:
        return False, str(e)

ok, res = try_ocr()
print("OCR test:", ok, res)
