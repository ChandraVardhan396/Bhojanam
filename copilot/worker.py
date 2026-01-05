from PySide6.QtCore import QObject, Signal, Slot

class FoodLabelWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, reader, client, image_path):
        super().__init__()
        self.reader = reader
        self.client = client
        self.image_path = image_path

    @Slot()
    def run(self):
        try:
            # OCR
            ocr_result = self.reader.readtext(self.image_path, detail=0)
            extracted_text = "\n".join(ocr_result)

            if not extracted_text.strip():
                self.finished.emit(
                    "Please provide a valid ingredients or nutrition label image."
                )
                return

            # Food label check
            keywords = [
                "ingredients", "nutrition", "energy", "fat",
                "protein", "carbohydrate", "sugar", "salt",
                "serving", "per 100", "calories"
            ]
            matches = sum(1 for k in keywords if k in extracted_text.lower())
            if matches < 2:
                self.finished.emit(
                    "Please provide a valid ingredients or nutrition label image."
                )
                return

            # LLM
            prompt = build_prompt(extracted_text)
            completion = self.client.chat.completions.create(
                model="moonshotai/Kimi-K2-Instruct:novita",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.45,
                timeout=30
            )

            self.finished.emit(
                completion.choices[0].message.content.strip()
            )

        except Exception as e:
            self.error.emit("Something went wrong. Please try again.")
